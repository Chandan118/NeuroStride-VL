"""
NeuroStride-VL: 双足机器人视觉-语言-动作框架
=================================================

一个端到端的双足机器人控制系统，结合大语言模型(LLM)的高级推理
与深度强化学习(DRL)的低层平衡控制。

作者: NeuroStride-VL Team
许可证: MIT
"""

__version__ = "0.1.0"
__author__ = "NeuroStride-VL Team"
__email__ = "contact@neurostride-vl.ai"
__license__ = "MIT"
__description__ = "Vision-Language-Action Bipedal Robot Framework"

# 核心模块导入
from neurostride.env.bipedal_env import BipedalEnv, RobotConfig, make_env
from neurostride.agents.rl_agent import (
    RLAgent,
    PPOAgent,
    SACAgent,
    TrainingConfig,
    create_agent,
)

__all__ = [
    "BipedalEnv",
    "RobotConfig",
    "make_env",
    "RLAgent",
    "PPOAgent",
    "SACAgent",
    "TrainingConfig",
    "create_agent",
]
