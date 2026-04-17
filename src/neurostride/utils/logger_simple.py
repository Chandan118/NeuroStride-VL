"""
NeuroStride-VL 简易日志模块
======================
当完整logger不可用时的后备方案
"""

import logging
import sys

# 基础日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)-8s] %(name)s: %(message)s',
    datefmt='%H:%M:%S'
)

def log_info(msg: str, *args, **kwargs):
    logging.getLogger("neurostride").info(msg, *args, **kwargs)

def log_success(msg: str, *args, **kwargs):
    logging.getLogger("neurostride").info(f"✅ {msg}", *args, **kwargs)

def log_warning(msg: str, *args, **kwargs):
    logging.getLogger("neurostride").warning(msg, *args, **kwargs)

def log_error(msg: str, *args, **kwargs):
    logging.getLogger("neurostride").error(msg, *args, **kwargs)

def log_debug(msg: str, *args, **kwargs):
    logging.getLogger("neurostride").debug(msg, *args, **kwargs)
