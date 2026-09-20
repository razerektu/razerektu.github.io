from curl_cffi import requests
import json
from pathlib import Path
from datetime import datetime, timezone

URL = "https://api.tracker.gg/api/v2/rocket-league/standard/profile/epic/RaZe%20Is%20Here"

HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://rocketleague.tracker.network",
    "Referer": "https://rocketleague.tracker.network/",
}

RANKED_PLAYLIST_IDS = {
    10: "1v1",
    11: "2v2",
    13: "3v3",
    27: "Hoops",
    28: "Rumble",
    29: "Dropshot",
    30: "Snow Day",
    61: "4v4 Quads",
}

response = requests.get(
    URL,
    headers=HEADERS,
    impersonate="chrome",
    timeout=30,
)

response.raise_for_status()
data = response.json()["data"]

ranks = {}

for segment in data.get("segments", []):
    if segment.get("type") != "playlist":
        continue

    attributes = segment.get("attributes", {})
    playlist_id = attributes.get("playlistId")

    if playlist_id not in RANKED_PLAYLIST_IDS:
        continue

    stats = segment.get("stats", {})
    tier = stats.get("tier", {})

    rank_name = (
        tier.get("metadata", {}).get("rankName")
        or tier.get("metadata", {}).get("name")
        or tier.get("metadata", {}).get("displayName")
        or tier.get("rankName")
        or tier.get("name")
        or tier.get("displayValue")
        or "Unknown"
    )

    ranks[RANKED_PLAYLIST_IDS[playlist_id]] = rank_name

if len(ranks) != len(RANKED_PLAYLIST_IDS):
    raise RuntimeError(f"Expected {len(RANKED_PLAYLIST_IDS)} ranked playlists, found {len(ranks)}")

output = {
    "player": "RaZe Is Here",
    "updated": datetime.now(timezone.utc).isoformat(),
    "ranks": ranks,
}

Path("ranks.json").write_text(
    json.dumps(output, indent=2) + "\n",
    encoding="utf-8",
)

print(json.dumps(output, indent=2))
