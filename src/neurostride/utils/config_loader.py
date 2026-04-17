"""
NeuroStride-VL: Configuration Loader
=====================================
Supports YAML and JSON configuration formats
"""

import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration file

    Args:
        config_path: Config file path (supports .yaml, .yml, .json)

    Returns:
        Configuration dictionary
    """
    path = Path(config_path)

    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(path, 'r', encoding='utf-8') as f:
        if path.suffix in ['.yaml', '.yml']:
            config = yaml.safe_load(f)
        elif path.suffix == '.json':
            config = json.load(f)
        else:
            raise ValueError(f"Unsupported config format: {path.suffix}")

    return config or {}


def save_config(config: Dict[str, Any], config_path: str, format: str = 'yaml'):
    """
    Save configuration file

    Args:
        config: Configuration dictionary
        config_path: Save path
        format: Format ('yaml' or 'json')
    """
    path = Path(config_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, 'w', encoding='utf-8') as f:
        if format == 'yaml':
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        elif format == 'json':
            json.dump(config, f, indent=2, ensure_ascii=False)
        else:
            raise ValueError(f"Unsupported format: {format}")


def merge_configs(base: Dict, override: Dict) -> Dict:
    """
    Merge configurations (override overrides base)

    Args:
        base: Base configuration
        override: Override configuration

    Returns:
        Merged configuration
    """
    result = base.copy()

    for key, value in override.items():
        if isinstance(value, dict) and key in result and isinstance(result[key], dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value

    return result
