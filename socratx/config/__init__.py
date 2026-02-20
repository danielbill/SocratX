"""Configuration module for SocratX."""

from .loader import load_config, get_config_path
from .schema import Config

__all__ = ["Config", "load_config", "get_config_path"]
