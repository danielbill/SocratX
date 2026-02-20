"""pytest 测试配置"""
import pytest
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 导入配置相关 - 使用绝对导入
from config.loader import load_config, save_config, get_config_path
from config.schema import Config, AgentsConfig, AgentDefaults, ProviderConfig, ProvidersConfig
