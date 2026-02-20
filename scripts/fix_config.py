#!/usr/bin/env python
"""修复配置文件，添加 api_base 并保留 API Key"""

import json
from pathlib import Path

config_path = Path.home() / '.socratx' / 'config.json'

with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

# 保留现有 API Key
existing_key = ""
if 'zai' in config.get('providers', {}):
    existing_key = config['providers']['zai'].get('api_key', '')

# 更新配置
config['providers']['zai'] = {
    'apiKey': existing_key,
    'apiBase': 'https://open.bigmodel.cn/api/paas/v4',
    'extraHeaders': None,
}

with open(config_path, 'w', encoding='utf-8') as f:
    json.dump(config, f, indent=2, ensure_ascii=False)

print(f'Config updated: {config_path}')
print(f'API Key: {existing_key[:10]}...')
print('API Base: https://open.bigmodel.cn/api/paas/v4')
