"""
NeuroStride-VL ROS2 桥接模块
=============================
分布式机器人控制
"""

from .commander_node import CommanderNode, CommanderConfig, main as commander_main
from .executor_node import ExecutorNode, ExecutorConfig, main as executor_main

__all__ = [
    'CommanderNode',
    'ExecutorNode',
    'CommanderConfig',
    'ExecutorConfig',
    'commander_main',
    'executor_main',
]
