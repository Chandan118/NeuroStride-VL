"""
NeuroStride-VL: Bipedal Robot Vision-Language-Action Framework
================================================================

An end-to-end bipedal robot control system combining high-level reasoning
from Large Language Models (LLM) with low-level balance control from
Deep Reinforcement Learning (DRL).

Authors: NeuroStride-VL Team
License: MIT
"""

__version__ = "0.1.0"
__author__ = "NeuroStride-VL Team"
__email__ = "contact@neurostride-vl.ai"
__license__ = "MIT"
__description__ = "Vision-Language-Action Bipedal Robot Framework"

# Core module imports
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
