"""
NeuroStride-VL 日志工具
=======================
提供结构化、彩色的日志输出
"""

import logging
import sys
from datetime import datetime
from typing import Optional

# 颜色代码
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


class ColoredFormatter(logging.Formatter):
    """彩色日志格式化器"""

    COLORS = {
        'DEBUG': Colors.CYAN,
        'INFO': Colors.BLUE,
        'SUCCESS': Colors.GREEN,
        'WARNING': Colors.YELLOW,
        'ERROR': Colors.RED,
        'CRITICAL': Colors.RED + Colors.BOLD,
    }

    def format(self, record):
        # 添加颜色
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{Colors.ENDC}"
            record.msg = f"{self.COLORS[levelname]}{record.msg}{Colors.ENDC}"
        return super().format(record)


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """获取带颜色的日志记录器"""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 避免重复添加 handler
    if logger.handlers:
        return logger

    # 控制台 handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # 格式化
    formatter = ColoredFormatter(
        fmt='%(asctime)s [%(levelname)-8s] %(name)s: %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    return logger


# 快捷函数
def log_info(msg: str, *args, **kwargs):
    logging.getLogger(__name__).info(msg, *args, **kwargs)


def log_success(msg: str, *args, **kwargs):
    logger = logging.getLogger(__name__)
    logger.log(25, msg, *args, **kwargs)  # 自定义级别 25


def log_warning(msg: str, *args, **kwargs):
    logging.getLogger(__name__).warning(msg, *args, **kwargs)


def log_error(msg: str, *args, **kwargs):
    logging.getLogger(__name__).error(msg, *args, **kwargs)


def log_debug(msg: str, *args, **kwargs):
    logging.getLogger(__name__).debug(msg, *args, **kwargs)


# 注册自定义日志级别 SUCCESS
logging.addLevelName(25, 'SUCCESS')
