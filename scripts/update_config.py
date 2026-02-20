#!/usr/bin/env python
"""更新配置文件为 nanobot 格式"""

import json
from pathlib import Path

config_path = Path.home() / '.socratx' / 'config.json'

# nanobot 格式配置
config = {
    "version": "1.0.0",
    "agent": {
        "model": "zai/glm-4",
        "temperature": 0.7,
        "max_tokens": 4096,
        "max_iterations": 20,
        "workspace": "",
        "memory_enabled": True,
        "memory_file": "MEMORY.md",
        "history_file": "HISTORY.md",
        "session_ttl": 86400,
    },
    "tools": {
        "enabled": ["file_read", "file_write", "shell_exec", "web_search"],
        "workspace_read_only": False,
        "allow_shell": True,
        "allowed_shell_commands": [],
        "mcp_servers": [],
    },
    "providers": {"zai": {"api_key": "请在此处填写你的智谱 AI API Key"}},
    "gateway": {
        "host": "127.0.0.1",
        "port": 8000,
        "allow_origins": ["http://localhost:5173", "http://localhost:1420"],
        "require_auth": False,
    },
    "logging": {"level": "INFO", "rotate": True, "max_size": 10485760},
}

with open(config_path, 'w', encoding='utf-8') as f:
    json.dump(config, f, indent=2, ensure_ascii=False)

print('Config updated to nanobot format')
print(f'File location: {config_path}')
print()
print('Please fill in your zai AI API Key in providers.zai.api_key')
