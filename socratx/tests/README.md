# SocratX 测试用例使用手册

> **版本**: 1.0  
> **最后更新**: 2026 年 2 月 20 日

## 目录

1. [快速开始](#快速开始)
2. [测试目录结构](#测试目录结构)
3. [运行测试](#运行测试)
4. [测试模块说明](#测试模块说明)
5. [编写测试用例](#编写测试用例)
6. [常见问题](#常见问题)

---

## 快速开始

```bash
# 1. 进入 socratx 目录
cd socratx

# 2. 运行所有测试
.venv\Scripts\pytest.exe tests/ -v

# 3. 运行特定测试文件
.venv\Scripts\pytest.exe tests/test_tools/test_registry.py -v

# 4. 运行特定测试函数
.venv\Scripts\pytest.exe tests/test_tools/test_registry.py::TestToolRegistry::test_register_tool -v
```

---

## 测试目录结构

```
socratx/tests/
├── conftest.py              # 全局 fixtures
├── test_chat.py             # LLM 对话测试
├── test_config/
│   └── test_schema.py       # 配置系统测试
├── test_tools/
│   ├── test_registry.py     # 工具注册表测试
│   ├── test_tool_base.py    # 工具基类测试
│   ├── test_file_tools.py   # 文件工具测试
│   ├── test_shell_tools.py  # Shell 工具测试
│   └── test_web_tools.py    # Web 工具测试
└── test_integration/
    ├── test_llm_with_tools.py   # LLM+ 工具调用测试
    └── test_llm_read_file.py    # LLM 读取文件测试
```

---

## 运行测试

### 基本命令

```bash
# 运行所有测试
cd socratx
.venv\Scripts\pytest.exe tests/ -v

# 运行特定目录
.venv\Scripts\pytest.exe tests/test_tools/ -v

# 运行特定文件
.venv\Scripts\pytest.exe tests/test_chat.py -v

# 运行特定测试类
.venv\Scripts\pytest.exe tests/test_tools/test_registry.py::TestToolRegistry -v

# 运行特定测试函数
.venv\Scripts\pytest.exe tests/test_chat.py::test_chat_completion -v
```

### 常用参数

| 参数 | 说明 |
|------|------|
| `-v` | 详细输出 |
| `-q` | 简洁输出 |
| `-s` | 显示 print 输出 |
| `--tb=short` | 简短 traceback |
| `-x` | 遇到失败停止 |
| `--maxfail=3` | 失败 3 次后停止 |
| `-k "pattern"` | 按名称过滤测试 |
| `--cov=socratx` | 显示覆盖率 |
| `--cov-report=html` | 生成 HTML 覆盖率报告 |

### 示例

```bash
# 运行所有工具测试，显示覆盖率
.venv\Scripts\pytest.exe tests/test_tools/ -v --cov=socratx --cov-report=html

# 运行包含 "file" 的测试
.venv\Scripts\pytest.exe tests/ -v -k "file"

# 运行测试并显示日志输出
.venv\Scripts\pytest.exe tests/test_integration/ -v -s

# 遇到第一个失败就停止
.venv\Scripts\pytest.exe tests/ -x
```

---

## 测试模块说明

### 1. 配置测试 (`test_config/test_schema.py`)

测试配置系统的核心功能：

```python
# 测试默认配置
pytest tests/test_config/test_schema.py::TestConfig::test_default_config -v

# 测试从文件加载配置
pytest tests/test_config/test_schema.py::TestLoadConfig::test_load_config_from_file -v

# 测试保存配置
pytest tests/test_config/test_schema.py::TestSaveConfig::test_save_config -v
```

### 2. 对话测试 (`test_chat.py`)

测试 LLM 基本对话功能：

```python
# 测试基本对话
pytest tests/test_chat.py::test_chat_completion -v
```

### 3. 工具测试 (`test_tools/`)

#### 工具注册表测试

```python
# 测试注册工具
pytest tests/test_tools/test_registry.py::TestToolRegistry::test_register_tool -v

# 测试执行工具
pytest tests/test_tools/test_registry.py::TestToolRegistry::test_execute_tool -v

# 测试获取工具定义
pytest tests/test_tools/test_registry.py::TestToolRegistry::test_get_definitions -v
```

#### 文件工具测试

```python
# 测试写入文件
pytest tests/test_tools/test_file_tools.py::TestFileTools::test_file_write_success -v

# 测试读取文件
pytest tests/test_tools/test_file_tools.py::TestFileTools::test_file_read_success -v

# 测试列出目录
pytest tests/test_tools/test_file_tools.py::TestFileTools::test_file_list_dir -v
```

#### Shell 工具测试

```python
# 测试执行命令
pytest tests/test_tools/test_shell_tools.py::TestShellTools::test_shell_exec_success -v

# 测试错误处理
pytest tests/test_tools/test_shell_tools.py::TestShellTools::test_shell_exec_error -v
```

### 4. 集成测试 (`test_integration/`)

#### LLM + 工具调用测试

```python
# 测试 LLM 调用 write_file 工具
pytest tests/test_integration/test_llm_with_tools.py::test_llm_with_file_tool_write_file -v -s

# 测试 LLM 调用 read_file 工具
pytest tests/test_integration/test_llm_read_file.py::test_llm_read_file -v -s
```

---

## 编写测试用例

### 基本结构

```python
"""模块测试说明"""
import pytest
from module import ClassToTest


class TestClassName:
    """测试类"""

    def test_feature_success(self):
        """测试功能成功场景"""
        obj = ClassToTest()
        result = obj.method()
        assert result == "expected"

    def test_feature_error(self):
        """测试功能错误场景"""
        obj = ClassToTest()
        result = obj.method(invalid_input)
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_async_feature(self):
        """测试异步功能"""
        obj = ClassToTest()
        result = await obj.async_method()
        assert result is not None
```

### Fixtures

在 `conftest.py` 中定义全局 fixtures：

```python
import pytest

@pytest.fixture
def tool_registry():
    """创建工具注册表"""
    from agent.tools.registry import ToolRegistry
    registry = ToolRegistry()
    # 注册需要的工具
    return registry
```

### 使用 tmp_path

```python
def test_file_operation(tmp_path):
    """测试文件操作"""
    test_file = tmp_path / "test.txt"
    test_file.write_text("hello")
    
    assert test_file.exists()
    assert test_file.read_text() == "hello"
```

### 参数化测试

```python
@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
])
def test_double(input, expected):
    assert input * 2 == expected
```

---

## 常见问题

### Q1: 测试失败 "ModuleNotFoundError"

**原因**: 导入路径错误

**解决**: 使用相对导入
```python
# ❌ 错误
from socratx.agent.tools import Tool

# ✅ 正确
from agent.tools import Tool
```

### Q2: 异步测试警告

**原因**: 缺少 `@pytest.mark.asyncio` 装饰器

**解决**:
```python
@pytest.mark.asyncio
async def test_async_method():
    result = await obj.async_method()
    assert result is not None
```

### Q3: 覆盖率报告为空

**原因**: 测试未导入模块

**解决**: 检查导入路径，确保测试正确导入被测模块

### Q4: 中文显示乱码

**原因**: 文件编码问题

**解决**: 使用 UTF-8 编码保存文件
```python
# 读取文件
content = Path("file.txt").read_text(encoding='utf-8')

# 写入文件
Path("file.txt").write_text("内容", encoding='utf-8')
```

### Q5: LLM 测试失败

**原因**: API Key 未配置或模型不可用

**解决**:
1. 检查 `~/.nanobot/config.json` 配置
2. 确认 API Key 有效
3. 确认模型名称正确

---

## 附录

### 测试命令速查表

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定目录
pytest tests/test_tools/ -v

# 运行特定文件
pytest tests/test_chat.py -v

# 运行特定测试
pytest tests/test_chat.py::test_chat_completion -v

# 显示覆盖率
pytest tests/ -v --cov=socratx

# 生成 HTML 覆盖率报告
pytest tests/ -v --cov=socratx --cov-report=html

# 显示 print 输出
pytest tests/ -v -s

# 遇到失败停止
pytest tests/ -x

# 按名称过滤
pytest tests/ -k "file"
```

### 测试文件命名规范

- 测试文件：`test_*.py`
- 测试类：`Test*`
- 测试函数：`test_*`

### 断言方法

```python
assert value == expected      # 等于
assert value != expected      # 不等于
assert value is None          # 为空
assert value is not None      # 不为空
assert "substring" in value   # 包含
assert len(value) > 0         # 长度
assert isinstance(obj, Class) # 类型
```

---

**文档结束**
