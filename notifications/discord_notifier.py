from __future__ import annotations

import logging
from datetime import datetime, timezone

from discord_webhook import DiscordWebhook, DiscordEmbed

from config import Config
from storage.models import CorroboratedIncident

logger = logging.getLogger(__name__)

# ── Colors ────────────────────────────────────────────────────────────
COLOR_NEW_HIGH = "FF0000"       # Red — new incident, high confidence
COLOR_NEW_MEDIUM = "FF4500"     # OrangeRed — new incident, medium
COLOR_NEW_LOW = "FF8C00"        # DarkOrange — new incident, low
COLOR_UPDATE = "3498DB"         # Blue — update to existing incident

# ── Source type labels ────────────────────────────────────────────────
SOURCE_LABELS = {
    "twitter": "Twitter/X",
    "reddit": "Reddit",
    "rss": "News (RSS)",
    "iceout": "Iceout.org",
}


def _confidence_emoji(score: float) -> str:
    if score >= 0.7:
        return "HIGH"
    elif score >= 0.45:
        return "MEDIUM"
    return "LOW"


def _get_color(incident: CorroboratedIncident) -> str:
    if incident.notification_type == "update":
        return COLOR_UPDATE
    score = incident.confidence_score
    if score >= 0.7:
        return COLOR_NEW_HIGH
    elif score >= 0.45:
        return COLOR_NEW_MEDIUM
    return COLOR_NEW_LOW


def _format_time_cst(dt: datetime) -> str:
    """Format a UTC datetime as Central time string."""
    # CST is UTC-6, CDT is UTC-5. Use -6 as approximation.
    from datetime import timedelta
    cst = dt - timedelta(hours=6)
    return cst.strftime("%-I:%M %p").replace("AM", "am").replace("PM", "pm")


def _format_time_cst_win(dt: datetime) -> str:
    """Format a UTC datetime as Central time string (Windows-safe)."""
    from datetime import timedelta
    cst = dt - timedelta(hours=6)
    # Windows doesn't support %-I, use %I and strip leading zero
    raw = cst.strftime("%I:%M %p")
    if raw.startswith("0"):
        raw = raw[1:]
    return raw.lower()


class DiscordNotifier:
    def __init__(self, config: Config):
        self.webhook_url = config.discord_webhook_url
        self.dry_run = config.dry_run

    def _build_new_incident_embed(
        self, incident: CorroboratedIncident
    ) -> DiscordEmbed:
        """Build embed for a NEW incident alert — designed for fast scanning."""
        color = _get_color(incident)
        conf = _confidence_emoji(incident.confidence_score)

        # Title: location front and center
        location = incident.primary_location or "Minneapolis area"
        embed = DiscordEmbed(
            title=f"ICE ACTIVITY: {location}",
            color=color,
        )

        # Topline summary — the most important info in 1-2 lines
        time_str = _format_time_cst_win(incident.earliest_report)
        if incident.earliest_report != incident.latest_report:
            time_str += f" - {_format_time_cst_win(incident.latest_report)}"

        platform_names = sorted(
            SOURCE_LABELS.get(s, s) for s in incident.unique_source_types
        )

        summary = (
            f"**{conf} confidence** | "
            f"{incident.source_count} reports across "
            f"{', '.join(platform_names)}\n"
            f"First reported: {time_str} CT"
        )
        embed.set_description(summary)

        # Source excerpts — compact, one per source
        for r in incident.reports[:6]:
            source_label = SOURCE_LABELS.get(r.source_type, r.source_type)
            # Truncate to keep it scannable
            excerpt = r.original_text[:120].replace("\n", " ").strip()
            if len(r.original_text) > 120:
                excerpt += "..."

            link = f"[source]({r.source_url})" if r.source_url else ""
            embed.add_embed_field(
                name=f"{source_label} — {r.author}",
                value=f"{excerpt}\n{link}",
                inline=False,
            )

        embed.set_footer(
            text=(
                "ICE Activity Monitor | Unverified community reporting | "
                "Confirm before acting"
            )
        )
        embed.set_timestamp(datetime.now(timezone.utc).isoformat())

        return embed

    def _build_update_embed(
        self, incident: CorroboratedIncident
    ) -> DiscordEmbed:
        """Build embed for an UPDATE to an existing incident."""
        color = COLOR_UPDATE
        location = incident.primary_location or "Minneapolis area"

        embed = DiscordEmbed(
            title=f"UPDATE: {location}",
            color=color,
        )

        new_reports = incident.new_reports or []
        conf = _confidence_emoji(incident.confidence_score)

        summary = (
            f"**{len(new_reports)} new source(s)** confirming earlier reports\n"
            f"Now at **{conf}** confidence | "
            f"{incident.source_count} total reports"
        )
        embed.set_description(summary)

        # Only show the NEW reports that triggered this update
        for r in new_reports[:4]:
            source_label = SOURCE_LABELS.get(r.source_type, r.source_type)
            excerpt = r.original_text[:120].replace("\n", " ").strip()
            if len(r.original_text) > 120:
                excerpt += "..."

            link = f"[source]({r.source_url})" if r.source_url else ""
            embed.add_embed_field(
                name=f"NEW: {source_label} — {r.author}",
                value=f"{excerpt}\n{link}",
                inline=False,
            )

        embed.set_footer(
            text=(
                "ICE Activity Monitor | Unverified community reporting | "
                "Confirm before acting"
            )
        )
        embed.set_timestamp(datetime.now(timezone.utc).isoformat())

        return embed

    def _build_embed(self, incident: CorroboratedIncident) -> DiscordEmbed:
        if incident.notification_type == "update":
            return self._build_update_embed(incident)
        return self._build_new_incident_embed(incident)

    async def send(self, incident: CorroboratedIncident) -> bool:
        """Send an incident to Discord. Returns True on success."""
        embed = self._build_embed(incident)

        if self.dry_run:
            ntype = incident.notification_type.upper()
            logger.info(
                "[discord] DRY RUN: Would send %s for cluster %d (%s, %d sources)",
                ntype,
                incident.cluster_id,
                incident.primary_location,
                incident.source_count,
            )
            return True

        if not self.webhook_url:
            logger.warning("[discord] No webhook URL configured, skipping")
            return False

        try:
            webhook = DiscordWebhook(
                url=self.webhook_url,
                username="ICE Activity Monitor",
            )
            webhook.add_embed(embed)
            response = webhook.execute()

            if response and response.status_code in (200, 204):
                logger.info(
                    "[discord] Sent %s notification for cluster %d",
                    incident.notification_type,
                    incident.cluster_id,
                )
                return True
            else:
                status = response.status_code if response else "no response"
                logger.error(
                    "[discord] Failed to send, status: %s", status
                )
                return False

        except Exception:
            logger.exception("[discord] Error sending webhook")
            return False
