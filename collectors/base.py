from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod

from config import Config
from storage.models import RawReport

logger = logging.getLogger(__name__)


class BaseCollector(ABC):
    """Abstract base for all data source collectors.

    Subclasses implement ``collect()`` and ``get_poll_interval()``.
    The ``run()`` loop handles scheduling and exponential backoff.
    """

    name: str = "base"

    def __init__(self, config: Config, report_queue: asyncio.Queue):
        self.config = config
        self.report_queue = report_queue
        self.is_running = False
        self._seen_ids: set[str] = set()

    @abstractmethod
    async def collect(self) -> list[RawReport]:
        """Perform one collection cycle. Return new reports."""
        ...

    @abstractmethod
    def get_poll_interval(self) -> int:
        """Seconds between collection cycles."""
        ...

    def _is_new(self, source_id: str) -> bool:
        """Check if we've already seen this source_id this session."""
        if source_id in self._seen_ids:
            return False
        self._seen_ids.add(source_id)
        # Cap the in-memory set to avoid unbounded growth
        if len(self._seen_ids) > 10_000:
            # Keep the most recent half (arbitrary trim)
            trimmed = list(self._seen_ids)[-5_000:]
            self._seen_ids = set(trimmed)
        return True

    async def run(self) -> None:
        """Main loop: collect, enqueue, sleep, repeat."""
        self.is_running = True
        backoff = 1
        max_backoff = 300  # 5 minutes
        cycle_count = 0

        logger.info("[%s] Collector starting", self.name)

        while self.is_running:
            try:
                cycle_count += 1
                logger.info("[%s] Starting collection cycle %d", self.name, cycle_count)

                reports = await self.collect()
                backoff = 1  # reset on success

                for report in reports:
                    await self.report_queue.put(report)

                if reports:
                    logger.info(
                        "[%s] Collected %d new reports", self.name, len(reports)
                    )
                else:
                    logger.info("[%s] Cycle %d complete, no new reports", self.name, cycle_count)

            except asyncio.CancelledError:
                logger.info("[%s] Collector cancelled", self.name)
                break
            except Exception:
                logger.exception(
                    "[%s] Error during collection, backing off %ds",
                    self.name,
                    backoff,
                )
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, max_backoff)
                continue

            await asyncio.sleep(self.get_poll_interval())

        logger.info("[%s] Collector stopped", self.name)

    def stop(self) -> None:
        self.is_running = False
