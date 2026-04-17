"""
NeuroStride-VL: Qwen-2-VL 视觉语言智能体
===========================================
基于 Qwen-2-VL 的场景理解与指令生成模块

功能:
- 实时摄像头画面捕获
- 视觉场景语义分析
- 自然语言指令解析
- 生成机器人动作命令

模型: Qwen/Qwen-VL-2B-Chat (2B 参数，适合边缘部署)
      Qwen/Qwen-VL-7B-Chat (7B 参数，更高精度)

作者: NeuroStride-VL Team
"""

import os
import time
import json
import base64
import threading
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from queue import Queue

import cv2
import numpy as np
from PIL import Image
import torch

from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    AutoProcessor,
    BitsAndBytesConfig,
)
from transformers.generation import GenerationConfig


@dataclass
class VLConfig:
    """视觉语言模型配置"""
    # 模型路径
    model_path: str = "Qwen/Qwen-VL-2B-Chat"

    # 模型加载选项
    use_quantization: bool = True  # 使用 4-bit 量化（减少内存占用）
    device_map: str = "auto"  # "auto", "cuda:0", "mps", "cpu"

    # 生成参数
    max_new_tokens: int = 512
    temperature: float = 0.7
    top_p: float = 0.8
    do_sample: bool = True

    # 系统提示词
    system_prompt: str = """你是一个双足机器人的视觉-语言智能体。
你的任务是根据摄像头画面和用户指令，生成机器人的动作命令。

输出格式必须是严格的 JSON:
{
    "scene_description": "对场景的简短描述",
    "objects": [{"name": "物体名", "position": "相对位置", "distance": "距离(米)"}],
    "hazards": ["潜在危险列表"],
    "command": "自然语言指令",
    "velocity": {"vx": 速度, "vy": 速度, "vyaw": 角速度},
    "action_type": "行走/停止/避障"
}

只输出 JSON，不要包含其他文本。"""

    # 摄像头配置
    camera_id: int = 0
    camera_width: int = 640
    camera_height: int = 480
    fps: int = 30

    # 性能优化
    use_cache: bool = True
    torch_dtype: torch.dtype = torch.float16  # 使用半精度加速


class SceneUnderstanding:
    """场景理解模块"""

    def __init__(self, vl_agent: 'QwenVLAgent'):
        self.vl_agent = vl_agent
        self.cache = {}
        self.cache_ttl = 2.0  # 缓存 2 秒

    def analyze_scene(
        self,
        image: np.ndarray,
        user_instruction: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        分析场景并生成指令

        Args:
            image: RGB 图像 (H, W, 3)
            user_instruction: 用户自然语言指令

        Returns:
            分析结果字典
        """
        # 生成查询
        if user_instruction:
            query = f"用户指令: {user_instruction}\n\n请分析场景并生成机器人指令。"
        else:
            query = "请分析当前场景，识别障碍物、目标物体，并生成默认的前进指令。"

        # 调用 VLM
        response = self.vl_agent.generate_response(image, query)

        # 解析 JSON
        try:
            result = json.loads(response)
            result["timestamp"] = time.time()
            result["success"] = True
        except json.JSONDecodeError:
            # 如果 JSON 解析失败，尝试提取 JSON 部分
            result = {
                "scene_description": response[:200],
                "objects": [],
                "hazards": [],
                "command": "继续前进",
                "velocity": {"vx": 0.5, "vy": 0.0, "vyaw": 0.0},
                "action_type": "行走",
                "success": False,
                "raw_response": response,
            }

        return result

    def detect_obstacles(self, image: np.ndarray) -> List[Dict]:
        """检测障碍物（简化版）"""
        # 这里可以集成专门的障碍物检测模型（如 YOLO）
        # 目前返回空列表
        return []

    def estimate_depth(self, image: np.ndarray) -> np.ndarray:
        """估计深度图（可选）"""
        # 未来可集成 MiDaS 等深度估计模型
        return np.zeros((image.shape[0], image.shape[1]))


class QwenVLAgent:
    """
    Qwen-2-VL 智能体

    主要功能:
    1. 加载和运行 Qwen-VL 模型
    2. 处理图像和文本输入
    3. 生成结构化的机器人指令
    4. 支持量化以在边缘设备运行
    """

    def __init__(self, config: VLConfig = None):
        """
        初始化 VLM 智能体

        Args:
            config: VLM 配置
        """
        self.config = config or VLConfig()
        self.model = None
        self.tokenizer = None
        self.processor = None

        # 初始化场景理解模块
        self.scene_analyzer = SceneUnderstanding(self)

        # 摄像头相关
        self.camera = None
        self.camera_running = False
        self.frame_queue = Queue(maxsize=10)

        # 性能统计
        self.inference_times = []
        self.total_inferences = 0

        log_info(f"QwenVLAgent 初始化: {self.config.model_path}")

    def load_model(self):
        """加载 Qwen-VL 模型"""
        log_info(f"正在加载模型: {self.config.model_path}...")
        start_time = time.time()

        try:
            # 量化配置（4-bit 减少内存占用）
            quantization_config = None
            if self.config.use_quantization:
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4",
                )
                log_info("启用 4-bit 量化（减少内存使用）")

            # 加载 tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.config.model_path,
                trust_remote_code=True,
            )

            # 加载 processor
            self.processor = AutoProcessor.from_pretrained(
                self.config.model_path,
                trust_remote_code=True,
            )

            # 加载模型
            self.model = AutoModelForCausalLM.from_pretrained(
                self.config.model_path,
                device_map=self.config.device_map,
                torch_dtype=self.config.torch_dtype,
                trust_remote_code=True,
                quantization_config=quantization_config,
            )

            # 设置生成配置
            self.model.generation_config = GenerationConfig.from_pretrained(
                self.config.model_path,
                trust_remote_code=True,
            )

            load_time = time.time() - start_time
            log_success(f"模型加载完成！耗时: {load_time:.2f}s")

            # 打印模型信息
            self._print_model_info()

        except Exception as e:
            log_error(f"模型加载失败: {e}")
            raise

    def _print_model_info(self):
        """打印模型信息"""
        if self.model is None:
            return

        # 计算参数量
        total_params = sum(p.numel() for p in self.model.parameters())
        trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)

        print(f"\n{'=' * 50}")
        print("模型信息:")
        print(f"  总参数量: {total_params / 1e9:.2f}B")
        print(f"  可训练参数: {trainable_params / 1e6:.1f}M")
        print(f"  设备: {self.model.device}")
        print(f"  数据类型: {self.model.dtype}")
        print(f"  量化: {'4-bit' if self.config.use_quantization else 'None'}")
        print(f"{'=' * 50}\n")

    def generate_response(
        self,
        image: np.ndarray,
        prompt: str,
        history: Optional[List[Dict]] = None
    ) -> str:
        """
        生成 VLM 响应

        Args:
            image: RGB 图像 (H, W, 3)
            prompt: 文本提示
            history: 对话历史

        Returns:
            生成的文本响应
        """
        if self.model is None:
            raise RuntimeError("模型未加载，请先调用 load_model()")

        start_time = time.time()

        try:
            # 预处理图像
            if isinstance(image, np.ndarray):
                image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

            # 构建消息（Qwen-VL 格式）
            messages = [
                {
                    "role": "system",
                    "content": [{"type": "text", "text": self.config.system_prompt}]
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "image": image},
                        {"type": "text", "text": prompt},
                    ]
                }
            ]

            # 应用聊天模板
            text = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )

            # 分词
            model_inputs = self.tokenizer(
                text,
                return_tensors="pt",
                padding=True,
            ).to(self.model.device)

            # 生成
            with torch.no_grad():
                generated_ids = self.model.generate(
                    **model_inputs,
                    max_new_tokens=self.config.max_new_tokens,
                    temperature=self.config.temperature,
                    top_p=self.config.top_p,
                    do_sample=self.config.do_sample,
                    use_cache=self.config.use_cache,
                )

            # 解码
            response = self.tokenizer.batch_decode(
                generated_ids,
                skip_special_tokens=True,
            )[0]

            # 提取助手回复（去掉提示部分）
            response = self._extract_assistant_response(response)

            inference_time = time.time() - start_time
            self.inference_times.append(inference_time)
            self.total_inferences += 1

            if self.total_inferences % 10 == 0:
                avg_time = np.mean(self.inference_times[-10:])
                log_debug(f"平均推理时间: {avg_time:.2f}s")

            return response

        except Exception as e:
            log_error(f"推理失败: {e}")
            return f"错误: {str(e)}"

    def _extract_assistant_response(self, full_text: str) -> str:
        """从完整文本中提取助手回复"""
        # Qwen-VL 使用特定标记
        if "assistant" in full_text.lower():
            # 查找 assistant 标记后的内容
            parts = full_text.split("assistant")
            if len(parts) > 1:
                return parts[-1].strip()
        return full_text

    def start_camera(self, camera_id: int = None):
        """启动摄像头捕获线程"""
        if self.camera_running:
            log_warning("摄像头已在运行")
            return

        self.camera_id = camera_id or self.config.camera_id

        def camera_thread():
            self.camera = cv2.VideoCapture(self.camera_id)
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.camera_width)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.camera_height)

            if not self.camera.isOpened():
                log_error(f"无法打开摄像头 {self.camera_id}")
                return

            self.camera_running = True
            log_info(f"摄像头已启动: {self.camera_id}")

            while self.camera_running:
                ret, frame = self.camera.read()
                if ret:
                    if not self.frame_queue.full():
                        self.frame_queue.put(frame)

                time.sleep(1.0 / self.config.fps)

            self.camera.release()
            log_info("摄像头已停止")

        self.camera_thread = threading.Thread(target=camera_thread, daemon=True)
        self.camera_thread.start()

    def stop_camera(self):
        """停止摄像头"""
        self.camera_running = False
        if hasattr(self, 'camera_thread'):
            self.camera_thread.join(timeout=2.0)

    def get_latest_frame(self) -> Optional[np.ndarray]:
        """获取最新帧"""
        if self.frame_queue.empty():
            return None
        return self.frame_queue.get(timeout=0.1)

    def process_live_scene(
        self,
        user_instruction: str,
        max_frames: int = 1
    ) -> Dict[str, Any]:
        """
        实时处理场景

        Args:
            user_instruction: 用户指令
            max_frames: 最大处理帧数（用于平滑）

        Returns:
            处理结果
        """
        results = []

        for _ in range(max_frames):
            frame = self.get_latest_frame()
            if frame is not None:
                result = self.scene_analyzer.analyze_scene(frame, user_instruction)
                results.append(result)

        if not results:
            return {"error": "未获取到摄像头画面"}

        # 返回最新结果
        return results[-1]

    def close(self):
        """清理资源"""
        self.stop_camera()
        if self.model is not None:
            del self.model
            torch.cuda.empty_cache() if torch.cuda.is_available() else None


# ==================== ROS2 集成接口 ====================

class ROS2VLBridge:
    """
    ROS2 视觉-语言桥接

    将 VLM 的输出转换为 ROS2 消息
    """

    def __init__(self, vl_agent: QwenVLAgent):
        self.vl_agent = vl_agent
        self.running = False

        # ROS2 相关（需要 ROS2 环境）
        self.node = None
        self.publisher = None

    def start(self):
        """启动 ROS2 桥接节点"""
        try:
            import rclpy
            from rclpy.node import Node
            from geometry_msgs.msg import Twist, PoseStamped
            from std_msgs.msg import String

            rclpy.init()
            self.node = Node('neurostride_vl_bridge')
            self.publisher = self.node.create_publisher(Twist, '/cmd_vel', 10)
            self.scene_pub = self.node.create_publisher(String, '/scene_description', 10)

            self.running = True
            log_info("ROS2 VL Bridge 已启动")

            # 启动处理线程
            self.process_thread = threading.Thread(target=self._process_loop, daemon=True)
            self.process_thread.start()

        except ImportError:
            log_warning("ROS2 未安装，跳过 ROS2 集成")

    def _process_loop(self):
        """处理循环"""
        while self.running:
            try:
                # 获取用户指令（这里简化为固定指令）
                instruction = "走向前方的目标"

                # 处理场景
                result = self.vl_agent.process_live_scene(instruction)

                # 发布速度命令
                if "velocity" in result:
                    self._publish_twist(result["velocity"])

                # 发布场景描述
                self._publish_scene(result)

                time.sleep(0.1)  # 10Hz 处理频率

            except Exception as e:
                log_error(f"ROS2 处理错误: {e}")

    def _publish_twist(self, velocity: Dict):
        """发布速度命令"""
        from geometry_msgs.msg import Twist
        msg = Twist()
        msg.linear.x = float(velocity.get("vx", 0.0))
        msg.linear.y = float(velocity.get("vy", 0.0))
        msg.angular.z = float(velocity.get("vyaw", 0.0))
        self.publisher.publish(msg)

    def _publish_scene(self, result: Dict):
        """发布场景描述"""
        from std_msgs.msg import String
        msg = String()
        msg.data = json.dumps(result, ensure_ascii=False)
        self.scene_pub.publish(msg)

    def stop(self):
        """停止"""
        self.running = False
        if self.node:
            import rclpy
            rclpy.shutdown()


# ==================== 主程序 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("NeuroStride-VL: Qwen-VL 智能体测试")
    print("=" * 60)

    # 创建配置
    config = VLConfig(
        model_path="Qwen/Qwen-VL-2B-Chat",  # 使用 2B 小模型测试
        use_quantization=False,  # 测试时禁用量化（加快加载）
    )

    # 创建智能体
    agent = QwenVLAgent(config)

    try:
        # 加载模型
        agent.load_model()

        # 创建测试图像（白色背景）
        test_image = np.ones((480, 640, 3), dtype=np.uint8) * 255
        cv2.putText(
            test_image, "Test Scene: Robot in Lab",
            (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2
        )

        # 测试查询
        query = "场景中有什么？请输出 JSON 格式。"

        print(f"\n查询: {query}")
        print("-" * 60)

        response = agent.generate_response(test_image, query)
        print(f"响应:\n{response}")

        print("\n✅ Qwen-VL 智能体测试完成！")

    except Exception as e:
        log_error(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        agent.close()
