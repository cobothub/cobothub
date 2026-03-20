"""Cron 任务存储

只负责任务的持久化操作，不涉及调度逻辑。
CLI 命令直接操作此存储，调度服务通过 watch 或轮询感知变化。
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from loguru import logger

from deepcobot.cron.types import (
    CronJob,
    compute_next_run,
)


class CronStore:
    """
    定时任务存储。

    只负责任务的 CRUD 操作和文件持久化。
    调度逻辑由 CronService 处理。

    Attributes:
        store_path: 任务存储文件路径
    """

    def __init__(self, store_path: Path | str):
        """
        初始化存储。

        Args:
            store_path: 任务存储文件路径
        """
        self.store_path = Path(store_path).expanduser()
        self._jobs: list[CronJob] = []
        self._load_jobs()

    def _load_jobs(self) -> None:
        """从文件加载任务"""
        if not self.store_path.exists():
            self._jobs = []
            return

        try:
            data = json.loads(self.store_path.read_text(encoding="utf-8"))
            jobs_data = data.get("jobs", [])
            self._jobs = [CronJob.from_dict(j) for j in jobs_data]
            logger.debug(f"CronStore: loaded {len(self._jobs)} jobs from {self.store_path}")
        except Exception as e:
            logger.warning(f"CronStore: failed to load from {self.store_path}: {e}")
            self._jobs = []

    def _save_jobs(self) -> None:
        """保存任务到文件"""
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "version": 1,
            "updated_at": datetime.now().isoformat(),
            "jobs": [j.to_dict() for j in self._jobs],
        }
        self.store_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        logger.debug(f"CronStore: saved {len(self._jobs)} jobs to {self.store_path}")

    def reload(self) -> None:
        """重新从文件加载（用于感知外部修改）"""
        self._load_jobs()

    def get_mtime(self) -> float | None:
        """获取文件最后修改时间"""
        if self.store_path.exists():
            return self.store_path.stat().st_mtime
        return None

    # ========== 查询操作 ==========

    def list_jobs(self, include_disabled: bool = False) -> list[CronJob]:
        """
        列出所有任务。

        Args:
            include_disabled: 是否包含禁用的任务

        Returns:
            任务列表
        """
        jobs = self._jobs if include_disabled else [j for j in self._jobs if j.enabled]
        return sorted(jobs, key=lambda j: j.next_run_at or datetime.max)

    def get_job(self, job_id: str) -> CronJob | None:
        """
        获取指定任务。

        Args:
            job_id: 任务 ID

        Returns:
            任务对象或 None
        """
        for job in self._jobs:
            if job.id == job_id:
                return job
        return None

    # ========== 写入操作 ==========

    def add_job(
        self,
        name: str,
        schedule: str,
        message: str,
        channel: str | None = None,
        chat_id: str | None = None,
        timeout: int = 120,
        enabled: bool = True,
    ) -> CronJob:
        """
        添加新任务。

        Args:
            name: 任务名称
            schedule: 调度表达式（cron 或 every 间隔）
            message: 发送给 Agent 的消息
            channel: 结果发送渠道
            chat_id: 结果发送目标
            timeout: 执行超时（秒）
            enabled: 是否启用

        Returns:
            新创建的任务
        """
        now = datetime.now()

        job = CronJob(
            id=str(uuid.uuid4())[:8],
            name=name,
            enabled=enabled,
            schedule=schedule,
            message=message,
            channel=channel,
            chat_id=chat_id,
            timeout=timeout,
            next_run_at=compute_next_run(schedule, now) if enabled else None,
        )

        self._jobs.append(job)
        self._save_jobs()

        logger.info(f"CronStore: added job '{name}' ({job.id})")
        return job

    def update_job(
        self,
        job_id: str,
        name: str | None = None,
        schedule: str | None = None,
        message: str | None = None,
        channel: str | None = None,
        chat_id: str | None = None,
        timeout: int | None = None,
    ) -> CronJob | None:
        """
        更新任务。

        Args:
            job_id: 任务 ID
            name: 新名称
            schedule: 新调度
            message: 新消息
            channel: 新渠道
            chat_id: 新目标
            timeout: 新超时

        Returns:
            更新后的任务或 None
        """
        job = self.get_job(job_id)
        if not job:
            return None

        if name is not None:
            job.name = name
        if schedule is not None:
            job.schedule = schedule
            job.next_run_at = compute_next_run(schedule, datetime.now()) if job.enabled else None
        if message is not None:
            job.message = message
        if channel is not None:
            job.channel = channel
        if chat_id is not None:
            job.chat_id = chat_id
        if timeout is not None:
            job.timeout = timeout

        self._save_jobs()

        logger.info(f"CronStore: updated job '{job.name}' ({job.id})")
        return job

    def remove_job(self, job_id: str) -> bool:
        """
        移除任务。

        Args:
            job_id: 任务 ID

        Returns:
            是否成功移除
        """
        before = len(self._jobs)
        self._jobs = [j for j in self._jobs if j.id != job_id]
        removed = len(self._jobs) < before

        if removed:
            self._save_jobs()
            logger.info(f"CronStore: removed job {job_id}")

        return removed

    def enable_job(self, job_id: str) -> bool:
        """启用任务"""
        job = self.get_job(job_id)
        if not job:
            return False

        job.enabled = True
        job.next_run_at = compute_next_run(job.schedule, datetime.now())
        self._save_jobs()

        logger.info(f"CronStore: enabled job '{job.name}' ({job.id})")
        return True

    def disable_job(self, job_id: str) -> bool:
        """禁用任务"""
        job = self.get_job(job_id)
        if not job:
            return False

        job.enabled = False
        job.next_run_at = None
        self._save_jobs()

        logger.info(f"CronStore: disabled job '{job.name}' ({job.id})")
        return True

    def trigger_now(self, job_id: str) -> bool:
        """
        标记任务立即执行。

        设置 next_run_at 为当前时间（或稍早），调度服务会立即执行。

        Args:
            job_id: 任务 ID

        Returns:
            是否成功
        """
        job = self.get_job(job_id)
        if not job:
            return False

        job.next_run_at = datetime.now()
        self._save_jobs()

        logger.info(f"CronStore: marked job '{job.name}' ({job.id}) for immediate execution")
        return True

    def update_job_status(
        self,
        job_id: str,
        last_status: str | None = None,
        last_error: str | None = None,
        last_run_at: datetime | None = None,
        next_run_at: datetime | None = None,
    ) -> bool:
        """
        更新任务执行状态（由 CronService 调用）。

        Args:
            job_id: 任务 ID
            last_status: 上次执行状态
            last_error: 上次执行错误
            last_run_at: 上次执行时间
            next_run_at: 下次执行时间

        Returns:
            是否成功
        """
        job = self.get_job(job_id)
        if not job:
            return False

        if last_status is not None:
            job.last_status = last_status
        if last_error is not None:
            job.last_error = last_error
        if last_run_at is not None:
            job.last_run_at = last_run_at
        if next_run_at is not None:
            job.next_run_at = next_run_at

        self._save_jobs()
        return True

    def get_all_jobs_ref(self) -> list[CronJob]:
        """获取任务列表的引用（用于 CronService）"""
        return self._jobs