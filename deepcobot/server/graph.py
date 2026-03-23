"""LangGraph Graph 导出模块

导出 Agent graph 供 LangGraph 服务器使用。

LangGraph CLI 支持两种导出方式：
1. graph 变量直接是 StateGraph 实例
2. graph 变量是返回 StateGraph 的工厂函数（支持 async）
"""

from typing import Any

from loguru import logger

from deepcobot.config import Config, load_config, get_langfuse_handler


async def create_graph_async(config: Config | None = None) -> Any:
    """
    异步创建并导出 LangGraph graph。

    Args:
        config: 配置对象，如果未提供则加载默认配置

    Returns:
        LangGraph graph 对象
    """
    if config is None:
        config = load_config()

    from deepcobot.agent.factory import create_agent_async

    agent_resources = await create_agent_async(config)

    # 初始化 Langfuse handler（如果启用）
    # 这会在 graph 创建时初始化，环境变量会被设置
    handler = get_langfuse_handler(config)
    if handler:
        logger.info("Langfuse CallbackHandler initialized for LangGraph Server")

    return agent_resources["graph"]


# 默认 graph 实例（用于 langgraph.json 配置）
_default_graph = None
_default_config = None
_langfuse_handler = None


async def get_graph_async() -> Any:
    """
    异步获取默认 graph 实例。

    Returns:
        LangGraph graph 对象
    """
    global _default_graph, _default_config, _langfuse_handler

    if _default_graph is None:
        _default_config = load_config()
        _default_graph = await create_graph_async(_default_config)
        # 获取 Langfuse handler（如果启用）
        _langfuse_handler = get_langfuse_handler(_default_config)

    return _default_graph


def get_default_config() -> Config | None:
    """获取默认配置（用于 LangGraph Server 模式获取 Langfuse handler）"""
    return _default_config


def get_server_callbacks() -> list[Any]:
    """
    获取 LangGraph Server 的 callbacks 列表。

    在 LangGraph Server 模式下，需要在每次调用时传入此列表。
    返回包含 Langfuse CallbackHandler 的列表（如果启用）。

    Usage:
        # LangGraph Server API 调用时
        config = {
            "configurable": {"thread_id": "xxx"},
            "callbacks": get_server_callbacks()
        }
        result = await graph.ainvoke(input, config=config)

    Returns:
        callbacks 列表，如果没有启用的 callbacks 则返回空列表
    """
    global _langfuse_handler

    # 确保已初始化
    if _default_graph is None:
        import asyncio
        asyncio.get_event_loop().run_until_complete(get_graph_async())

    callbacks = []
    if _langfuse_handler is not None:
        callbacks.append(_langfuse_handler)

    return callbacks


# LangGraph 异步工厂函数
# LangGraph CLI 会调用这个函数来获取 graph
async def graph(config: dict | None = None) -> Any:
    """
    LangGraph 异步工厂函数，返回编译后的 graph。

    LangGraph CLI 期望 graph 是一个 StateGraph 实例或返回 StateGraph 的函数。
    支持异步函数以避免阻塞调用。

    Args:
        config: 可选配置字典（LangGraph 运行时可能传入）

    Returns:
        编译后的 LangGraph StateGraph
    """
    return await get_graph_async()