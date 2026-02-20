# SocratX CI/CD 配置指南

本文档介绍 SocratX 项目的 CI/CD 配置和测试自动化流程。

---

## GitHub Actions 工作流

### 工作流文件

**位置**: `.github/workflows/test.yml`

### 触发条件

| 事件 | 分支 | 说明 |
|------|------|------|
| `push` | main, develop | 推送到主分支或开发分支 |
| `pull_request` | main | PR 请求合并到主分支 |

### 工作流程

```
代码提交 → 触发 GitHub Actions → 运行测试 → 上传覆盖率 → 完成
                                    ↓
                              失败则阻止合并
```

---

## 测试任务

### 1. 前端测试 (test-frontend)

**运行环境**: Ubuntu latest

**步骤**:
1. Checkout 代码
2. 设置 pnpm (v9)
3. 设置 Node.js (v20)
4. 安装依赖 (`pnpm install`)
5. 运行测试 (`cd apps/desktop && pnpm test:run`)
6. 上传覆盖率到 Codecov

**测试框架**: Vitest + React Testing Library

**覆盖率文件**: `apps/desktop/coverage/coverage-final.json`

---

### 2. Python 测试 (test-python)

**运行环境**: Ubuntu latest

**步骤**:
1. Checkout 代码
2. 设置 Python (3.11)
3. 安装依赖 (`pip install -r requirements.txt`)
4. 运行测试 (`pytest --cov=agent --cov=providers --cov=config --cov-report=xml`)
5. 上传覆盖率到 Codecov

**测试框架**: pytest + pytest-cov + pytest-asyncio

**覆盖率文件**: `services/agent/coverage.xml`

---

### 3. Rust 测试 (test-rust)

**运行环境**: Ubuntu latest

**步骤**:
1. Checkout 代码
2. 设置 Rust (stable)
3. 缓存 Cargo 依赖
4. 运行测试 (`cargo test`)
5. 上传覆盖率到 Codecov

**测试框架**: Rust 内置测试

**覆盖率文件**: `apps/desktop/src-tauri/coverage/lcov.info`

---

## Codecov 集成

### 覆盖率上传

所有测试任务都会上传覆盖率到 [Codecov](https://about.codecov.io/)。

**配置**:
```yaml
uses: codecov/codecov-action@v4
with:
  files: <覆盖率文件路径>
  flags: <frontend|backend|rust>
```

### 查看覆盖率报告

访问：`https://app.codecov.io/gh/<your-org>/SocratX`

---

## 本地运行测试

### Python 后端

```bash
cd services/agent

# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_agent/test_loop.py -v

# 生成覆盖率报告
pytest --cov=agent --cov=providers --cov=config --cov-report=html
```

### 前端

```bash
cd apps/desktop

# 运行所有测试
pnpm test:run

# 监视模式
pnpm test

# 生成覆盖率
pnpm test:coverage
```

### Rust

```bash
cd apps/desktop/src-tauri

# 运行所有测试
cargo test

# 显示输出
cargo test -- --nocapture
```

---

## 添加新测试

### Python 测试

1. 在 `services/agent/tests/` 创建 `test_*.py` 文件
2. 使用 `Test*` 类名和 `test_*` 函数名
3. 使用 `@pytest.mark.asyncio` 标记异步测试

**示例**:
```python
import pytest

class TestMyFeature:
    @pytest.mark.asyncio
    async def test_something(self):
        assert True
```

### 前端测试

1. 在 `apps/desktop/src/` 创建 `*.test.tsx` 或 `*.test.ts` 文件
2. 使用 Vitest 语法

**示例**:
```typescript
import { describe, it, expect } from 'vitest'

describe('MyComponent', () => {
  it('renders correctly', () => {
    expect(true).toBe(true)
  })
})
```

---

## 故障排查

### 测试失败

1. 查看 GitHub Actions 日志
2. 本地复现问题
3. 修复后重新提交

### 覆盖率上传失败

1. 检查覆盖率文件路径
2. 确认 Codecov token（如果需要）
3. 检查网络问题

### 依赖安装失败

1. 清除缓存：`rm -rf node_modules && pnpm install`
2. 检查 `package.json` 和 `requirements.txt`
3. 确认版本兼容性

---

## 最佳实践

### 1. 测试命名

```python
# ✅ 好的命名
def test_init_default_config():
def test_chat_with_tool_call():

# ❌ 避免
def test_1():
def test_stuff():
```

### 2. 测试独立性

```python
# ✅ 每个测试独立
def test_a():
    setup()
    # 测试逻辑

def test_b():
    setup()  # 重新设置
    # 测试逻辑
```

### 3. 使用夹具

```python
@pytest.fixture
def sample_data():
    return {"key": "value"}

def test_with_fixture(sample_data):
    assert sample_data["key"] == "value"
```

### 4. 异步测试

```python
@pytest.mark.asyncio
async def test_async_operation():
    result = await async_function()
    assert result is not None
```

---

## 参考资源

- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [Codecov 文档](https://docs.codecov.com/)
- [pytest 文档](https://docs.pytest.org/)
- [Vitest 文档](https://vitest.dev/)

---

*最后更新：2026 年 2 月 20 日*
