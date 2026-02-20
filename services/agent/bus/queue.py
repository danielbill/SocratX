"""
Message Bus Queue - 消息总线队列

参考: nanobot/nanobot/bus/queue.py
异步消息队列，用于解耦消息生产者和消费者
"""

import asyncio
from typing import Callable, Optional, Any
from collections import deque
from .events import InboundMessage, OutboundMessage


class MessageBus:
    """
    消息总线

    提供异步队列用于解耦入站和出站消息
    """

    def __init__(self, max_size: int = 1000):
        """
        初始化消息总线

        Args:
            max_size: 队列最大大小
        """
        self._inbound_queue: asyncio.Queue[InboundMessage] = asyncio.Queue(maxsize=max_size)
        self._outbound_queue: asyncio.Queue[OutboundMessage] = asyncio.Queue(maxsize=max_size)

        # 订阅者
        self._inbound_subscribers: list[Callable] = []
        self._outbound_subscribers: list[Callable] = []

        # 运行状态
        self._running = False
        self._tasks: list[asyncio.Task] = []

    async def publish_inbound(self, message: InboundMessage) -> None:
        """
        发布入站消息

        Args:
            message: 入站消息
        """
        await self._inbound_queue.put(message)

    async def publish_outbound(self, message: OutboundMessage) -> None:
        """
        发布出站消息

        Args:
            message: 出站消息
        """
        await self._outbound_queue.put(message)

    async def consume_inbound(self) -> InboundMessage:
        """
        消费入站消息

        Returns:
            入站消息
        """
        return await self._inbound_queue.get()

    async def consume_outbound(self) -> OutboundMessage:
        """
        消费出站消息

        Returns:
            出站消息
        """
        return await self._outbound_queue.get()

    def subscribe_inbound(self, callback: Callable[[InboundMessage], Any]) -> None:
        """
        订阅入站消息

        Args:
            callback: 回调函数
        """
        self._inbound_subscribers.append(callback)

    def subscribe_outbound(self, callback: Callable[[OutboundMessage], Any]) -> None:
        """
        订阅出站消息

        Args:
            callback: 回调函数
        """
        self._outbound_subscribers.append(callback)

    async def _dispatch_inbound(self, message: InboundMessage) -> None:
        """
        分发入站消息给订阅者

        Args:
            message: 入站消息
        """
        for callback in self._inbound_subscribers:
            try:
                result = callback(message)
                if asyncio.iscoroutine(result):
                    await result
            except Exception as e:
                print(f"Error in inbound subscriber: {e}")

    async def _dispatch_outbound(self, message: OutboundMessage) -> None:
        """
        分发出站消息给订阅者

        Args:
            message: 出站消息
        """
        for callback in self._outbound_subscribers:
            try:
                result = callback(message)
                if asyncio.iscoroutine(result):
                    await result
            except Exception as e:
                print(f"Error in outbound subscriber: {e}")

    async def start(self) -> None:
        """启动消息总线"""
        if self._running:
            return

        self._running = True

        # 启动分发任务
        self._tasks.append(asyncio.create_task(self._inbound_dispatcher()))
        self._tasks.append(asyncio.create_task(self._outbound_dispatcher()))

    async def stop(self) -> None:
        """停止消息总线"""
        self._running = False

        # 取消所有任务
        for task in self._tasks:
            task.cancel()

        # 等待任务完成
        await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()

    async def _inbound_dispatcher(self) -> None:
        """入站消息分发器"""
        while self._running:
            try:
                message = await asyncio.wait_for(self.consume_inbound(), timeout=1.0)
                await self._dispatch_inbound(message)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"Error in inbound dispatcher: {e}")

    async def _outbound_dispatcher(self) -> None:
        """出站消息分发器"""
        while self._running:
            try:
                message = await asyncio.wait_for(self.consume_outbound(), timeout=1.0)
                await self._dispatch_outbound(message)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"Error in outbound dispatcher: {e}")

    def get_stats(self) -> dict:
        """获取统计信息"""
        return {
            "inbound_queue_size": self._inbound_queue.qsize(),
            "outbound_queue_size": self._outbound_queue.qsize(),
            "inbound_subscribers": len(self._inbound_subscribers),
            "outbound_subscribers": len(self._outbound_subscribers),
            "running": self._running,
        }

    def clear(self) -> None:
        """清空队列"""
        while not self._inbound_queue.empty():
            try:
                self._inbound_queue.get_nowait()
            except asyncio.QueueEmpty:
                break

        while not self._outbound_queue.empty():
            try:
                self._outbound_queue.get_nowait()
            except asyncio.QueueEmpty:
                break


# 全局消息总线实例
_global_bus: Optional[MessageBus] = None


def get_message_bus() -> MessageBus:
    """
    获取全局消息总线

    Returns:
        MessageBus 实例
    """
    global _global_bus
    if _global_bus is None:
        _global_bus = MessageBus()
    return _global_bus
