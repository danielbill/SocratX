"""
Config Loader - 配置加载和保存

参考: nanobot/nanobot/config/loader.py
负责从文件加载配置和保存配置到文件
"""

import json
from pathlib import Path
from typing import Optional

from .schema import SocratXConfig, get_default_config


class ConfigLoader:
    """
    配置加载器

    负责从文件加载配置，支持 JSON 和 YAML 格式
    """

    DEFAULT_CONFIG_PATH = Path.home() / ".socratx" / "config.json"

    def __init__(self, config_path: Optional[Path | str] = None):
        """
        初始化配置加载器

        Args:
            config_path: 配置文件路径，默认为 ~/.socratx/config.json
        """
        if config_path is None:
            self.config_path = self.DEFAULT_CONFIG_PATH
        else:
            self.config_path = Path(config_path)

        # 确保配置目录存在
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> SocratXConfig:
        """
        加载配置

        如果配置文件不存在，返回默认配置

        Returns:
            SocratXConfig
        """
        if not self.config_path.exists():
            # 配置文件不存在，创建默认配置
            config = get_default_config()
            self.save(config)
            return config

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            return SocratXConfig(**data)

        except (json.JSONDecodeError, TypeError) as e:
            print(f"Error loading config: {e}, using default config")
            return get_default_config()

    def save(self, config: SocratXConfig) -> None:
        """
        保存配置

        Args:
            config: 要保存的配置
        """
        with open(self.config_path, "w", encoding="utf-8") as f:
            f.write(config.model_dump_json())

    def update(self, updates: dict) -> SocratXConfig:
        """
        更新配置

        Args:
            updates: 要更新的字段

        Returns:
            更新后的配置
        """
        current = self.load()

        # 递归更新配置
        for key, value in updates.items():
            if hasattr(current, key):
                current_attr = getattr(current, key)
                if isinstance(current_attr, dict) and isinstance(value, dict):
                    current_attr.update(value)
                else:
                    setattr(current, key, value)

        self.save(current)
        return current

    def reset(self) -> SocratXConfig:
        """
        重置为默认配置

        Returns:
            默认配置
        """
        config = get_default_config()
        self.save(config)
        return config

    def exists(self) -> bool:
        """检查配置文件是否存在"""
        return self.config_path.exists()

    def get_config_path(self) -> Path:
        """获取配置文件路径"""
        return self.config_path


# 全局配置实例
_global_config: Optional[SocratXConfig] = None
_global_loader: Optional[ConfigLoader] = None


def init_config(config_path: Optional[Path | str] = None) -> SocratXConfig:
    """
    初始化全局配置

    Args:
        config_path: 配置文件路径

    Returns:
        加载的配置
    """
    global _global_config, _global_loader

    _global_loader = ConfigLoader(config_path)
    _global_config = _global_loader.load()

    return _global_config


def get_config() -> SocratXConfig:
    """
    获取全局配置

    Returns:
        当前配置

    Raises:
        RuntimeError: 如果配置未初始化
    """
    if _global_config is None:
        raise RuntimeError("Config not initialized. Call init_config() first.")
    return _global_config


def save_config(config: Optional[SocratXConfig] = None) -> None:
    """
    保存全局配置

    Args:
        config: 要保存的配置，如果为 None 则保存当前配置

    Raises:
        RuntimeError: 如果配置未初始化
    """
    if _global_loader is None:
        raise RuntimeError("Config not initialized. Call init_config() first.")

    config_to_save = config or _global_config
    _global_loader.save(config_to_save)

    if config:
        _global_config = config


def update_config(updates: dict) -> SocratXConfig:
    """
    更新全局配置

    Args:
        updates: 要更新的字段

    Returns:
        更新后的配置
    """
    if _global_loader is None:
        raise RuntimeError("Config not initialized. Call init_config() first.")

    _global_config = _global_loader.update(updates)
    return _global_config


def reset_config() -> SocratXConfig:
    """
    重置全局配置为默认值

    Returns:
        默认配置
    """
    if _global_loader is None:
        raise RuntimeError("Config not initialized. Call init_config() first.")

    _global_config = _global_loader.reset()
    return _global_config
