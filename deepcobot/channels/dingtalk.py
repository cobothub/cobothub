"""钉钉渠道实现

使用 dingtalk-stream 库实现钉钉机器人渠道。
"""

import asyncio
import threading
from typing import TYPE_CHECKING

from loguru import logger

from deepcobot.channels.base import BaseChannel
from deepcobot.channels.events import OutboundMessage

if TYPE_CHECKING:
    from deepcobot.bus.queue import MessageBus

# 延迟导入标记
_DINGTALK_AVAILABLE = False
_CallbackHandler = object
_CallbackMessage = None
_AckMessage = None
_ChatbotMessage = None
_Credential = None
_DingTalkStreamClient = None


def _ensure_dingtalk():
    """确保 dingtalk-stream 已安装"""
    global _DINGTALK_AVAILABLE, _CallbackHandler, _CallbackMessage, _AckMessage
    global _ChatbotMessage, _Credential, _DingTalkStreamClient

    if _DINGTALK_AVAILABLE:
        return True

    try:
        from dingtalk_stream import (
            AckMessage,
            CallbackHandler,
            CallbackMessage,
            Credential,
            DingTalkStreamClient,
        )
        from dingtalk_stream.chatbot import ChatbotMessage

        _CallbackHandler = CallbackHandler
        _CallbackMessage = CallbackMessage
        _AckMessage = AckMessage
        _ChatbotMessage = ChatbotMessage
        _Credential = Credential
        _DingTalkStreamClient = DingTalkStreamClient
        _DINGTALK_AVAILABLE = True
        return True
    except ImportError:
        return False


class DingTalkChannel(BaseChannel):
    """
    钉钉渠道实现，使用 Stream 模式连接。

    特点：
    - 无需公网 IP
    - 支持 Stream 模式
    - 支持卡片消息
    - 使用独立线程运行 stream，支持优雅关闭

    Attributes:
        name: 渠道名称（"dingtalk"）
    """

    name = "dingtalk"

    def __init__(self, config, bus: "MessageBus"):
        """
        初始化钉钉渠道。

        Args:
            config: 渠道配置（包含 client_id, client_secret, allowed_users）
            bus: 消息总线
        """
        super().__init__(config, bus)
        self.client_id = getattr(config, "client_id", "")
        self.client_secret = getattr(config, "client_secret", "")
        self._client = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self._stream_thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._background_tasks: set[asyncio.Task] = set()

    async def start(self) -> None:
        """启动钉钉 Bot"""
        if not self.client_id or not self.client_secret:
            logger.error("DingTalk client_id or client_secret not configured")
            return

        if not _ensure_dingtalk():
            logger.error(
                "dingtalk-stream not installed. "
                "Install it with: pip install deepcobot[dingtalk]"
            )
            return

        self._running = True

        # 创建自定义处理器
        class CustomDingTalkHandler(_CallbackHandler):
            def __init__(self, channel):
                super().__init__()
                self.channel = channel

            async def process(self, message: _CallbackMessage):
                """处理入站消息"""
                try:
                    # 调试日志：原始消息和 topic
                    logger.info("=" * 50)
                    logger.info("DingTalk callback received!")
                    logger.info("Topic: {}", message.headers.topic if hasattr(message, 'headers') else 'N/A')
                    logger.info("Raw message data: {}", message.data)
                    logger.debug("Received raw message: {}", message.data)

                    # 使用 SDK 的 ChatbotMessage 解析消息
                    chatbot_msg = _ChatbotMessage.from_dict(message.data)

                    # 调试日志：消息类型
                    logger.info(
                        "DingTalk message received - type: {}, sender: {}",
                        chatbot_msg.message_type,
                        chatbot_msg.sender_nick or chatbot_msg.sender_id,
                    )

                    # 提取文本内容
                    content = ""
                    if chatbot_msg.text:
                        content = chatbot_msg.text.content.strip()
                    elif chatbot_msg.extensions.get("content", {}).get("recognition"):
                        content = chatbot_msg.extensions["content"]["recognition"].strip()
                    if not content:
                        content = message.data.get("text", {}).get("content", "").strip()

                    if not content:
                        logger.warning(
                            "Received empty or unsupported message type: {}",
                            chatbot_msg.message_type,
                        )
                        return _AckMessage.STATUS_OK, "OK"

                    # 提取发送者信息
                    sender_id = chatbot_msg.sender_staff_id or chatbot_msg.sender_id
                    sender_name = chatbot_msg.sender_nick or "Unknown"

                    # 提取会话信息
                    conversation_type = message.data.get("conversationType")
                    conversation_id = (
                        message.data.get("conversationId")
                        or message.data.get("openConversationId")
                    )

                    # 群聊消息需要特殊处理 chat_id
                    is_group = conversation_type == "2" and conversation_id
                    chat_id = f"group:{conversation_id}" if is_group else sender_id

                    logger.info(
                        "Received DingTalk message from {} ({}): {}",
                        sender_name,
                        sender_id,
                        content,
                    )

                    # 异步处理消息，避免阻塞
                    task = asyncio.create_task(
                        self.channel._handle_message(
                            sender_id=sender_id,
                            chat_id=chat_id,
                            content=content,
                            metadata={
                                "sender_name": sender_name,
                                "conversation_type": conversation_type,
                            },
                        )
                    )
                    self.channel._background_tasks.add(task)
                    task.add_done_callback(self.channel._background_tasks.discard)

                    return _AckMessage.STATUS_OK, "OK"

                except Exception as e:
                    logger.error("Error processing DingTalk message: {}", e)
                    return _AckMessage.STATUS_OK, "Error"

        # 创建凭证和客户端
        credential = _Credential(self.client_id, self.client_secret)
        self._client = _DingTalkStreamClient(credential)

        # 注册回调处理器
        handler = CustomDingTalkHandler(self)
        self._client.register_callback_handler(_ChatbotMessage.TOPIC, handler)

        logger.info("DingTalk client initialized")

        # 保存当前事件循环引用
        self._loop = asyncio.get_running_loop()

        # 清除停止信号
        self._stop_event.clear()

        # 在独立线程中运行 stream，支持优雅关闭
        self._stream_thread = threading.Thread(
            target=self._run_stream_forever,
            daemon=True,
        )
        self._stream_thread.start()

        logger.info("DingTalk stream thread started")

    def _run_stream_forever(self) -> None:
        """在独立线程中运行 stream 循环"""
        logger.info("DingTalk stream thread running...")
        try:
            if self._client:
                asyncio.run(self._stream_loop())
        except Exception as e:
            logger.exception("DingTalk stream thread failed: {}", e)
        finally:
            self._stop_event.set()
            logger.info("DingTalk stream thread stopped")

    async def _stream_loop(self) -> None:
        """
        驱动 DingTalkStreamClient.start() 并在 _stop_event 设置时优雅停止。

        关闭 websocket 并取消任务，避免进程退出时出现 "Task was destroyed but it is pending"。
        """
        client = self._client
        if not client:
            return

        main_task = asyncio.create_task(client.start())

        async def stop_watcher() -> None:
            """监控停止信号，触发时关闭 websocket"""
            while not self._stop_event.is_set():
                await asyncio.sleep(0.5)
            # 关闭 websocket 以中断 client.start()
            if client.websocket is not None:
                try:
                    await client.websocket.close()
                except Exception:
                    pass
            await asyncio.sleep(0.2)
            # 取消主任务
            if not main_task.done():
                main_task.cancel()

        watcher_task = asyncio.create_task(stop_watcher())

        try:
            await main_task
        except asyncio.CancelledError:
            logger.debug("DingTalk stream main task cancelled")
        except Exception as e:
            logger.warning("DingTalk stream error: {}", e)

        # 取消 watcher
        watcher_task.cancel()
        try:
            await watcher_task
        except asyncio.CancelledError:
            pass

        # 取消剩余的后台任务，确保循环干净退出
        loop = asyncio.get_running_loop()
        pending = [
            t
            for t in asyncio.all_tasks(loop)
            if t is not asyncio.current_task() and not t.done()
        ]
        for t in pending:
            t.cancel()
        if pending:
            try:
                await asyncio.wait_for(
                    asyncio.gather(*pending, return_exceptions=True),
                    timeout=4.0,
                )
            except asyncio.TimeoutError:
                pass

    async def stop(self) -> None:
        """停止钉钉 Bot"""
        logger.info("Stopping DingTalk channel...")
        self._running = False

        # 设置停止信号，触发 stop_watcher 关闭 websocket
        self._stop_event.set()

        # 等待 stream 线程结束
        if self._stream_thread and self._stream_thread.is_alive():
            self._stream_thread.join(timeout=5)
            if self._stream_thread.is_alive():
                logger.warning("DingTalk stream thread did not stop gracefully")

        # 取消后台任务
        if self._loop and not self._loop.is_closed():
            for task in self._background_tasks:
                if not task.done():
                    task.cancel()
            self._background_tasks.clear()

        self._client = None
        logger.info("DingTalk channel stopped")

    async def send(self, msg: OutboundMessage) -> None:
        """
        发送消息到钉钉。

        注意：需要通过 HTTP API 发送消息，Stream SDK 只用于接收。

        Args:
            msg: 出站消息
        """
        if not self._client:
            logger.warning("DingTalk client not initialized, cannot send message")
            return

        try:
            # 获取 access_token
            token = await self._client.get_access_token()
            if not token:
                logger.error("Failed to get DingTalk access token")
                return

            # 通过 HTTP API 发送消息
            import httpx
            import json

            headers = {"x-acs-dingtalk-access-token": token}
            chat_id = msg.chat_id

            if chat_id.startswith("group:"):
                # 群聊消息
                url = "https://api.dingtalk.com/v1.0/robot/groupMessages/send"
                payload = {
                    "robotCode": self.client_id,
                    "openConversationId": chat_id[6:],  # 移除 "group:" 前缀
                    "msgKey": "sampleMarkdown",
                    "msgParam": json.dumps({"title": "Reply", "text": msg.content}, ensure_ascii=False),
                }
            else:
                # 私聊消息
                url = "https://api.dingtalk.com/v1.0/robot/oToMessages/batchSend"
                payload = {
                    "robotCode": self.client_id,
                    "userIds": [chat_id],
                    "msgKey": "sampleMarkdown",
                    "msgParam": json.dumps({"title": "Reply", "text": msg.content}, ensure_ascii=False),
                }

            async with httpx.AsyncClient() as client:
                resp = await client.post(url, json=payload, headers=headers)
                if resp.status_code != 200:
                    logger.error("DingTalk send failed: status={}, body={}", resp.status_code, resp.text[:500])
                else:
                    logger.debug("DingTalk message sent to {}", chat_id)

        except Exception as e:
            logger.error("Error sending DingTalk message: {}", e)

    async def send_progress(self, chat_id: str, content: str) -> None:
        """
        发送进度更新。

        钉钉不支持"正在输入"状态。

        Args:
            chat_id: 会话 ID
            content: 进度内容
        """
        # 钉钉不支持输入状态
        pass