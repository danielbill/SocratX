"""Logger 测试"""
import pytest
from pathlib import Path
import logging

from utils.logger import SocratXLogger, logger


class TestSocratXLogger:
    """SocratXLogger 测试"""

    def test_singleton(self):
        """测试单例模式"""
        logger1 = SocratXLogger()
        logger2 = SocratXLogger()
        assert logger1 is logger2

    def test_system_log(self, tmp_path, monkeypatch):
        """测试系统日志"""
        # 临时修改日志目录
        test_log_dir = tmp_path / "logs"
        test_log_dir.mkdir()
        
        test_logger = SocratXLogger()
        # 重新配置 handler 到测试目录
        test_logger._system_logger.handlers.clear()
        handler = logging.FileHandler(test_log_dir / "SocratX.log", encoding="utf-8")
        test_logger._system_logger.addHandler(handler)
        
        test_logger.system("Test system message")
        
        log_file = test_log_dir / "SocratX.log"
        assert log_file.exists()
        content = log_file.read_text(encoding='utf-8')
        assert "Test system message" in content

    def test_conversation_log(self, tmp_path):
        """测试对话日志"""
        test_logger = SocratXLogger()
        test_logger._conversation_logger.handlers.clear()
        
        log_file = tmp_path / "conversation.log"
        handler = logging.FileHandler(log_file, encoding='utf-8')
        formatter = logging.Formatter(
            "[%(asctime)s] [SESSION:%(sessionid)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        test_logger._conversation_logger.addHandler(handler)
        
        test_logger.conversation("session-123", "USER", "Hello")
        
        assert log_file.exists()
        content = log_file.read_text(encoding='utf-8')
        assert "[SESSION:session-123]" in content
        assert "[USER]" in content
        assert "Hello" in content

    def test_ai_request_log(self, tmp_path):
        """测试 AI 请求日志"""
        test_logger = SocratXLogger()
        test_logger._ai_logger.handlers.clear()
        
        log_file = tmp_path / "ai.log"
        handler = logging.FileHandler(log_file, encoding='utf-8')
        test_logger._ai_logger.addHandler(handler)
        
        messages = [
            {"role": "user", "content": "Hello"}
        ]
        test_logger.ai_request("anthropic/claude-3-5-sonnet", messages)
        
        assert log_file.exists()
        content = log_file.read_text(encoding='utf-8')
        assert "[REQUEST]" in content
        assert "anthropic/claude-3-5-sonnet" in content

    def test_ai_response_log(self, tmp_path):
        """测试 AI 响应日志"""
        test_logger = SocratXLogger()
        test_logger._ai_logger.handlers.clear()
        
        log_file = tmp_path / "ai.log"
        handler = logging.FileHandler(log_file, encoding='utf-8')
        test_logger._ai_logger.addHandler(handler)
        
        test_logger.ai_response("Hello! How can I help you?", {"prompt_tokens": 10, "completion_tokens": 20})
        
        assert log_file.exists()
        content = log_file.read_text(encoding='utf-8')
        assert "[RESPONSE]" in content
        assert "Usage:" in content

    def test_error_log(self, tmp_path):
        """测试错误日志"""
        test_logger = SocratXLogger()
        test_logger._system_logger.handlers.clear()
        
        log_file = tmp_path / "SocratX.log"
        handler = logging.FileHandler(log_file, encoding='utf-8')
        test_logger._system_logger.addHandler(handler)
        
        try:
            raise ValueError("Test error")
        except ValueError as e:
            test_logger.error("Something went wrong", exc=e)
        
        assert log_file.exists()
        content = log_file.read_text(encoding='utf-8')
        assert "Something went wrong" in content
        assert "ValueError" in content


class TestLoggerIntegration:
    """Logger 集成测试"""

    def test_logger_in_main_dir(self):
        """测试日志文件在根目录 logs/"""
        log_dir = Path(__file__).parent.parent.parent / "logs"
        
        assert log_dir.exists()
        assert (log_dir / "SocratX.log").exists()
        assert (log_dir / "conversation.log").exists()
        assert (log_dir / "ai.log").exists()

    def test_logger_format(self):
        """测试日志格式"""
        # 验证日志文件格式正确
        log_dir = Path(__file__).parent.parent.parent / "logs"
        log_file = log_dir / "conversation.log"
        
        if log_file.exists():
            content = log_file.read_text(encoding='utf-8')
            # 验证格式：[timestamp] [SESSION:id] [role] content
            assert "[SESSION:" in content or len(content) == 0
