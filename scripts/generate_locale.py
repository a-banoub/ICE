"""Generate locale YAML files for new cities.

Usage:
    python scripts/generate_locale.py                # Generate all new cities
    python scripts/generate_locale.py lasvegas       # Generate one city
    python scripts/generate_locale.py --list          # List available cities
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

LOCALES_DIR = Path(__file__).resolve().parent.parent / "locales"

# ── City data ────────────────────────────────────────────────────────────
# Each entry: (filename, display_name, state, state_abbrev, lat, lon, timezone, radius_km,
#              counties, neighborhoods/suburbs, landmarks)

CITIES: dict[str, dict] = {
    "lasvegas": {
        "display_name": "Las Vegas Metro",
        "state": "Nevada",
        "state_abbrev": "NV",
        "lat": 36.1699,
        "lon": -115.1398,
        "timezone": "America/Los_Angeles",
        "radius_km": 50.0,
        "counties": ["Clark County"],
        "neighborhoods": [
            "The Strip", "Downtown Las Vegas", "Summerlin", "Henderson",
            "North Las Vegas", "Paradise", "Spring Valley", "Enterprise",
            "Sunrise Manor", "Winchester", "Whitney", "Nellis AFB",
            "Boulder City", "Mesquite", "Pahrump", "Centennial Hills",
            "Aliante", "Anthem", "Green Valley", "Lake Las Vegas",
            "Chinatown", "Arts District", "Fremont Street",
            "East Las Vegas", "West Las Vegas",
        ],
        "landmarks": [
            "McCarran Airport", "Harry Reid Airport", "Fremont Street",
            "Las Vegas Boulevard", "UNLV",
        ],
        "subreddit": "vegaslocals",
    },
    "losangeles": {
        "display_name": "Los Angeles Metro",
        "state": "California",
        "state_abbrev": "CA",
        "lat": 34.0522,
        "lon": -118.2437,
        "timezone": "America/Los_Angeles",
        "radius_km": 60.0,
        "counties": ["Los Angeles County", "Orange County"],
        "neighborhoods": [
            "Downtown LA", "East LA", "South LA", "Boyle Heights",
            "Koreatown", "Westlake", "Pico-Union", "MacArthur Park",
            "Hollywood", "Echo Park", "Silver Lake", "Highland Park",
            "El Monte", "Pomona", "Compton", "Inglewood",
            "Long Beach", "Pasadena", "Glendale", "Burbank",
            "Santa Ana", "Anaheim", "Garden Grove", "Huntington Park",
            "Maywood", "Bell Gardens", "Cudahy", "South Gate",
            "Pacoima", "Van Nuys", "North Hollywood", "Canoga Park",
        ],
        "landmarks": ["LAX", "Union Station", "Olvera Street", "USC", "UCLA"],
        "subreddit": "LosAngeles",
    },
    "houston": {
        "display_name": "Houston Metro",
        "state": "Texas",
        "state_abbrev": "TX",
        "lat": 29.7604,
        "lon": -95.3698,
        "timezone": "America/Chicago",
        "radius_km": 60.0,
        "counties": ["Harris County", "Fort Bend County", "Montgomery County"],
        "neighborhoods": [
            "Downtown Houston", "Midtown Houston", "Montrose", "Heights",
            "East End", "Gulfton", "Sharpstown", "Alief",
            "Spring Branch", "Greenspoint", "Pasadena", "Baytown",
            "Sugar Land", "Katy", "Humble", "Channelview",
            "Galena Park", "Jacinto City", "South Houston",
            "Missouri City", "Pearland", "League City",
            "Magnolia Park", "Denver Harbor", "Second Ward",
        ],
        "landmarks": ["George Bush IAH", "Hobby Airport", "Galleria"],
        "subreddit": "houston",
    },
    "phoenix": {
        "display_name": "Phoenix Metro",
        "state": "Arizona",
        "state_abbrev": "AZ",
        "lat": 33.4484,
        "lon": -112.0740,
        "timezone": "America/Phoenix",
        "radius_km": 55.0,
        "counties": ["Maricopa County", "Pinal County"],
        "neighborhoods": [
            "Downtown Phoenix", "South Phoenix", "Maryvale", "Alhambra",
            "Central City", "Encanto", "Laveen", "Guadalupe",
            "Mesa", "Tempe", "Chandler", "Gilbert",
            "Scottsdale", "Glendale", "Peoria", "Surprise",
            "Avondale", "Goodyear", "Buckeye", "Casa Grande",
            "Apache Junction", "Tolleson", "El Mirage",
        ],
        "landmarks": ["Sky Harbor Airport", "ASU", "Papago Park"],
        "subreddit": "phoenix",
    },
    "sandiego": {
        "display_name": "San Diego Metro",
        "state": "California",
        "state_abbrev": "CA",
        "lat": 32.7157,
        "lon": -117.1611,
        "timezone": "America/Los_Angeles",
        "radius_km": 50.0,
        "counties": ["San Diego County"],
        "neighborhoods": [
            "Downtown San Diego", "Barrio Logan", "City Heights",
            "San Ysidro", "Otay Mesa", "Chula Vista", "National City",
            "El Cajon", "Escondido", "Oceanside", "Vista",
            "Carlsbad", "Encinitas", "La Mesa", "Lemon Grove",
            "Spring Valley", "Encanto", "Logan Heights",
            "Sherman Heights", "Linda Vista", "Mira Mesa",
        ],
        "landmarks": [
            "San Ysidro Port of Entry", "Otay Mesa Port of Entry",
            "San Diego Airport", "SDSU",
        ],
        "subreddit": "sandiego",
    },
    "sanfrancisco": {
        "display_name": "San Francisco Bay Area",
        "state": "California",
        "state_abbrev": "CA",
        "lat": 37.7749,
        "lon": -122.4194,
        "timezone": "America/Los_Angeles",
        "radius_km": 50.0,
        "counties": [
            "San Francisco County", "Alameda County",
            "Santa Clara County", "Contra Costa County",
        ],
        "neighborhoods": [
            "Mission District", "Tenderloin", "SoMa", "Chinatown",
            "Sunset", "Excelsior", "Bayview", "Visitacion Valley",
            "Oakland", "Berkeley", "Richmond", "San Leandro",
            "Hayward", "Fremont", "Concord", "Antioch",
            "Daly City", "South San Francisco", "San Mateo",
            "Redwood City", "East Palo Alto",
        ],
        "landmarks": ["SFO Airport", "Oakland Airport", "UC Berkeley"],
        "subreddit": "bayarea",
    },
    "seattle": {
        "display_name": "Seattle Metro",
        "state": "Washington",
        "state_abbrev": "WA",
        "lat": 47.6062,
        "lon": -122.3321,
        "timezone": "America/Los_Angeles",
        "radius_km": 50.0,
        "counties": ["King County", "Snohomish County", "Pierce County"],
        "neighborhoods": [
            "Downtown Seattle", "Capitol Hill", "International District",
            "Beacon Hill", "Rainier Valley", "Columbia City",
            "Georgetown", "White Center", "Burien", "Tukwila",
            "SeaTac", "Renton", "Kent", "Auburn",
            "Federal Way", "Tacoma", "Everett", "Lynnwood",
            "Bellevue", "Redmond", "Kirkland",
        ],
        "landmarks": ["Sea-Tac Airport", "Pike Place", "UW"],
        "subreddit": "Seattle",
    },
    "denver": {
        "display_name": "Denver Metro",
        "state": "Colorado",
        "state_abbrev": "CO",
        "lat": 39.7392,
        "lon": -104.9903,
        "timezone": "America/Denver",
        "radius_km": 50.0,
        "counties": ["Denver County", "Adams County", "Arapahoe County", "Jefferson County"],
        "neighborhoods": [
            "Downtown Denver", "Five Points", "Globeville", "Elyria-Swansea",
            "Sun Valley", "Westwood", "Barnum", "Federal Boulevard",
            "Aurora", "Lakewood", "Arvada", "Westminster",
            "Thornton", "Northglenn", "Commerce City", "Brighton",
            "Englewood", "Littleton", "Centennial",
        ],
        "landmarks": ["DIA", "Denver International Airport", "Coors Field"],
        "subreddit": "Denver",
    },
    "boston": {
        "display_name": "Boston Metro",
        "state": "Massachusetts",
        "state_abbrev": "MA",
        "lat": 42.3601,
        "lon": -71.0589,
        "timezone": "America/New_York",
        "radius_km": 45.0,
        "counties": ["Suffolk County", "Middlesex County", "Norfolk County"],
        "neighborhoods": [
            "Downtown Boston", "East Boston", "Dorchester", "Roxbury",
            "Mattapan", "Jamaica Plain", "Hyde Park", "Roslindale",
            "Chelsea", "Revere", "Everett", "Somerville",
            "Cambridge", "Lynn", "Brockton", "Quincy",
            "Malden", "Waltham", "Lawrence", "Lowell",
        ],
        "landmarks": ["Logan Airport", "MIT", "Harvard"],
        "subreddit": "boston",
    },
    "philadelphia": {
        "display_name": "Philadelphia Metro",
        "state": "Pennsylvania",
        "state_abbrev": "PA",
        "lat": 39.9526,
        "lon": -75.1652,
        "timezone": "America/New_York",
        "radius_km": 45.0,
        "counties": ["Philadelphia County", "Delaware County", "Montgomery County"],
        "neighborhoods": [
            "Center City", "North Philadelphia", "South Philadelphia",
            "Kensington", "Fairhill", "Hunting Park", "Olney",
            "Frankford", "Feltonville", "West Philadelphia",
            "Upper Darby", "Chester", "Norristown", "Camden",
            "Cherry Hill", "Trenton",
        ],
        "landmarks": ["PHL Airport", "Temple University", "UPenn"],
        "subreddit": "philadelphia",
    },
    "detroit": {
        "display_name": "Detroit Metro",
        "state": "Michigan",
        "state_abbrev": "MI",
        "lat": 42.3314,
        "lon": -83.0458,
        "timezone": "America/Detroit",
        "radius_km": 50.0,
        "counties": ["Wayne County", "Oakland County", "Macomb County"],
        "neighborhoods": [
            "Downtown Detroit", "Southwest Detroit", "Mexicantown",
            "Corktown", "Hamtramck", "Dearborn", "Dearborn Heights",
            "Lincoln Park", "Ecorse", "River Rouge",
            "Pontiac", "Sterling Heights", "Warren", "Southgate",
            "Taylor", "Westland", "Canton", "Ypsilanti",
        ],
        "landmarks": [
            "Detroit Metro Airport", "Ambassador Bridge",
            "Detroit-Windsor Tunnel", "Wayne State",
        ],
        "subreddit": "Detroit",
    },
    "portland": {
        "display_name": "Portland Metro",
        "state": "Oregon",
        "state_abbrev": "OR",
        "lat": 45.5152,
        "lon": -122.6784,
        "timezone": "America/Los_Angeles",
        "radius_km": 45.0,
        "counties": ["Multnomah County", "Washington County", "Clackamas County"],
        "neighborhoods": [
            "Downtown Portland", "Old Town Chinatown", "Pearl District",
            "East Portland", "Jade District", "Lents",
            "Cully", "Montavilla", "Rockwood", "Gresham",
            "Beaverton", "Hillsboro", "Tigard", "Tualatin",
            "Oregon City", "Milwaukie", "Lake Oswego",
        ],
        "landmarks": ["PDX Airport", "Portland State University"],
        "subreddit": "Portland",
    },
    "sacramento": {
        "display_name": "Sacramento Metro",
        "state": "California",
        "state_abbrev": "CA",
        "lat": 38.5816,
        "lon": -121.4944,
        "timezone": "America/Los_Angeles",
        "radius_km": 45.0,
        "counties": ["Sacramento County", "Yolo County", "Placer County"],
        "neighborhoods": [
            "Downtown Sacramento", "Midtown Sacramento", "Oak Park",
            "Del Paso Heights", "North Sacramento", "South Sacramento",
            "Meadowview", "Fruitridge", "Elk Grove", "Rancho Cordova",
            "Citrus Heights", "Roseville", "Folsom", "Davis",
            "Woodland", "West Sacramento", "Arden-Arcade",
        ],
        "landmarks": ["Sacramento Airport", "UC Davis", "Sac State"],
        "subreddit": "Sacramento",
    },
    "sanjose": {
        "display_name": "San Jose Metro",
        "state": "California",
        "state_abbrev": "CA",
        "lat": 37.3382,
        "lon": -121.8863,
        "timezone": "America/Los_Angeles",
        "radius_km": 40.0,
        "counties": ["Santa Clara County"],
        "neighborhoods": [
            "Downtown San Jose", "East San Jose", "Alum Rock",
            "Mayfair", "Santana Row", "Willow Glen", "Japantown",
            "Milpitas", "Sunnyvale", "Santa Clara", "Mountain View",
            "Gilroy", "Morgan Hill", "Campbell", "Los Gatos",
            "Cupertino", "Palo Alto",
        ],
        "landmarks": ["San Jose Airport", "SJSU", "Stanford"],
        "subreddit": "SanJose",
    },
    "elpaso": {
        "display_name": "El Paso Metro",
        "state": "Texas",
        "state_abbrev": "TX",
        "lat": 31.7619,
        "lon": -106.4850,
        "timezone": "America/Denver",
        "radius_km": 45.0,
        "counties": ["El Paso County"],
        "neighborhoods": [
            "Downtown El Paso", "Segundo Barrio", "Chihuahuita",
            "Central El Paso", "Lower Valley", "Upper Valley",
            "Northeast El Paso", "Eastside", "Mission Valley",
            "Socorro", "Horizon City", "Canutillo",
            "Sunland Park", "Anthony", "Clint", "Fabens",
        ],
        "landmarks": [
            "El Paso Airport", "Bridge of the Americas",
            "Paso del Norte Bridge", "Ysleta Port of Entry",
            "UTEP", "Fort Bliss",
        ],
        "subreddit": "ElPaso",
    },
    "sanantonio": {
        "display_name": "San Antonio Metro",
        "state": "Texas",
        "state_abbrev": "TX",
        "lat": 29.4241,
        "lon": -98.4936,
        "timezone": "America/Chicago",
        "radius_km": 50.0,
        "counties": ["Bexar County", "Comal County"],
        "neighborhoods": [
            "Downtown San Antonio", "West Side", "South Side",
            "East Side", "Prospect Hill", "Avenida Guadalupe",
            "Las Palmas", "Edgewood", "Highlands",
            "Leon Valley", "Balcones Heights", "Converse",
            "Live Oak", "Universal City", "Schertz",
            "New Braunfels", "Seguin", "Selma",
        ],
        "landmarks": ["San Antonio Airport", "Lackland AFB", "UTSA", "The Alamo"],
        "subreddit": "sanantonio",
    },
    "austin": {
        "display_name": "Austin Metro",
        "state": "Texas",
        "state_abbrev": "TX",
        "lat": 30.2672,
        "lon": -97.7431,
        "timezone": "America/Chicago",
        "radius_km": 45.0,
        "counties": ["Travis County", "Williamson County", "Hays County"],
        "neighborhoods": [
            "Downtown Austin", "East Austin", "South Austin",
            "North Austin", "Rundberg", "Riverside",
            "Montopolis", "Dove Springs", "St Johns",
            "Pflugerville", "Round Rock", "Cedar Park",
            "Georgetown", "San Marcos", "Kyle", "Buda",
            "Del Valle", "Manor",
        ],
        "landmarks": ["Austin-Bergstrom Airport", "UT Austin", "State Capitol"],
        "subreddit": "Austin",
    },
    "charlotte": {
        "display_name": "Charlotte Metro",
        "state": "North Carolina",
        "state_abbrev": "NC",
        "lat": 35.2271,
        "lon": -80.8431,
        "timezone": "America/New_York",
        "radius_km": 45.0,
        "counties": ["Mecklenburg County", "Gaston County", "Union County"],
        "neighborhoods": [
            "Uptown Charlotte", "South End", "NoDa",
            "East Charlotte", "West Charlotte", "Hidden Valley",
            "University City", "Ballantyne", "Steele Creek",
            "Gastonia", "Concord", "Kannapolis",
            "Huntersville", "Matthews", "Mint Hill",
            "Monroe", "Indian Trail",
        ],
        "landmarks": ["Charlotte Douglas Airport", "UNCC", "Bank of America Stadium"],
        "subreddit": "Charlotte",
    },
    "newark": {
        "display_name": "Newark / North Jersey",
        "state": "New Jersey",
        "state_abbrev": "NJ",
        "lat": 40.7357,
        "lon": -74.1724,
        "timezone": "America/New_York",
        "radius_km": 40.0,
        "counties": ["Essex County", "Hudson County", "Passaic County", "Bergen County"],
        "neighborhoods": [
            "Downtown Newark", "Ironbound", "North Ward", "East Ward",
            "South Ward", "West Ward", "Central Ward",
            "Jersey City", "Elizabeth", "Paterson", "Passaic",
            "Union City", "West New York", "North Bergen",
            "Hackensack", "Garfield", "Clifton", "East Orange",
            "Irvington", "Bloomfield", "Belleville",
        ],
        "landmarks": ["Newark Airport", "EWR", "Rutgers Newark", "NJIT"],
        "subreddit": "newjersey",
    },
}


def generate_yaml(key: str) -> str:
    """Generate a locale YAML string for a city."""
    city = CITIES[key]
    name = city["display_name"].split(" Metro")[0].split(" /")[0].split(" Bay")[0]
    state = city["state"]
    state_abbrev = city["state_abbrev"]

    # Build geo_keywords
    geo_keywords = []
    # City name variations
    geo_keywords.append(name.lower())
    if " " in name:
        geo_keywords.append(name.lower().replace(" ", ""))  # e.g. "lasvegas"
    geo_keywords.append(state.lower())
    # Counties
    for county in city["counties"]:
        geo_keywords.append(county.lower())
    # Metro name
    geo_keywords.append(f"metro {name.lower()}")
    # Neighborhoods
    for n in city["neighborhoods"]:
        geo_keywords.append(n.lower())
    # Landmarks
    for lm in city["landmarks"]:
        geo_keywords.append(lm.lower())

    # Deduplicate preserving order
    seen = set()
    unique_keywords = []
    for kw in geo_keywords:
        if kw not in seen:
            seen.add(kw)
            unique_keywords.append(kw)

    # Build geo_city_names (broader, simpler matches)
    geo_city_names = [name.lower()]
    if " " in name:
        geo_city_names.append(name.lower().replace(" ", ""))
    geo_city_names.append(state.lower())
    geo_city_names.append(state_abbrev.lower())
    for county in city["counties"]:
        geo_city_names.append(county.lower())
    # Add major suburbs/cities from neighborhoods
    for n in city["neighborhoods"]:
        nl = n.lower()
        # Skip generic directional names
        if nl.startswith(("downtown", "east ", "west ", "north ", "south ", "central ", "upper ", "lower ", "northeast")):
            continue
        geo_city_names.append(nl)

    seen2 = set()
    unique_city_names = []
    for cn in geo_city_names:
        if cn not in seen2:
            seen2.add(cn)
            unique_city_names.append(cn)

    subreddit = city.get("subreddit", name.replace(" ", ""))

    lines = []
    lines.append(f"# ============================================================")
    lines.append(f"# {name}, {state_abbrev} — Locale Configuration")
    lines.append(f"# ============================================================")
    lines.append(f"")
    lines.append(f"name: {key}")
    lines.append(f'display_name: "{city["display_name"]}"')
    lines.append(f"timezone: {city['timezone']}")
    lines.append(f"")
    lines.append(f"# ── Geographic center & radius ────────────────────────────────")
    lines.append(f"center:")
    lines.append(f"  lat: {city['lat']}")
    lines.append(f"  lon: {city['lon']}")
    lines.append(f"radius_km: {city['radius_km']}")
    lines.append(f"")
    lines.append(f"# ── Fallback location strings ────────────────────────────────")
    lines.append(f'fallback_location: "{name} area"')
    lines.append(f'fallback_location_unspecified: "{name} (unspecified)"')
    lines.append(f"")
    lines.append(f"# ── Geodata files ─────────────────────────────────────────────")
    lines.append(f'neighborhoods_file: ""')
    lines.append(f'landmarks_file: ""')
    lines.append(f"")
    lines.append(f"# ── Geographic keywords ──────────────────────────────────────")
    lines.append(f"geo_keywords:")
    for kw in unique_keywords:
        lines.append(f"  - {kw}")
    lines.append(f"")
    lines.append(f"geo_city_names:")
    for cn in unique_city_names:
        lines.append(f"  - {cn}")
    lines.append(f"")
    lines.append(f"# ── RSS feeds ────────────────────────────────────────────────")
    lines.append(f"rss_feeds: []")
    lines.append(f"")
    lines.append(f"# ── Reddit ───────────────────────────────────────────────────")
    lines.append(f"subreddits:")
    lines.append(f"  - {subreddit}")
    lines.append(f"  - immigration")
    lines.append(f"")
    lines.append(f"# ── Bluesky ──────────────────────────────────────────────────")
    lines.append(f"bluesky:")
    lines.append(f"  search_queries:")
    lines.append(f'    - "ICE {name}"')
    lines.append(f'    - "ICE {state}"')
    lines.append(f'    - "immigration raid {name}"')
    lines.append(f'    - "deportation {state}"')
    lines.append(f"  monitored_accounts: []")
    lines.append(f"  trusted_accounts: []")
    lines.append(f"")
    lines.append(f"# ── Twitter/X ────────────────────────────────────────────────")
    lines.append(f"twitter:")
    lines.append(f"  search_queries:")
    lines.append(f'    - \'(ICE OR "immigration enforcement") ("{name}" OR "{city["counties"][0]}") -is:retweet\'')
    lines.append(f'    - \'(ICE raid OR "ICE agents" OR deportation) {state} -is:retweet\'')
    lines.append(f'    - \'("federal agents" OR "unmarked van" OR "ICE sighting") "{name}" -is:retweet\'')
    lines.append(f'    - \'(detained OR detention OR "immigration arrest") "{name}" -is:retweet\'')
    lines.append(f"  reporter_accounts: []")
    lines.append(f"  activist_accounts:")
    lines.append(f"    - UnitedWeDream")
    lines.append(f"    - ConMijente")
    lines.append(f"  news_accounts: []")
    lines.append(f"  official_accounts: []")
    lines.append(f"")
    lines.append(f"# ── Instagram ────────────────────────────────────────────────")
    lines.append(f"instagram:")
    lines.append(f"  monitored_accounts: []")
    lines.append(f"")
    lines.append(f"# ── Discord display ──────────────────────────────────────────")
    lines.append(f"discord:")
    lines.append(f'  bot_description: "{name} ICE Activity Monitor"')
    lines.append(f'  footer_text: "{name} ICE Monitor | Stay safe, know your rights"')
    lines.append(f'  subscribe_message: "ICE activity is reported in the {name} area"')
    lines.append(f"  help_description: >-")
    lines.append(f"    This bot monitors multiple sources for ICE enforcement activity")
    lines.append(f"    in the {name} metro area and sends alerts to subscribed channels.")
    lines.append(f"")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate locale YAML files")
    parser.add_argument("cities", nargs="*", help="City keys to generate (default: all)")
    parser.add_argument("--list", action="store_true", help="List available city keys")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    args = parser.parse_args()

    if args.list:
        for key in sorted(CITIES):
            city = CITIES[key]
            print(f"  {key:20s} {city['display_name']}")
        return

    cities_to_generate = args.cities if args.cities else list(CITIES.keys())

    for key in cities_to_generate:
        if key not in CITIES:
            print(f"Unknown city: {key}", file=sys.stderr)
            print(f"Available: {', '.join(sorted(CITIES))}", file=sys.stderr)
            sys.exit(1)

    generated = 0
    skipped = 0
    for key in cities_to_generate:
        path = LOCALES_DIR / f"{key}.yaml"
        if path.exists() and not args.force:
            print(f"  SKIP {path.name} (already exists, use --force to overwrite)")
            skipped += 1
            continue

        yaml_content = generate_yaml(key)
        path.write_text(yaml_content, encoding="utf-8")
        print(f"  CREATED {path.name}")
        generated += 1

    print(f"\nDone: {generated} created, {skipped} skipped")


if __name__ == "__main__":
    main()
