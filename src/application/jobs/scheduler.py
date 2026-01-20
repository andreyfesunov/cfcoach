import asyncio
from typing import Callable, Optional, Awaitable
from asyncio import Task


class Scheduler:
    def __init__(self, interval_hours: float) -> None:
        self.interval_hours = interval_hours
        self.interval_seconds = interval_hours * 3600
        self._running = False
        self._task: Optional[Task[None]] = None

    async def start(self, job: Callable[[], Awaitable[None]]) -> None:
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._run_periodically(job))

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _run_periodically(self, job: Callable[[], Awaitable[None]]) -> None:
        while self._running:
            try:
                await job()
            except Exception:
                pass
            await asyncio.sleep(self.interval_seconds)


class MultiScheduler:
    def __init__(self) -> None:
        self._jobs: list[tuple[Callable[[], Awaitable[None]], float]] = []
        self._schedulers: list[Scheduler] = []
        self._running = False

    def add_job(
        self, job: Callable[[], Awaitable[None]], interval_hours: float
    ) -> None:
        self._jobs.append((job, interval_hours))

    async def start_all(self) -> None:
        if self._running:
            return
        self._running = True
        for job, interval_hours in self._jobs:
            scheduler = Scheduler(interval_hours)
            await scheduler.start(job)
            self._schedulers.append(scheduler)

    async def stop_all(self) -> None:
        self._running = False
        for scheduler in self._schedulers:
            await scheduler.stop()
        self._schedulers.clear()
