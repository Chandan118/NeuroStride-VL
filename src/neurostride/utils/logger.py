"""
NeuroStride-VL: Logging Utilities
==================================
Provides structured, colored logging output
"""

import logging
import sys
from datetime import datetime
from typing import Optional

# Color codes
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
    """Colored log formatter"""

    COLORS = {
        'DEBUG': Colors.CYAN,
        'INFO': Colors.BLUE,
        'SUCCESS': Colors.GREEN,
        'WARNING': Colors.YELLOW,
        'ERROR': Colors.RED,
        'CRITICAL': Colors.RED + Colors.BOLD,
    }

    def format(self, record):
        # Add colors
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{Colors.ENDC}"
            record.msg = f"{self.COLORS[levelname]}{record.msg}{Colors.ENDC}"
        return super().format(record)


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Get a colored logger"""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # Format
    formatter = ColoredFormatter(
        fmt='%(asctime)s [%(levelname)-8s] %(name)s: %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    return logger


# Convenience functions
def log_info(msg: str, *args, **kwargs):
    logging.getLogger(__name__).info(msg, *args, **kwargs)


def log_success(msg: str, *args, **kwargs):
    logger = logging.getLogger(__name__)
    logger.log(25, msg, *args, **kwargs)  # Custom level 25


def log_warning(msg: str, *args, **kwargs):
    logging.getLogger(__name__).warning(msg, *args, **kwargs)


def log_error(msg: str, *args, **kwargs):
    logging.getLogger(__name__).error(msg, *args, **kwargs)


def log_debug(msg: str, *args, **kwargs):
    logging.getLogger(__name__).debug(msg, *args, **kwargs)


# Register custom SUCCESS log level
logging.addLevelName(25, 'SUCCESS')
