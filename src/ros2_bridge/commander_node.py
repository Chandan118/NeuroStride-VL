"""
NeuroStride-VL: ROS2 指挥官节点（运行在 Mac M2 Pro）
======================================================
负责接收VLM指令并发送控制命令到执行器

ROS2 主题:
- /neurostride/command (geometry_msgs/Twist) - 速度指令
- /neurostride/policy (neurostride_msgs/Policy) - 策略参数
- /neurostride/scene (std_msgs/String) - 场景描述

作者: NeuroStride-VL Team
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

import json
import time
import threading
from typing import Optional, Dict, Any
from dataclasses import dataclass

# ROS2 消息类型
from geometry_msgs.msg import Twist, PoseStamped
from std_msgs.msg import String, Float32MultiArray
from sensor_msgs.msg import Imu, JointState
from neurostride_msgs.msg import (
    RobotState,
    LocomotionCommand,
    VLCommand,
    PolicyAction
)

# 导入 VLM 智能体
import sys
sys.path.append('/home/jetson/neurostride-vl/src')
from perception.qwen_vl_agent import QwenVLAgent, VLConfig


@dataclass
class CommanderConfig:
    """指挥官节点配置"""
    node_name: str = "neurostride_commander"
    qos_depth: int = 10
    qos_reliability: str = "reliable"  # "reliable" or "best_effort"

    # VLM 配置
    vlm_enabled: bool = True
    vlm_model_path: str = "Qwen/Qwen-VL-2B-Chat"

    # 摄像头
    camera_id: int = 0
    camera_fps: int = 15  # VLM 推理频率（降低以节省算力）

    # 控制频率
    command_freq: float = 10.0  # Hz

    # 话题名称
    cmd_vel_topic: str = "/cmd_vel"
    scene_topic: str = "/scene_description"
    robot_state_topic: str = "/robot_state"


class CommanderNode(Node):
    """
    NeuroStride-VL 指挥官节点

    运行在 Mac M2 Pro 上，负责:
    1. 启动摄像头捕获
    2. 运行 Qwen-VL 视觉语言模型
    3. 解析自然语言指令
    4. 生成速度命令并发布到 ROS2 网络
    5. 监控机器人状态
    """

    def __init__(self, config: CommanderConfig = None):
        super().__init__(config.node_name if config else "neurostride_commander")

        self.config = config or CommanderConfig()

        # QoS 配置
        qos_profile = QoSProfile(
            depth=self.config.qos_depth,
            reliability=ReliabilityPolicy.RELIABLE
            if self.config.qos_reliability == "reliable"
            else ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
        )

        # 初始化 VLM 智能体
        if self.config.vlm_enabled:
            vl_config = VLConfig(
                model_path=self.config.vlm_model_path,
                camera_id=self.config.camera_id,
                fps=self.config.camera_fps,
            )
            self.vl_agent = QwenVLAgent(vl_config)
            self.get_logger().info("VLM 智能体已创建")

        # 发布器
        self.cmd_vel_pub = self.create_publisher(
            Twist,
            self.config.cmd_vel_topic,
            qos_profile
        )
        self.scene_pub = self.create_publisher(
            String,
            self.config.scene_topic,
            qos_profile
        )
        self.vl_command_pub = self.create_publisher(
            VLCommand,
            "/neurostride/vl_command",
            qos_profile
        )

        # 订阅器
        self.state_sub = self.create_subscription(
            RobotState,
            self.config.robot_state_topic,
            self._robot_state_callback,
            qos_profile
        )

        # 状态变量
        self.robot_state: Optional[RobotState] = None
        self.running = False
        self.last_command_time = time.time()

        # 统计
        self.total_inferences = 0
        self.total_commands = 0

        self.get_logger().info("✅ 指挥官节点已启动")
        self.get_logger().info(f"  发布话题: {self.config.cmd_vel_topic}")
        self.get_logger().info(f"  VLM 模型: {self.config.vlm_model_path}")

    def start(self):
        """启动指挥官节点"""
        self.running = True

        # 启动 VLM
        if self.config.vlm_enabled:
            self.get_logger().info("正在加载 VLM 模型...")
            try:
                self.vl_agent.load_model()
                self.vl_agent.start_camera(self.config.camera_id)
                self.get_logger().info("✅ VLM 模型加载完成，摄像头已启动")
            except Exception as e:
                self.get_logger().error(f"VLM 加载失败: {e}")
                self.config.vlm_enabled = False

        # 启动处理循环
        self.process_thread = threading.Thread(
            target=self._processing_loop,
            daemon=True
        )
        self.process_thread.start()

        self.get_logger().info("🚀 指挥官节点运行中...")

    def _processing_loop(self):
        """主处理循环"""
        rate = self.create_rate(self.config.command_freq)

        while self.running and rclpy.ok():
            try:
                # 获取用户指令（可以从订阅或参数服务器获取）
                user_instruction = self._get_user_instruction()

                if self.config.vlm_enabled and user_instruction:
                    # VLM 推理
                    result = self.vl_agent.process_live_scene(user_instruction)

                    # 发布场景分析结果
                    self._publish_scene(result)

                    # 生成并发布速度命令
                    self._publish_command(result)

                rate.sleep()

            except Exception as e:
                self.get_logger().error(f"处理循环错误: {e}")

    def _get_user_instruction(self) -> Optional[str]:
        """
        获取用户指令
        可以从多个来源获取:
        1. ROS2 话题订阅
        2. 参数服务器
        3. 键盘输入（调试用）
        """
        # 这里返回固定指令，实际可改为订阅 ROS2 话题
        return "走向前方的目标"

    def _publish_scene(self, result: Dict[str, Any]):
        """发布场景描述"""
        msg = String()
        msg.data = json.dumps(result, ensure_ascii=False)
        self.scene_pub.publish(msg)

        # 记录日志
        self.get_logger().debug(
            f"场景: {result.get('scene_description', 'N/A')[:50]}..."
        )

    def _publish_command(self, result: Dict[str, Any]):
        """发布速度命令"""
        velocity = result.get("velocity", {"vx": 0.0, "vy": 0.0, "vyaw": 0.0})

        # Twist 消息
        twist = Twist()
        twist.linear.x = float(velocity.get("vx", 0.0))
        twist.linear.y = float(velocity.get("vy", 0.0))
        twist.linear.z = 0.0
        twist.angular.x = 0.0
        twist.angular.y = 0.0
        twist.angular.z = float(velocity.get("vyaw", 0.0))

        self.cmd_vel_pub.publish(twist)

        # VLCommand 消息（包含额外信息）
        vl_cmd = VLCommand()
        vl_cmd.header.stamp = self.get_clock().now().to_msg()
        vl_cmd.command = result.get("command", "")
        vl_cmd.action_type = result.get("action_type", "walk")
        vl_cmd.confidence = 0.8  # 可以从模型获取
        vl_cmd.objects = json.dumps(result.get("objects", []))
        vl_cmd.hazards = json.dumps(result.get("hazards", []))

        self.vl_command_pub.publish(vl_cmd)

        self.total_commands += 1

        if self.total_commands % 10 == 0:
            self.get_logger().info(
                f"发布 #{self.total_commands}: vx={twist.linear.x:.2f}, "
                f"vyaw={twist.angular.z:.2f}"
            )

    def _robot_state_callback(self, msg: RobotState):
        """机器人状态回调"""
        self.robot_state = msg

    def stop(self):
        """停止节点"""
        self.running = False
        if hasattr(self, 'vl_agent'):
            self.vl_agent.stop_camera()
            self.vl_agent.close()
        self.get_logger().info("👋 指挥官节点已停止")


def main(args=None):
    rclpy.init(args=args)

    config = CommanderConfig()
    node = CommanderNode(config)

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
