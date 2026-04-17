"""
NeuroStride-VL 配置文件加载器
==============================
支持 YAML 和 JSON 格式配置
"""

import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional


def load_config(config_path: str) -> Dict[str, Any]:
    """
    加载配置文件

    Args:
        config_path: 配置文件路径（支持 .yaml, .yml, .json）

    Returns:
        配置字典
    """
    path = Path(config_path)

    if not path.exists():
        raise FileNotFoundError(f"配置文件未找到: {config_path}")

    with open(path, 'r', encoding='utf-8') as f:
        if path.suffix in ['.yaml', '.yml']:
            config = yaml.safe_load(f)
        elif path.suffix == '.json':
            config = json.load(f)
        else:
            raise ValueError(f"不支持的配置文件格式: {path.suffix}")

    return config or {}


def save_config(config: Dict[str, Any], config_path: str, format: str = 'yaml'):
    """
    保存配置文件

    Args:
        config: 配置字典
        config_path: 保存路径
        format: 格式 ('yaml' 或 'json')
    """
    path = Path(config_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, 'w', encoding='utf-8') as f:
        if format == 'yaml':
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        elif format == 'json':
            json.dump(config, f, indent=2, ensure_ascii=False)
        else:
            raise ValueError(f"不支持的格式: {format}")


def merge_configs(base: Dict, override: Dict) -> Dict:
    """
    合并配置（override 覆盖 base）

    Args:
        base: 基础配置
        override: 覆盖配置

    Returns:
        合并后的配置
    """
    result = base.copy()

    for key, value in override.items():
        if isinstance(value, dict) and key in result and isinstance(result[key], dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value

    return result
