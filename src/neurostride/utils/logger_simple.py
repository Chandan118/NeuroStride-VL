"""
NeuroStride-VL: Simple Logger Module
=====================================
Fallback logging when full logger is unavailable
"""

import logging
import sys

# Basic logging configuration
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
