from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

import feedparser
from dateutil import parser as dateparse

from collectors.base import BaseCollector
from storage.models import RawReport

logger = logging.getLogger(__name__)


class RSSCollector(BaseCollector):
    name = "rss"

    def get_poll_interval(self) -> int:
        return self.config.rss_poll_interval

    async def collect(self) -> list[RawReport]:
        reports: list[RawReport] = []
        for feed_url in self.config.rss_feeds:
            try:
                items = await self._fetch_feed(feed_url)
                reports.extend(items)
            except Exception:
                logger.exception("[rss] Failed to fetch %s", feed_url)
        return reports

    async def _fetch_feed(self, url: str) -> list[RawReport]:
        # feedparser is synchronous — run in a thread
        feed = await asyncio.to_thread(feedparser.parse, url)

        if feed.bozo and not feed.entries:
            logger.warning("[rss] Malformed feed %s: %s", url, feed.bozo_exception)
            return []

        reports = []
        now = datetime.now(timezone.utc)

        for entry in feed.entries:
            entry_id = entry.get("id") or entry.get("link") or entry.get("title", "")
            if not entry_id or not self._is_new(entry_id):
                continue

            # Parse the publication date
            published = entry.get("published") or entry.get("updated")
            if published:
                try:
                    ts = dateparse.parse(published)
                    if ts.tzinfo is None:
                        ts = ts.replace(tzinfo=timezone.utc)
                except (ValueError, TypeError):
                    ts = now
            else:
                ts = now

            title = entry.get("title", "")
            summary = entry.get("summary", "")
            text = f"{title}\n\n{summary}" if summary else title

            link = entry.get("link", "")
            author = entry.get("author", feed.feed.get("title", url))

            reports.append(RawReport(
                source_type="rss",
                source_id=entry_id,
                source_url=link,
                author=author,
                text=text,
                timestamp=ts,
                collected_at=now,
                raw_metadata={
                    "feed_url": url,
                    "feed_title": feed.feed.get("title", ""),
                    "tags": [t.get("term", "") for t in entry.get("tags", [])],
                },
            ))

        return reports
