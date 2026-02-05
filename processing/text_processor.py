from __future__ import annotations

import html
import re
import logging

logger = logging.getLogger(__name__)

# --- Two-tier keyword system ---
# A report is relevant only if it matches at least one keyword from EACH tier.

# ICE / immigration enforcement keywords.
# Single words use word-boundary regex; phrases use substring match.
ICE_KEYWORDS_EXACT: set[str] = {
    # These require word boundaries to avoid false positives
    # ("ice" matches "notice", "service" etc. without boundaries)
    "ice",
    "ero",
}

ICE_KEYWORDS_PHRASE: set[str] = {
    # These are specific enough to use substring matching
    "immigration and customs enforcement",
    "immigration enforcement",
    "enforcement and removal",
    "deportation",
    "deportation raid",
    "immigration raid",
    "immigration arrest",
    "federal agents",
    "detained by",
    "detention center",
    "immigration checkpoint",
    "ice agents",
    "ice raid",
    "ice officers",
    "immigration officers",
    "customs enforcement",
    "removal operations",
    "ice vehicle",
    "unmarked van",
    "unmarked vehicle",
    "unmarked suv",
    "ice sighting",
    "ice spotted",
    "ice watch",
    "ice activity",
    "immigration sweep",
    "deportation force",
    "rapid response",
    "know your rights",
    "community alert",
    "ice detainer",
}

# Pre-compiled word-boundary patterns for exact keywords
_ICE_EXACT_RE = re.compile(
    r"\b(?:" + "|".join(re.escape(kw) for kw in ICE_KEYWORDS_EXACT) + r")\b",
    re.IGNORECASE,
)

GEO_KEYWORDS: set[str] = {
    "minneapolis",
    "mpls",
    "hennepin",
    "hennepin county",
    "twin cities",
    "st paul",
    "saint paul",
    "ramsey county",
    "minnesota",
    # Major neighborhoods
    "uptown",
    "downtown minneapolis",
    "north minneapolis",
    "south minneapolis",
    "northeast minneapolis",
    "cedar-riverside",
    "cedar riverside",
    "west bank",
    "phillips",
    "powderhorn",
    "whittier",
    "seward",
    "longfellow",
    "nokomis",
    "loring park",
    "elliot park",
    "stevens square",
    "ventura village",
    "midtown",
    "corcoran",
    "standish",
    "ericsson",
    "kingfield",
    "lyndale",
    "tangletown",
    "diamond lake",
    "hale",
    "page",
    "field",
    "regina",
    "northrup",
    "kenny",
    "windom",
    "armatage",
    "lynnhurst",
    "fulton",
    "linden hills",
    "east harriet",
    "west calhoun",
    "east isles",
    "lowry hill",
    "lowry hill east",
    "kenwood",
    "bryn mawr",
    "harrison",
    "hawthorne",
    "near north",
    "willard-hay",
    "jordan",
    "folwell",
    "mckinley",
    "humboldt industrial",
    "sumner-glenwood",
    "prospect park",
    "como",
    "marcy-holmes",
    "nicollet island",
    "st anthony west",
    "st anthony east",
    "waite park",
    "audubon park",
    "holland",
    "logan park",
    "marshall terrace",
    "bottineau",
    "sheridan",
    "columbia park",
    "windom park",
    # Metro suburbs commonly involved in ICE enforcement
    "bloomington",
    "richfield",
    "brooklyn park",
    "brooklyn center",
    "columbia heights",
    "fridley",
    "crystal",
    "golden valley",
    "robbinsdale",
    "st louis park",
    "eden prairie",
    "burnsville",
    "eagan",
    "shakopee",
    "albertville",
    # Major streets and landmarks
    "lake street",
    "nicollet avenue",
    "hennepin avenue",
    "franklin avenue",
    "central avenue",
    "university avenue",
    "washington avenue",
    "lyndale avenue",
    "bloomington avenue",
    "chicago avenue",
    "portland avenue",
    "cedar avenue",
    "hiawatha avenue",
    "minnehaha",
    "us bank stadium",
    "mall of america",
    "msp airport",
}

# ── Noise rejection ──────────────────────────────────────────────────
# Terms that cause false positives when "ice" is matched.
# If text contains these WITHOUT a stronger ICE phrase, it's likely noise.
NOISE_CONTEXTS = re.compile(
    r"\b(?:"
    r"ice cream|ice fishing|ice skating|icy roads|"
    r"black ice|ice dam|ice storm|ice hockey|"
    r"ice rink|dry ice|thin ice|break the ice|"
    r"ice scraper|ice melt|ice cold|iced coffee|iced tea"
    r")\b",
    re.IGNORECASE,
)

# Pre-compile a URL stripping pattern
_URL_RE = re.compile(r"https?://\S+")
_HTML_TAG_RE = re.compile(r"<[^>]+>")
_WHITESPACE_RE = re.compile(r"\s+")


def clean_text(text: str) -> str:
    """Normalize text for processing."""
    text = _HTML_TAG_RE.sub(" ", text)
    text = html.unescape(text)
    text = _URL_RE.sub("", text)
    text = _WHITESPACE_RE.sub(" ", text)
    return text.strip()


def _match_ice_keywords(text_lower: str) -> list[str]:
    """Find ICE-related keyword matches with word-boundary awareness."""
    matches = []

    # Check exact keywords with word boundaries
    for m in _ICE_EXACT_RE.finditer(text_lower):
        matches.append(m.group())

    # Check phrase keywords with substring matching
    for kw in ICE_KEYWORDS_PHRASE:
        if kw in text_lower:
            matches.append(kw)

    return matches


def _match_geo_keywords(text_lower: str) -> list[str]:
    """Find geographic keyword matches."""
    return [kw for kw in GEO_KEYWORDS if kw in text_lower]


def find_matching_keywords(text: str) -> tuple[list[str], list[str]]:
    """Return (matched_ice_keywords, matched_geo_keywords) found in text."""
    text_lower = text.lower()
    ice_matches = _match_ice_keywords(text_lower)
    geo_matches = _match_geo_keywords(text_lower)
    return ice_matches, geo_matches


def is_relevant(text: str) -> bool:
    """Check if text matches at least one ICE keyword AND one geo keyword.

    Also rejects false positives where "ice" only appears in a noise
    context like "ice cream" or "ice fishing".
    """
    text_lower = text.lower()
    ice_matches = _match_ice_keywords(text_lower)
    geo_matches = _match_geo_keywords(text_lower)

    if not ice_matches or not geo_matches:
        return False

    # If the only ICE match is the bare word "ice", check for noise contexts
    if ice_matches == ["ice"] or all(m == "ice" for m in ice_matches):
        # If there's a noise context match, reject unless there's also
        # a stronger signal (like "ice agents" or "detained")
        if NOISE_CONTEXTS.search(text_lower):
            return False

    return True


def get_all_matched_keywords(text: str) -> list[str]:
    """Return combined list of all matched keywords."""
    ice_matches, geo_matches = find_matching_keywords(text)
    return ice_matches + geo_matches
