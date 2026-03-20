"""Cron commands - Manage scheduled tasks.

这些命令只操作任务存储文件，不会启动调度服务。
调度服务应在 bot 或 serve 模式下运行。
"""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from deepcobot import apply_config
from deepcobot.config import load_config
from deepcobot.cron import CronStore
from deepcobot.cli.i18n import t
from deepcobot.cli.context import setup_language

console = Console()

# Create cron subcommand group
cron_app = typer.Typer(
    name="cron",
    help="Manage scheduled tasks (store operations, service runs in bot/serve mode)",
)


@cron_app.command("list")
def cron_list(
    config: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Config file",
    ),
    all: bool = typer.Option(
        False,
        "--all",
        "-a",
        help="Show all (including disabled)",
    ),
) -> None:
    """List all scheduled tasks.

    Note: This reads from the task store file. The scheduler service
    should be running via 'deepcobot bot' or 'deepcobot serve'.
    """
    lang = setup_language(config)

    cfg = load_config(config)
    apply_config(cfg)

    store = CronStore(cfg.cron.store_path)
    jobs = store.list_jobs(include_disabled=all)

    if not jobs:
        console.print(f"[yellow]{t('cron.no_jobs', lang)}[/yellow]")
        return

    table = Table(title="Cron Jobs")
    table.add_column(t("cron.table_id", lang), style="cyan")
    table.add_column(t("cron.table_name", lang), style="green")
    table.add_column(t("cron.table_schedule", lang), style="yellow")
    table.add_column(t("cron.table_status", lang), style="magenta")
    table.add_column(t("cron.table_next_run", lang), style="blue")

    for job in jobs:
        status = f"[green]{t('cron.enabled', lang)}[/green]" if job.enabled else f"[red]{t('cron.disabled', lang)}[/red]"
        next_run = "-"
        if job.next_run_at:
            next_run = job.next_run_at.strftime("%Y-%m-%d %H:%M:%S")

        table.add_row(job.id, job.name, job.schedule, status, next_run)

    console.print(table)


@cron_app.command("add")
def cron_add(
    name: str = typer.Argument(..., help="Task name"),
    message: str = typer.Argument(..., help="Message to send to agent"),
    every: Optional[str] = typer.Option(
        None,
        "--every",
        "-e",
        help="Interval (e.g., 30s, 5m, 1h, 1d, 2h30m)",
    ),
    cron: Optional[str] = typer.Option(
        None,
        "--cron",
        help="Cron expression (5 fields: minute hour day month weekday)",
    ),
    channel: Optional[str] = typer.Option(
        None,
        "--channel",
        help="Channel to dispatch results (e.g., telegram, discord)",
    ),
    chat_id: Optional[str] = typer.Option(
        None,
        "--chat-id",
        help="Chat ID to dispatch results",
    ),
    timeout: int = typer.Option(
        120,
        "--timeout",
        "-t",
        help="Execution timeout in seconds",
    ),
    config: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Config file",
    ),
) -> None:
    """Add a scheduled task.

    The task will be saved to the store file. If the scheduler service
    is running (via 'deepcobot bot'), it will automatically pick up the change.
    """
    lang = setup_language(config)

    cfg = load_config(config)
    apply_config(cfg)

    # 确定调度表达式
    schedule = every or cron or "1h"

    store = CronStore(cfg.cron.store_path)
    job = store.add_job(
        name=name,
        schedule=schedule,
        message=message,
        channel=channel,
        chat_id=chat_id,
        timeout=timeout,
    )

    console.print(f"[green]{t('cron.created', lang)}[/green] {job.id}")
    console.print(f"  Name: {job.name}")
    console.print(f"  Schedule: {job.schedule}")
    console.print(f"  Message: {job.message}")
    if job.channel:
        console.print(f"  Dispatch: {job.channel}:{job.chat_id}")

    # 提示用户启动服务
    if not cfg.cron.enabled:
        console.print(f"\n[yellow]Tip: Enable cron service in config with [cron] enabled = true[/yellow]")
        console.print("[yellow]Then restart with 'deepcobot bot' or 'deepcobot serve'[/yellow]")


@cron_app.command("remove")
def cron_remove(
    job_id: str = typer.Argument(..., help="Task ID"),
    config: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Config file",
    ),
) -> None:
    """Remove a scheduled task."""
    lang = setup_language(config)

    cfg = load_config(config)
    apply_config(cfg)

    store = CronStore(cfg.cron.store_path)
    if store.remove_job(job_id):
        console.print(f"[green]{t('cron.removed', lang)}[/green] {job_id}")
    else:
        console.print(f"[red]{t('cron.not_found', lang)}[/red] {job_id}")
        raise typer.Exit(1)


@cron_app.command("run")
def cron_run_cmd(
    job_id: str = typer.Argument(..., help="Task ID"),
    config: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Config file",
    ),
) -> None:
    """Trigger a task to run immediately.

    Note: This marks the task for immediate execution in the store.
    The scheduler service (running via 'deepcobot bot' or 'deepcobot serve')
    will pick it up and execute.
    """
    lang = setup_language(config)

    cfg = load_config(config)
    apply_config(cfg)

    store = CronStore(cfg.cron.store_path)
    job = store.get_job(job_id)

    if not job:
        console.print(f"[red]{t('cron.not_found', lang)}[/red] {job_id}")
        raise typer.Exit(1)

    # 设置立即执行
    store.trigger_now(job_id)

    console.print(f"[green]Task '{job.name}' ({job_id}) marked for immediate execution[/green]")
    console.print("[yellow]The scheduler service will execute it shortly.[/yellow]")

    if not cfg.cron.enabled:
        console.print("\n[yellow]Warning: Cron service is not enabled.[/yellow]")
        console.print("[yellow]Enable it with [cron] enabled = true and restart.[/yellow]")


@cron_app.command("enable")
def cron_enable(
    job_id: str = typer.Argument(..., help="Task ID"),
    config: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Config file",
    ),
) -> None:
    """Enable a scheduled task."""
    lang = setup_language(config)

    cfg = load_config(config)
    apply_config(cfg)

    store = CronStore(cfg.cron.store_path)
    if store.enable_job(job_id):
        console.print(f"[green]Task {job_id} enabled[/green]")
    else:
        console.print(f"[red]{t('cron.not_found', lang)}[/red] {job_id}")
        raise typer.Exit(1)


@cron_app.command("disable")
def cron_disable(
    job_id: str = typer.Argument(..., help="Task ID"),
    config: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Config file",
    ),
) -> None:
    """Disable a scheduled task."""
    lang = setup_language(config)

    cfg = load_config(config)
    apply_config(cfg)

    store = CronStore(cfg.cron.store_path)
    if store.disable_job(job_id):
        console.print(f"[green]Task {job_id} disabled[/green]")
    else:
        console.print(f"[red]{t('cron.not_found', lang)}[/red] {job_id}")
        raise typer.Exit(1)


@cron_app.command("status")
def cron_status(
    config: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Config file",
    ),
) -> None:
    """Show cron service status."""
    lang = setup_language(config)

    cfg = load_config(config)
    apply_config(cfg)

    store = CronStore(cfg.cron.store_path)
    jobs = store.list_jobs(include_disabled=True)
    enabled_jobs = [j for j in jobs if j.enabled]

    console.print(f"\n[bold]Cron Service Status[/bold]")
    console.print(f"  Config enabled: {'[green]Yes[/green]' if cfg.cron.enabled else '[red]No[/red]'}")
    console.print(f"  Store path: {cfg.cron.store_path}")
    console.print(f"  Total tasks: {len(jobs)}")
    console.print(f"  Enabled tasks: {len(enabled_jobs)}")

    if jobs and cfg.cron.enabled:
        from datetime import datetime
        next_runs = [j.next_run_at for j in enabled_jobs if j.next_run_at]
        if next_runs:
            next_run = min(next_runs)
            console.print(f"  Next run: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            console.print("  Next run: [yellow]No scheduled runs[/yellow]")