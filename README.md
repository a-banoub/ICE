# ICE Activity Monitor

Real-time monitoring system for ICE (Immigration and Customs Enforcement) activity. Collects reports from multiple community sources, correlates them across platforms, and sends alerts to Discord.

**Locale-aware** — ships with Minneapolis/Twin Cities configuration, but every piece of location-specific data lives in a single YAML file so you can deploy it for any city.

## Purpose

This tool helps community members stay informed about ICE enforcement activity in their area by:

- Aggregating reports from trusted community platforms (Iceout.org, StopICE.net)
- Monitoring social media for real-time alerts (Bluesky, Instagram, Twitter/X)
- Scanning local news RSS feeds for breaking enforcement stories
- Correlating reports across sources to reduce false positives
- Sending timely Discord notifications when activity is detected

## Features

- **Multi-Source Collection** — 7 collector types: Iceout.org, StopICE.net, Bluesky, Instagram, Twitter/X, Reddit, and RSS
- **Smart Correlation** — Groups related reports using temporal, geographic, and content similarity analysis
- **Configurable Locale** — All geographic keywords, monitored accounts, coordinates, and search queries live in `locales/<city>.yaml`
- **Geographic Filtering** — Configurable radius from a center point (default 50 km / ~31 mi)
- **Source-Based Trust** — High-priority sources (Iceout, StopICE) can trigger single-source alerts
- **News Filtering** — Rejects articles about court cases, past events, and policy discussions
- **Stale Account Detection** — Automatically skips social media accounts that haven't posted in 90+ days
- **Timezone-Aware** — Notifications display times in the locale's timezone (proper DST via `zoneinfo`)

## Data Sources

| Source | Type | Auth Required | Description |
|--------|------|:---:|-------------|
| **Iceout.org** | Community Platform | No | Crowd-sourced ICE sighting reports with verification |
| **StopICE.net** | Community Platform | No | SMS/web-based alert network |
| **Bluesky** | Social Media | No | Public API — monitored accounts + keyword searches |
| **Instagram** | Social Media | No | Playwright scraping of public profiles |
| **Twitter/X** | Social Media | Optional | Playwright scraping; login enables search |
| **Reddit** | Social Media | Yes | Async PRAW — monitors configured subreddits |
| **RSS Feeds** | News | No | Configurable feed list with strict relevance filtering |

---

## Quick Start

### 1. Install uv

[uv](https://docs.astral.sh/uv/) is a fast Python package manager that replaces `pip`, `venv`, and `pip-tools`.

**Linux / macOS / WSL:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

After installing, either restart your shell or run:
```bash
source $HOME/.local/bin/env
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Verify installation:**
```bash
uv --version
```

> **Already have uv?** Skip ahead to step 2.
>
> **Prefer pip?** You can still use `pip install -r requirements.txt` — the legacy file is kept for compatibility.

### 2. Clone & install

```bash
git clone https://github.com/yourusername/ice-monitor.git
cd ice-monitor
uv sync
```

`uv sync` reads `pyproject.toml`, creates a `.venv`, resolves dependencies, and installs everything in one shot.

### 3. Install browser & NLP model

```bash
# Playwright browser (needed for Iceout, Twitter, Instagram)
uv run playwright install chromium

# spaCy language model (needed for location extraction)
uv run python -m spacy download en_core_web_sm
```

### 4. Configure

```bash
cp .env.example .env
```

Edit `.env` — at minimum you need a Discord webhook URL:

```env
LOCALE=minneapolis                          # which locale YAML to load
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

See [Configuration](#configuration) below for all options.

### 5. Run

```bash
uv run python main.py
```

Dry run (logs only, no Discord):
```bash
uv run python main.py --dry-run
```

Verbose logging:
```bash
uv run python main.py --log-level DEBUG
```

---

## Configuration

All settings live in `.env`. Copy `.env.example` for the full reference.

### Locale

```env
# Must match a file in locales/ (e.g. minneapolis → locales/minneapolis.yaml)
LOCALE=minneapolis
```

The locale file controls: center coordinates, radius, timezone, geo keywords, monitored accounts, search queries, RSS feeds, subreddits, and Discord display text. See [Adding a New City](#adding-a-new-city).

### Discord

You can run **both** modes simultaneously.

#### Webhook Mode (simple, single channel)
1. Channel Settings → Integrations → Webhooks → New Webhook
2. Copy the URL

```env
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

#### Bot Mode (multi-server, subscribable)
1. [Discord Developer Portal](https://discord.com/developers/applications) → New Application → Bot
2. Enable **MESSAGE CONTENT INTENT** under Privileged Gateway Intents
3. OAuth2 → URL Generator → scopes: `bot`, `applications.commands` → permissions: Send Messages, Embed Links, Use Slash Commands
4. Share the invite URL

```env
DISCORD_BOT_TOKEN=your_bot_token
DISCORD_BOT_CLIENT_ID=your_app_client_id
```

**Bot Commands:**

| Command | Description |
|---------|-------------|
| `/ice subscribe [location]` | Subscribe this channel to alerts |
| `/ice unsubscribe` | Unsubscribe this channel |
| `/ice status` | View subscription status |
| `/ice help` | Show help |

### Collectors

```env
# Twitter (optional login for search)
TWITTER_ENABLED=true
TWITTER_USERNAME=
TWITTER_PASSWORD=

# Reddit (requires API creds from https://www.reddit.com/prefs/apps)
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=

# Community platforms (no auth needed)
ICEOUT_ENABLED=true
STOPICE_ENABLED=true
BLUESKY_ENABLED=true
INSTAGRAM_ENABLED=true
```

### Tuning

```env
MAX_DISTANCE_KM=50.0              # Geo-filter radius
CORRELATION_WINDOW_SECONDS=10800   # 3-hour correlation window
MIN_CORROBORATION_SOURCES=2        # Multi-source required (except trusted)
SIMILARITY_THRESHOLD=0.35          # Content similarity for clustering
GEO_PROXIMITY_KM=3.0              # Spatial proximity for clustering
CLUSTER_EXPIRY_HOURS=6.0           # Stop updates after this
```

---

## How It Works

### Pipeline

```
Collectors → Queue → Processor → Database → Correlator → Notifier → Discord
```

### Collection Phase

Each collector polls its source at configured intervals:

| Collector | Default Interval |
|-----------|:---:|
| Iceout.org | 90 s |
| Bluesky | 2 min |
| Twitter/X | 2 min |
| Instagram | 5 min |
| RSS | 5 min |
| Reddit | 1 min |
| StopICE.net | 30 min |

### Processing Phase

1. **Freshness Filter** — Discards reports older than 3 hours (6 h for trusted sources)
2. **Relevance Filter** — Two-tier keyword check: ICE keywords + geographic keywords (loaded from locale)
3. **News Filter** — Rejects articles about court cases, past events, or policy discussions
4. **Location Extraction** — spaCy NER + custom gazetteer identifies neighborhoods and coordinates

### Correlation Phase

1. **Cluster Updates** — Matches new reports to existing active incidents
2. **New Clusters** — Groups unclustered reports by temporal + geographic + content similarity
3. **High-Priority Singles** — Trusted sources (Iceout, StopICE) can trigger alerts without corroboration
4. **Confidence Scoring** — Source count, diversity, temporal tightness, location precision

### Notification Phase

- **NEW** — First-time corroborated incident
- **UPDATE** — Additional reports added to an existing incident
- Embeds include location, source count, confidence level, timestamps (in locale timezone), and source excerpts with links

---

## Locale System

All location-specific data is isolated in YAML files under `locales/`.

### What's in a locale file

| Section | Examples |
|---------|----------|
| `center` / `radius_km` | Geographic center + filter radius |
| `timezone` | IANA timezone (e.g. `America/Chicago`) |
| `geo_keywords` | 100+ keywords for text relevance filtering |
| `geo_city_names` | City/suburb names for coordinate-fallback filtering |
| `rss_feeds` / `subreddits` | Local news feeds and subreddits |
| `bluesky` / `twitter` / `instagram` | Monitored accounts, search queries, trusted handles |
| `discord` | Bot description, footer text, help text |
| `neighborhoods_file` / `landmarks_file` | Paths to geodata JSON files |
| `fallback_location` | Default location string for notifications |

### Adding a New City

1. **Copy the template:**
   ```bash
   cp locales/minneapolis.yaml locales/chicago.yaml
   ```

2. **Edit every section** — update center coordinates, geo keywords, monitored accounts, RSS feeds, search queries, and Discord display strings.

3. **Add geodata** (optional but recommended for neighborhood-level precision):
   ```bash
   # Create neighborhood + landmark JSON files for your city
   # See geodata/minneapolis_neighborhoods.json for the expected format
   ```

4. **Set the locale in `.env`:**
   ```env
   LOCALE=chicago
   ```

5. **Run** — everything else is automatic.

---

## Project Structure

```
ice-monitor/
├── main.py                     # Application entry point & orchestrator
├── config.py                   # Configuration (loads .env + locale)
├── pyproject.toml              # Project metadata & dependencies (uv)
├── requirements.txt            # Legacy pip dependencies
├── run_bot.py                  # Standalone Discord bot runner
├── .env.example                # Environment variable template
│
├── locales/                    # ⬅ Locale-specific configuration
│   └── minneapolis.yaml        #   Minneapolis/Twin Cities locale
├── geodata/                    # Geographic reference data
│   ├── minneapolis_neighborhoods.json
│   └── landmarks.json
│
├── collectors/                 # Data source collectors
│   ├── base.py                 #   Abstract base collector
│   ├── rss_collector.py
│   ├── reddit_collector.py
│   ├── bluesky_collector.py
│   ├── instagram_collector.py
│   ├── twitter_collector.py
│   ├── iceout_collector.py
│   └── stopice_collector.py
├── processing/                 # Text & location processing
│   ├── locale.py               #   Locale dataclass & YAML loader
│   ├── text_processor.py       #   ICE + geo keyword relevance filtering
│   ├── location_extractor.py   #   spaCy NER + gazetteer
│   └── similarity.py           #   TF-IDF content similarity
├── correlation/                # Report correlation engine
│   ├── correlator.py           #   Clustering & confidence scoring
│   └── report.py
├── notifications/              # Alert dispatching
│   ├── discord_notifier.py     #   Webhook-based notifications
│   └── discord_bot.py          #   Multi-server bot w/ subscriptions
├── storage/                    # Data persistence
│   ├── database.py             #   SQLite async wrapper
│   └── models.py               #   Data models (RawReport, etc.)
└── tests/
```

---

## Monitored Accounts (Minneapolis)

These are configured in `locales/minneapolis.yaml` and can be customized per-locale.

### Bluesky (8 accounts)
- **News:** @startribune, @bringmethenews, @sahanjournal
- **Journalists:** @maxnesterak
- **Community:** @miracmn, @conmijente, @defend612, @sunrisemvmt

### Instagram (4 accounts)
- @sunrisetwincities, @indivisible_twincities, @mnfreedomfund, @isaiah_mn

### Twitter/X (28 accounts)
Categorized as reporters, activists, news outlets, and officials. Automatically validates accounts — only scrapes those that have posted within 90 days.

---

## Reliability

- **Auto-Recovery** — Browser collectors automatically restart on crash or timeout
- **Timeout Protection** — 2-minute cap on each collection cycle
- **Backoff** — Collectors reset after 10 consecutive failures
- **Duplicate Prevention** — Database tracks seen report IDs across restarts
- **Account Validation** — Weekly cache refresh; stale/deleted accounts are skipped

---

## Disclaimer

This tool is for informational purposes only. It aggregates publicly available information from community sources. The accuracy of reports depends on the underlying sources. Always verify information through official channels when making safety decisions.

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT License — see LICENSE file for details.
