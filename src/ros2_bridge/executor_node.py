"""
NeuroStride-VL: ROS2 执行器节点（运行在 Jetson Orin Nano）
============================================================
负责接收指挥官指令并控制机器人执行动作

ROS2 功能:
- 订阅速度命令和策略参数
- 执行强化学习策略（TensorRT加速）
- 控制电机（通过 ROS2 control 或直接串口）
- 发布机器人状态（IMU、关节状态等）

作者: NeuroStride-VL Team
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

import time
import threading
import numpy as np
from typing import Optional, Dict, Any
from dataclasses import dataclass
import torch

# ROS2 消息类型
from geometry_msgs.msg import Twist, PoseStamped
from std_msgs.msg import String, Float32MultiArray
from sensor_msgs.msg import Imu, JointState, Image
from neurostride_msgs.msg import (
    RobotState,
    LocomotionCommand,
    VLCommand,
    PolicyAction,
    MotorCommand
)

# RL 策略
import sys
sys.path.append('/home/jetson/neurostride-vl/src')
from agents.rl_agent import PPOAgent, SACAgent, TrainingConfig


@dataclass
class ExecutorConfig:
    """执行器配置"""
    node_name: str = "neurostride_executor"
    qos_depth: int = 10

    # 控制频率
    control_freq: float = 50.0  # Hz (与仿真环境一致)
    control_period: float = 0.02  # 50Hz

    # 策略模型
    model_path: str = "models/checkpoints/sac_final.zip"
    algo: str = "sac"
    device: str = "cuda"  # Jetson 使用 CUDA

    # 硬件接口
    use_ros2_control: bool = False  # 使用 ros2_control
    motor_port: str = "/dev/ttyUSB0"  # 串口（如果不是 ros2_control）
    motor_baudrate: int = 1000000

    # TensorRT 优化
    use_tensorrt: bool = True
    trt_engine_path: str = "models/trt/policy_fp16.engine"

    # 话题名称
    cmd_vel_topic: str = "/cmd_vel"
    robot_state_topic: str = "/robot_state"
    motor_cmd_topic: str = "/motor_commands"


class ExecutorNode(Node):
    """
    NeuroStride-VL 执行器节点

    运行在 Jetson Orin Nano 上，负责:
    1. 接收 Mac M2 Pro 发布的命令
    2. 运行 RL 策略（TensorRT加速）
    3. 将动作转换为电机指令
    4. 通过串口或 ros2_control 发送到物理机器人
    5. 发布传感器数据（IMU、关节状态）
    """

    def __init__(self, config: ExecutorConfig = None):
        super().__init__(config.node_name if config else "neurostride_executor")

        self.config = config or ExecutorConfig()

        # QoS 配置
        qos = QoSProfile(
            depth=self.config.qos_depth,
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
        )

        # RL 策略
        self.policy = None
        self.current_velocity_command = np.array([0.0, 0.0, 0.0])
        self.policy_lock = threading.Lock()

        # 加载策略模型
        self._load_policy()

        # 订阅器
        self.cmd_vel_sub = self.create_subscription(
            Twist,
            self.config.cmd_vel_topic,
            self._cmd_vel_callback,
            qos
        )
        self.vl_command_sub = self.create_subscription(
            VLCommand,
            "/neurostride/vl_command",
            self._vl_command_callback,
            qos
        )

        # 发布器
        self.state_pub = self.create_publisher(
            RobotState,
            self.config.robot_state_topic,
            qos
        )
        self.joint_state_pub = self.create_publisher(
            JointState,
            "/joint_states",
            qos
        )
        self.motor_cmd_pub = self.create_publisher(
            MotorCommand,
            self.config.motor_cmd_topic,
            qos
        )

        # 硬件接口
        self.motor_interface = None
        if not self.config.use_ros2_control:
            self._init_serial_interface()

        # 控制循环
        self.running = False
        self.control_thread = None

        # 统计
        self.control_count = 0
        self.start_time = time.time()

        self.get_logger().info("✅ 执行器节点已启动")
        self.get_logger().info(f"  策略: {self.config.algo.upper()}")
        self.get_logger().info(f"  模型: {self.config.model_path}")
        self.get_logger().info(f"  控制频率: {self.config.control_freq} Hz")

    def _load_policy(self):
        """加载 RL 策略模型"""
        try:
            # 创建配置
            train_config = TrainingConfig(
                algo=self.config.algo,
                device=self.config.device,
            )

            # 创建智能体
            if self.config.algo == "ppo":
                self.policy = PPOAgent(train_config)
            elif self.config.algo == "sac":
                self.policy = SACAgent(train_config)
            else:
                raise ValueError(f"不支持的算法: {self.config.algo}")

            # 加载模型
            self.policy.load(self.config.model_path)
            self.get_logger().info(f"✅ 策略模型已加载: {self.config.model_path}")

        except Exception as e:
            self.get_logger().error(f"策略模型加载失败: {e}")
            raise

    def _init_serial_interface(self):
        """初始化串口电机接口"""
        try:
            import serial
            self.serial_port = serial.Serial(
                port=self.config.motor_port,
                baudrate=self.config.motor_baudrate,
                timeout=0.1
            )
            self.get_logger().info(f"✅ 串口已连接: {self.config.motor_port}")
        except ImportError:
            self.get_logger().warning("pyserial 未安装，跳过串口初始化")
        except Exception as e:
            self.get_logger().warning(f"串口连接失败: {e}")

    def _cmd_vel_callback(self, msg: Twist):
        """速度命令回调"""
        with self.policy_lock:
            self.current_velocity_command = np.array([
                msg.linear.x,
                msg.linear.y,
                msg.angular.z
            ])
        self.get_logger().debug(
            f"收到速度命令: vx={msg.linear.x:.2f}, vyaw={msg.angular.z:.2f}"
        )

    def _vl_command_callback(self, msg: VLCommand):
        """VLM 指令回调"""
        self.get_logger().info(f"VLM 指令: {msg.command}")
        # 可以解析 VLCommand 并转换为速度命令
        # 目前主要使用 /cmd_vel 话题

    def start(self):
        """启动执行器"""
        self.running = True
        self.control_thread = threading.Thread(
            target=self._control_loop,
            daemon=True
        )
        self.control_thread.start()
        self.get_logger().info("🚀 执行器节点运行中...")

    def _control_loop(self):
        """主控制循环"""
        rate = self.create_rate(self.config.control_freq)

        while self.running and rclpy.ok():
            try:
                # 1. 获取机器人当前状态（从传感器）
                current_state = self._read_robot_state()

                # 2. 构建观测向量（与训练时一致）
                observation = self._build_observation(current_state)

                # 3. RL 策略推理（获取动作）
                with self.policy_lock:
                    target_velocity = self.current_velocity_command.copy()

                action = self._infer_policy(observation, target_velocity)

                # 4. 将动作转换为电机指令
                motor_command = self._action_to_motor_command(action)

                # 5. 发送指令到电机
                self._send_motor_command(motor_command)

                # 6. 发布机器人状态
                self._publish_robot_state(current_state, action)

                # 统计
                self.control_count += 1

                rate.sleep()

            except Exception as e:
                self.get_logger().error(f"控制循环错误: {e}")
                time.sleep(0.1)

    def _read_robot_state(self) -> Dict[str, Any]:
        """
        读取机器人当前状态
        实际实现需要根据硬件调整:
        - 通过 ros2_control 读取
        - 或通过串口读取 IMU 和编码器
        """
        # 这里返回模拟数据
        return {
            "joint_positions": np.zeros(23),  # 实际从传感器读取
            "joint_velocities": np.zeros(23),
            "imu": {
                "accel": [0.0, 0.0, 9.81],
                "gyro": [0.0, 0.0, 0.0],
            },
            "foot_contacts": [1.0, 1.0],
            "torso_height": 1.0,
            "torso_orientation": [1.0, 0.0, 0.0, 0.0],  # 四元数
        }

    def _build_observation(self, state: Dict) -> np.ndarray:
        """
        构建观测向量（必须与训练环境一致）

        [q_pos (23), q_vel (23), imu (6), foot_contact (2), target_vel (3)]
        """
        obs = []

        # 关节位置
        qpos = state["joint_positions"]
        qpos_norm = np.clip(qpos / np.pi, -1, 1)
        obs.append(qpos_norm)

        # 关节速度
        qvel = state["joint_velocities"]
        qvel_norm = np.clip(qvel / 10.0, -1, 1)
        obs.append(qvel_norm)

        # IMU
        imu_data = np.concatenate([
            state["imu"]["accel"],
            state["imu"]["gyro"]
        ])
        obs.append(imu_data)

        # 脚接触
        obs.append(np.array(state["foot_contacts"]))

        # 目标速度（来自命令）
        with self.policy_lock:
            target_vel = self.current_velocity_command.copy()
        obs.append(target_vel)

        observation = np.concatenate(obs).astype(np.float32)
        return observation.reshape(1, -1)  # 添加批次维度

    def _infer_policy(self, observation: np.ndarray, target_velocity: np.ndarray) -> np.ndarray:
        """
        策略推理

        Args:
            observation: 状态观测 (1, obs_dim)
            target_velocity: 目标速度

        Returns:
            action: 动作向量 (num_actions,)
        """
        if self.policy is None:
            return np.zeros(23)

        try:
            # 使用 Stable-Baselines3 的 predict
            action, _states = self.policy.predict(observation, deterministic=True)
            return action.flatten()

        except Exception as e:
            self.get_logger().error(f"策略推理失败: {e}")
            return np.zeros(23)

    def _action_to_motor_command(self, action: np.ndarray) -> MotorCommand:
        """
        将动作转换为电机指令

        Args:
            action: 标准化动作 [-1, 1]

        Returns:
            motor_command: 电机指令消息
        """
        # 反归一化到实际扭矩范围
        max_torque = 50.0  # N·m
        torques = action * max_torque

        # 创建电机指令消息
        cmd = MotorCommand()
        cmd.header.stamp = self.get_clock().now().to_msg()
        cmd.joint_names = [f"joint_{i}" for i in range(len(action))]
        cmd.effort = torques.tolist()
        cmd.mode = MotorCommand.MODE_TORQUE

        return cmd

    def _send_motor_command(self, command: MotorCommand):
        """发送电机指令"""
        # 方式1: 通过 ROS2 发布
        self.motor_cmd_pub.publish(command)

        # 方式2: 通过串口发送（如果使用自定义硬件）
        if hasattr(self, 'serial_port') and self.serial_port.is_open:
            self._send_via_serial(command)

    def _send_via_serial(self, command: MotorCommand):
        """通过串口发送指令（针对自定义硬件）"""
        try:
            # 将扭矩数组转换为二进制数据
            data = np.array(command.effort, dtype=np.float32)
            self.serial_port.write(data.tobytes())
        except Exception as e:
            self.get_logger().warning(f"串口发送失败: {e}")

    def _publish_robot_state(self, state: Dict, action: np.ndarray):
        """发布机器人状态"""
        # RobotState 消息
        robot_state = RobotState()
        robot_state.header.stamp = self.get_clock().now().to_msg()
        robot_state.torso_height = float(state["torso_height"])
        robot_state.torso_orientation = state["torso_orientation"]
        robot_state.foot_contact_left = float(state["foot_contacts"][0])
        robot_state.foot_contact_right = float(state["foot_contacts"][1])
        robot_state.velocity = self.current_velocity_command.tolist()
        robot_state.action = action.tolist()

        self.state_pub.publish(robot_state)

        # JointState 消息（用于 rviz 可视化）
        joint_state = JointState()
        joint_state.header.stamp = self.get_clock().now().to_msg()
        joint_state.name = [f"joint_{i}" for i in range(len(state["joint_positions"]))]
        joint_state.position = state["joint_positions"].tolist()
        joint_state.velocity = state["joint_velocities"].tolist()
        joint_state.effort = action.tolist()

        self.joint_state_pub.publish(joint_state)

    def stop(self):
        """停止节点"""
        self.running = False
        if self.control_thread:
            self.control_thread.join(timeout=2.0)

        # 发送零扭矩（停止电机）
        if hasattr(self, 'serial_port') and self.serial_port.is_open:
            zero_torques = np.zeros(23, dtype=np.float32)
            self.serial_port.write(zero_torques.tobytes())
            self.serial_port.close()

        if hasattr(self, 'policy'):
            del self.policy
            torch.cuda.empty_cache()

        self.get_logger().info("👋 执行器节点已停止")


def main(args=None):
    rclpy.init(args=args)

    config = ExecutorConfig()
    node = ExecutorNode(config)

    try:
        node.start()
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("收到中断信号")
    finally:
        node.stop()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
