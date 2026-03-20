"""Cron 服务

定时任务调度和执行。

与 HeartbeatService 类似，作为消息触发源，通过 on_execute 回调调用 Agent，
结果通过 MessageBus 投递到配置的渠道。

服务通过轮询检测存储文件变更，感知 CLI 命令的操作。
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Coroutine

from loguru import logger

from deepcobot.cron.store import CronStore
from deepcobot.cron.types import compute_next_run

if TYPE_CHECKING:
    from deepcobot.bus.queue import MessageBus


class CronService:
    """
    定时任务调度服务。

    负责：
    1. 定时触发任务执行
    2. 检测存储文件变更（感知 CLI 操作）
    3. 通过回调执行任务并投递结果

    Attributes:
        store: 任务存储
        bus: 消息总线
        on_execute: 任务执行回调函数
    """

    # 文件变更检测间隔（秒）
    FILE_CHECK_INTERVAL = 5.0

    def __init__(
        self,
        store_path: Path,
        bus: "MessageBus | None" = None,
        on_execute: Callable[[str, str, str], Coroutine[Any, Any, str]] | None = None,
    ):
        """
        初始化 Cron 服务。

        Args:
            store_path: 任务存储文件路径
            bus: 消息总线（可选，用于结果投递）
            on_execute: 任务执行回调，接收 (message, session_key, channel) 返回响应
        """
        self.store = CronStore(store_path)
        self.bus = bus
        self.on_execute = on_execute
        self._timer_task: asyncio.Task | None = None
        self._file_check_task: asyncio.Task | None = None
        self._running = False
        self._last_mtime: float | None = None

    async def start(self) -> None:
        """启动定时任务服务"""
        self._running = True

        # 计算所有启用任务的下次执行时间
        now = datetime.now()
        for job in self.store.get_all_jobs_ref():
            if job.enabled and not job.next_run_at:
                job.next_run_at = compute_next_run(job.schedule, now)
        self.store._save_jobs()

        # 记录文件修改时间
        self._last_mtime = self.store.get_mtime()

        # 启动定时器和文件检测
        self._arm_timer()
        self._start_file_check()

        logger.info(f"Cron service started with {len(self.store.list_jobs())} jobs")

    async def stop(self) -> None:
        """停止定时任务服务"""
        self._running = False

        if self._timer_task:
            self._timer_task.cancel()
            try:
                await self._timer_task
            except asyncio.CancelledError:
                pass
            self._timer_task = None

        if self._file_check_task:
            self._file_check_task.cancel()
            try:
                await self._file_check_task
            except asyncio.CancelledError:
                pass
            self._file_check_task = None

        logger.info("Cron service stopped")

    def _start_file_check(self) -> None:
        """启动文件变更检测"""

        async def check_loop():
            while self._running:
                await asyncio.sleep(self.FILE_CHECK_INTERVAL)
                if not self._running:
                    break

                try:
                    current_mtime = self.store.get_mtime()
                    if current_mtime and current_mtime != self._last_mtime:
                        logger.info("Cron: detected store file change, reloading...")
                        self.store.reload()
                        self._last_mtime = current_mtime
                        self._arm_timer()
                except Exception as e:
                    logger.warning(f"Cron: file check error: {e}")

        self._file_check_task = asyncio.create_task(check_loop())

    def _get_next_wake_time(self) -> datetime | None:
        """获取最近的执行时间"""
        times = [
            j.next_run_at
            for j in self.store.get_all_jobs_ref()
            if j.enabled and j.next_run_at
        ]
        return min(times) if times else None

    def _arm_timer(self) -> None:
        """设置下次执行的定时器"""
        if self._timer_task:
            self._timer_task.cancel()
            self._timer_task = None

        if not self._running:
            return

        next_wake = self._get_next_wake_time()
        if not next_wake:
            return

        now = datetime.now()
        if next_wake <= now:
            delay = 0
        else:
            delay = (next_wake - now).total_seconds()

        async def tick():
            await asyncio.sleep(delay)
            if self._running:
                await self._on_timer()

        self._timer_task = asyncio.create_task(tick())

    async def _on_timer(self) -> None:
        """定时器触发，执行到期的任务"""
        now = datetime.now()
        due_jobs = [
            j for j in self.store.get_all_jobs_ref()
            if j.enabled and j.next_run_at and now >= j.next_run_at
        ]

        for job in due_jobs:
            asyncio.create_task(self._execute_job(job))

        self._arm_timer()

    async def _execute_job(self, job) -> None:
        """执行单个任务"""
        from deepcobot.cron.types import CronJob
        assert isinstance(job, CronJob)

        logger.info(f"Cron: executing job '{job.name}' ({job.id})")

        try:
            if self.on_execute:
                session_key = f"cron:{job.id}"
                channel = job.channel or "cron"

                response = await asyncio.wait_for(
                    self.on_execute(job.message, session_key, channel),
                    timeout=job.timeout,
                )

                # 如果有响应且配置了投递目标，通过 MessageBus 投递
                if response and self.bus and job.channel and job.chat_id:
                    from deepcobot.channels.events import OutboundMessage
                    await self.bus.publish_outbound(OutboundMessage(
                        channel=job.channel,
                        chat_id=job.chat_id,
                        content=response,
                    ))
                    logger.info(f"Cron: job '{job.name}' completed, dispatched to {job.channel}:{job.chat_id}")
                else:
                    logger.info(f"Cron: job '{job.name}' completed (no dispatch)")

                # 更新任务状态
                job.last_status = "ok"
                job.last_error = None
            else:
                logger.warning(f"Cron: no on_execute callback for job '{job.name}'")
                job.last_status = "error"
                job.last_error = "No execution callback"

        except asyncio.TimeoutError:
            logger.warning(f"Cron: job '{job.name}' timed out after {job.timeout}s")
            job.last_status = "error"
            job.last_error = f"Timeout after {job.timeout}s"
        except Exception as e:
            logger.error(f"Cron: job '{job.name}' failed: {e}")
            job.last_status = "error"
            job.last_error = str(e)

        job.last_run_at = datetime.now()
        job.next_run_at = compute_next_run(job.schedule, datetime.now())

        # 更新存储
        self.store.update_job_status(
            job.id,
            last_status=job.last_status,
            last_error=job.last_error,
            last_run_at=job.last_run_at,
            next_run_at=job.next_run_at,
        )
        self._last_mtime = self.store.get_mtime()

    # ========== 公共 API（委托给 store）==========

    def list_jobs(self, include_disabled: bool = False):
        """列出所有任务"""
        return self.store.list_jobs(include_disabled)

    def get_job(self, job_id: str):
        """获取指定任务"""
        return self.store.get_job(job_id)

    def status(self) -> dict:
        """获取服务状态"""
        jobs = self.store.list_jobs(include_disabled=True)
        return {
            "running": self._running,
            "jobs": len(jobs),
            "enabled_jobs": len([j for j in jobs if j.enabled]),
            "next_wake": self._get_next_wake_time().isoformat() if self._get_next_wake_time() else None,
            "store_path": str(self.store.store_path),
        }