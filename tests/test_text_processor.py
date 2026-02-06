"""Tests for content filtering in text_processor.py.

Focuses on NEWS_ARTICLE_PATTERNS that should reject news articles
from community sources (Bluesky, Twitter, Reddit) while allowing
real-time activity reports through.
"""

import pytest
from processing.text_processor import is_relevant, NEWS_ARTICLE_PATTERNS, REALTIME_SIGNALS


# ── Posts that SHOULD be rejected (news articles from community sources) ──


class TestDayOfWeekReferences:
    """Day-of-week references indicate past events, not real-time activity."""

    def test_on_sunday(self):
        text = "Federal agents in tactical gear deployed irritants at Powderhorn Park on Sunday."
        assert is_relevant(text, "bluesky") is False

    def test_on_monday(self):
        text = "ICE-related developments in Minnesota today, which follows more protests on Monday."
        assert is_relevant(text, "bluesky") is False

    def test_on_friday_twitter(self):
        text = "ICE raids reported across Minneapolis on Friday."
        assert is_relevant(text, "twitter") is False

    def test_day_reference_with_realtime_override(self):
        """Real-time signals should override day-of-week patterns."""
        text = "ICE spotted at Lake Street in Minneapolis right now, similar to what happened on Monday."
        assert is_relevant(text, "bluesky") is True


class TestPoliticalCommentary:
    """Political quotes/commentary about past events, not real-time reports."""

    def test_president_trump_said(self):
        text = "Here's exactly what President Trump said about the fatal Minneapolis ICE shootings."
        assert is_relevant(text, "bluesky") is False

    def test_governor_announced(self):
        text = "Governor Walz announced new measures regarding ICE operations in Minnesota."
        assert is_relevant(text, "bluesky") is False

    def test_mayor_responded(self):
        text = "Mayor Frey responded to ICE activity in Minneapolis neighborhoods."
        assert is_relevant(text, "bluesky") is False

    def test_what_said_about(self):
        text = "What the chief of police said about ICE operations in Minneapolis."
        assert is_relevant(text, "bluesky") is False


class TestViralRetrospectiveContent:
    """Sharing of viral past content, not real-time reports."""

    def test_viral_clip(self):
        text = "You may have seen the viral clip of ICE agents in Minneapolis."
        assert is_relevant(text, "bluesky") is False

    def test_viral_video(self):
        text = "This viral video shows ICE enforcement in the Twin Cities."
        assert is_relevant(text, "bluesky") is False

    def test_you_may_have_seen(self):
        text = "You may have seen the reports about ICE activity at Lake Street Minneapolis."
        assert is_relevant(text, "bluesky") is False


class TestFatalEventCoverage:
    """Coverage of past fatal events, not real-time activity."""

    def test_fatal_shooting(self):
        text = "The fatal shooting involving ICE agents in Minneapolis."
        assert is_relevant(text, "bluesky") is False

    def test_fatal_encounter(self):
        text = "Details emerge about the fatal encounter between ICE agents and residents in St Paul."
        assert is_relevant(text, "bluesky") is False


class TestNewsFramingLanguage:
    """News outlet language indicating coverage, not real-time reports."""

    def test_following_the_latest(self):
        text = "We're following the latest ICE-related developments in Minnesota."
        assert is_relevant(text, "bluesky") is False

    def test_following_recent(self):
        text = "Following recent ICE enforcement actions in Minneapolis."
        assert is_relevant(text, "bluesky") is False

    def test_more_protests(self):
        text = "More protests against ICE operations in Minneapolis."
        assert is_relevant(text, "bluesky") is False


# ── Posts that SHOULD pass (real-time activity reports) ──


class TestRealTimeReportsShouldPass:
    """Legitimate real-time reports must not be blocked."""

    def test_spotted_right_now(self):
        text = "ICE agents spotted at Lake Street and Nicollet in Minneapolis right now."
        assert is_relevant(text, "bluesky") is True

    def test_heads_up(self):
        text = "Heads up - unmarked van seen near Cedar-Riverside, possible ICE activity."
        assert is_relevant(text, "bluesky") is True

    def test_ice_is_here(self):
        text = "ICE is here at the corner of Franklin Avenue in Minneapolis."
        assert is_relevant(text, "bluesky") is True

    def test_community_alert_sighting(self):
        text = "Community alert: ICE sighting near Powderhorn Park in Minneapolis."
        assert is_relevant(text, "bluesky") is True

    def test_generic_community_report(self):
        text = "ICE activity reported near Uptown Minneapolis."
        assert is_relevant(text, "bluesky") is True

    def test_federal_agents_community(self):
        text = "Reports of federal agents in Phillips neighborhood Minneapolis."
        assert is_relevant(text, "bluesky") is True


class TestTrustedSourcesBypass:
    """Trusted sources (iceout, stopice) should bypass news filtering."""

    def test_iceout_with_news_pattern(self):
        """Even if text has news-like words, iceout is trusted."""
        text = "ICE activity at Lake Street in Minneapolis yesterday."
        assert is_relevant(text, "iceout") is True

    def test_stopice_with_news_pattern(self):
        text = "ICE agents in St Paul on Sunday, confirmed by community."
        assert is_relevant(text, "stopice") is True


class TestNewsSourcesStrict:
    """RSS/news sources require real-time signals to pass."""

    def test_rss_rejected_without_realtime(self):
        text = "ICE enforcement operations continue in Minneapolis."
        assert is_relevant(text, "rss") is False

    def test_rss_passes_with_realtime_signal(self):
        text = "ICE agents spotted at Lake Street right now, Minneapolis police confirm."
        assert is_relevant(text, "rss") is True


# ── Original patterns still work ──


class TestExistingPatternsStillWork:
    """Verify pre-existing filter patterns haven't regressed."""

    def test_yesterday(self):
        text = "ICE raids in Minneapolis yesterday left community shaken."
        assert is_relevant(text, "bluesky") is False

    def test_last_week(self):
        text = "ICE enforcement actions in Minneapolis last week."
        assert is_relevant(text, "bluesky") is False

    def test_sentenced_to(self):
        text = "Man sentenced to 5 years for threatening ICE agents in Minneapolis."
        assert is_relevant(text, "bluesky") is False

    def test_executive_order(self):
        text = "New executive order expands ICE authority in Minnesota."
        assert is_relevant(text, "bluesky") is False

    def test_trump_administration(self):
        text = "Trump administration announces expanded ICE operations in Minneapolis."
        assert is_relevant(text, "bluesky") is False

    def test_noise_ice_cream(self):
        text = "Best ice cream shops in Minneapolis, Minnesota."
        assert is_relevant(text, "bluesky") is False


# ── The exact posts from the screenshot ──


class TestScreenshotPosts:
    """The three Bluesky posts from the screenshot that should have been filtered."""

    def test_bringmethenews_post1(self):
        text = (
            "You may have seen the viral clip, but here's exactly what "
            "President Trump said about the fatal Minneapolis ICE shootings..."
        )
        assert is_relevant(text, "bluesky") is False

    def test_bringmethenews_post2(self):
        text = (
            "Federal agents in tactical gear deployed irritants, "
            "arrested observer at Powderhorn Park on Sunday."
        )
        assert is_relevant(text, "bluesky") is False

    def test_bringmethenews_post3(self):
        text = (
            "We're once again following the latest ICE-related developments "
            "in Minnesota today, which follows more protests on Monday..."
        )
        assert is_relevant(text, "bluesky") is False
