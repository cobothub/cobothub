"""
DeepCoBot - 极简封装的个人 AI 助理框架

基于 DeepAgents SDK 构建，提供配置驱动和多渠道接入能力。
"""

import json
import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from deepcobot.config import Config

__version__ = "0.1.0"

# 配置日志（默认从环境变量读取）
log_level = os.environ.get("DEEPCOBOT_LOG_LEVEL", "INFO").upper()
json_format = os.environ.get("DEEPCOBOT_LOG_JSON", "false").lower() == "true"
log_file = os.environ.get("DEEPCOBOT_LOG_FILE", "")

# 移除默认处理器
logger.remove()

# 根据配置选择格式
_setup_complete = False


def _setup_logging(
    level: str = "INFO",
    json_output: bool = False,
    file_path: str | Path | None = None,
) -> None:
    """
    设置日志处理器。

    Args:
        level: 日志级别
        json_output: 是否输出 JSON 格式
        file_path: 日志文件路径
    """
    global _setup_complete

    # 移除现有处理器
    logger.remove()

    if json_output:
        # JSON 格式日志（生产环境）
        def json_sink(message):
            record = message.record
            log_entry = {
                "timestamp": record["time"].isoformat(),
                "level": record["level"].name,
                "message": record["message"],
                "module": record["module"],
                "function": record["function"],
                "line": record["line"],
            }
            if record.get("extra"):
                log_entry["extra"] = record["extra"]
            print(json.dumps(log_entry), file=sys.stderr)

        logger.add(
            json_sink,
            level=level,
            format="{message}",
        )
    else:
        # 人类可读格式（开发环境）
        logger.add(
            sys.stderr,
            level=level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        )

    # 日志文件（如果配置）
    if file_path:
        path = str(file_path)
        if path.startswith("~"):
            path = os.path.expanduser(path)
        logger.add(
            path,
            level=level,
            rotation="10 MB",
            retention="7 days",
            compression="gz",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        )

    _setup_complete = True


def apply_config(config: "Config") -> None:
    """
    应用配置到运行时环境。

    包括日志配置和 LangSmith 配置。

    Args:
        config: 配置对象
    """
    global log_level, json_format, log_file

    # 应用日志配置
    log_level = config.logging.level.upper()
    json_format = config.logging.json_format
    log_file = str(config.logging.file) if config.logging.file else ""

    _setup_logging(
        level=log_level,
        json_output=json_format,
        file_path=log_file or None,
    )

    # 应用 LangSmith 配置
    if config.langsmith.enabled:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        if config.langsmith.api_key:
            os.environ["LANGSMITH_API_KEY"] = config.langsmith.api_key
        if config.langsmith.project:
            os.environ["LANGCHAIN_PROJECT"] = config.langsmith.project

    logger.info(f"DeepCoBot v{__version__} initialized")
    if log_file:
        logger.info(f"Logging to file: {log_file}")


def configure_logging(
    level: str | None = None,
    json_output: bool | None = None,
    file_path: str | None = None,
) -> None:
    """
    手动配置日志输出。

    Args:
        level: 日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL）
        json_output: 是否输出 JSON 格式
        file_path: 日志文件路径
    """
    global log_level, json_format, log_file

    if level:
        log_level = level.upper()
    if json_output is not None:
        json_format = json_output
    if file_path:
        log_file = file_path

    _setup_logging(
        level=log_level,
        json_output=json_format,
        file_path=log_file or None,
    )


# 初始化默认日志
_setup_logging(
    level=log_level,
    json_output=json_format,
    file_path=log_file or None,
)


__all__ = ["__version__", "logger", "configure_logging", "apply_config"]