from __future__ import annotations

import logging
from datetime import datetime, timezone

import asyncpraw

from collectors.base import BaseCollector
from processing.text_processor import is_relevant
from storage.models import RawReport

logger = logging.getLogger(__name__)


class RedditCollector(BaseCollector):
    name = "reddit"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._reddit: asyncpraw.Reddit | None = None

    async def _ensure_client(self) -> asyncpraw.Reddit:
        if self._reddit is None:
            self._reddit = asyncpraw.Reddit(
                client_id=self.config.reddit_client_id,
                client_secret=self.config.reddit_client_secret,
                user_agent=self.config.reddit_user_agent,
            )
        return self._reddit

    def get_poll_interval(self) -> int:
        return self.config.reddit_poll_interval

    async def collect(self) -> list[RawReport]:
        reddit = await self._ensure_client()
        reports: list[RawReport] = []
        now = datetime.now(timezone.utc)

        for sub_name in self.config.reddit_subreddits:
            try:
                subreddit = await reddit.subreddit(sub_name)
                async for submission in subreddit.new(limit=25):
                    source_id = f"reddit_{submission.id}"
                    if not self._is_new(source_id):
                        continue

                    title = submission.title or ""
                    selftext = submission.selftext or ""
                    full_text = f"{title}\n\n{selftext}" if selftext else title

                    # Client-side relevance pre-filter to avoid storing junk
                    if not is_relevant(full_text):
                        continue

                    ts = datetime.fromtimestamp(
                        submission.created_utc, tz=timezone.utc
                    )

                    reports.append(RawReport(
                        source_type="reddit",
                        source_id=source_id,
                        source_url=f"https://reddit.com{submission.permalink}",
                        author=str(submission.author) if submission.author else "[deleted]",
                        text=full_text,
                        timestamp=ts,
                        collected_at=now,
                        raw_metadata={
                            "subreddit": sub_name,
                            "score": submission.score,
                            "num_comments": submission.num_comments,
                            "link_flair_text": submission.link_flair_text,
                        },
                    ))

            except Exception:
                logger.exception("[reddit] Error fetching r/%s", sub_name)

        return reports

    async def stop(self) -> None:
        super().stop()
        if self._reddit:
            await self._reddit.close()
            self._reddit = None
