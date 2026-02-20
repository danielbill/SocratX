"""记忆系统测试"""
import pytest
from pathlib import Path
from agent.memory import MemoryStore, create_memory_store


class TestMemoryStore:
    """MemoryStore 测试"""

    @pytest.fixture
    def memory_store(self, tmp_path) -> MemoryStore:
        """创建测试用的 MemoryStore"""
        return MemoryStore(tmp_path)

    def test_init_creates_files(self, tmp_path):
        """测试初始化时创建文件"""
        store = MemoryStore(tmp_path)
        
        assert store.memory_file.exists()
        assert store.history_file.exists()

    def test_get_memory_initial_content(self, memory_store: MemoryStore):
        """测试获取初始记忆内容"""
        import asyncio
        content = asyncio.run(memory_store.get_memory())
        
        assert "# SocratX 记忆" in content
        assert "## 用户信息" in content
        assert "## 重要知识" in content

    def test_update_memory_append(self, memory_store: MemoryStore):
        """测试追加记忆"""
        import asyncio
        asyncio.run(memory_store.update_memory("Test memory item"))
        
        content = asyncio.run(memory_store.get_memory())
        assert "Test memory item" in content

    def test_update_memory_with_section(self, memory_store: MemoryStore):
        """测试更新特定章节"""
        import asyncio
        asyncio.run(memory_store.update_memory("New user info", section="用户信息"))
        
        content = asyncio.run(memory_store.get_memory())
        assert "## 用户信息" in content
        assert "New user info" in content

    def test_append_to_history(self, memory_store: MemoryStore):
        """测试追加对话历史"""
        import asyncio
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]
        asyncio.run(memory_store.append_to_history(messages))
        
        content = memory_store.history_file.read_text(encoding="utf-8")
        assert "Hello" in content
        assert "Hi there!" in content

    def test_search_history(self, memory_store: MemoryStore):
        """测试搜索历史"""
        import asyncio
        # 先添加一些历�?
        messages = [
            {"role": "user", "content": "Python is great"},
            {"role": "assistant", "content": "Yes, Python is awesome"},
        ]
        asyncio.run(memory_store.append_to_history(messages))
        
        # 搜索
        results = asyncio.run(memory_store.search_history("Python"))
        assert len(results) > 0
        assert any("Python" in r for r in results)

    def test_search_history_limit(self, memory_store: MemoryStore):
        """测试搜索历史限制"""
        import asyncio
        # 添加多条历史
        for i in range(20):
            messages = [
                {"role": "user", "content": f"Message {i}"},
            ]
            asyncio.run(memory_store.append_to_history(messages))
        
        results = asyncio.run(memory_store.search_history("Message", limit=5))
        assert len(results) <= 5

    def test_get_recent_history(self, memory_store: MemoryStore):
        """测试获取最近历�?""
        import asyncio
        # 添加多条历史
        for i in range(10):
            messages = [
                {"role": "user", "content": f"Recent message {i}"},
            ]
            asyncio.run(memory_store.append_to_history(messages))
        
        recent = asyncio.run(memory_store.get_recent_history(count=5))
        assert len(recent) <= 5

    def test_clear_memory(self, memory_store: MemoryStore):
        """测试清空记忆"""
        import asyncio
        # 先添加内�?
        asyncio.run(memory_store.update_memory("Test item"))
        
        # 清空
        memory_store.clear_memory()
        
        content = asyncio.run(memory_store.get_memory())
        assert "Test item" not in content
        assert "# SocratX 记忆" in content

    def test_clear_history(self, memory_store: MemoryStore):
        """测试清空历史"""
        import asyncio
        # 先添加历�?
        messages = [{"role": "user", "content": "Test"}]
        asyncio.run(memory_store.append_to_history(messages))
        
        # 清空
        memory_store.clear_history()
        
        content = memory_store.history_file.read_text(encoding="utf-8")
        assert "Test" not in content

    def test_get_stats(self, memory_store: MemoryStore):
        """测试获取统计信息"""
        stats = memory_store.get_stats()
        
        assert "memory_file" in stats
        assert "history_file" in stats
        assert "memory_size" in stats
        assert "history_size" in stats

    def test_get_stats_after_update(self, memory_store: MemoryStore):
        """测试更新后的统计"""
        import asyncio
        initial_stats = memory_store.get_stats()
        
        # 添加内容
        asyncio.run(memory_store.update_memory("New item"))
        
        new_stats = memory_store.get_stats()
        assert new_stats["memory_size"] > initial_stats["memory_size"]


class TestCreateMemoryStore:
    """create_memory_store 测试"""

    @pytest.mark.asyncio
    async def test_create_memory_store_default(self, tmp_path):
        """测试创建默认 MemoryStore"""
        store = await create_memory_store(str(tmp_path))
        
        assert isinstance(store, MemoryStore)
        assert store.workspace == tmp_path

    @pytest.mark.asyncio
    async def test_create_memory_store_empty_path(self, tmp_path, monkeypatch):
        """测试使用空路径（使用当前目录�?""
        monkeypatch.chdir(tmp_path)
        store = await create_memory_store("")
        
        assert isinstance(store, MemoryStore)
