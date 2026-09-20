from curl_cffi import requests
import json

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

print("HTTP Status:", response.status_code)

if response.status_code != 200:
    raise RuntimeError(
        f"Tracker returned HTTP {response.status_code}: {response.text[:1000]}"
    )

data = response.json()["data"]
segments = data.get("segments", [])

ranks = {}

for segment in segments:
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
    )

    if not rank_name:
        raise RuntimeError(f"Could not determine rank for playlist {playlist_id}")

    ranks[RANKED_PLAYLIST_IDS[playlist_id]] = rank_name

expected_modes = set(RANKED_PLAYLIST_IDS.values())
missing = expected_modes - set(ranks.keys())

if missing:
    raise RuntimeError(f"Tracker response was missing ranked modes: {sorted(missing)}")

with open("ranks.json", "w", encoding="utf-8") as file:
    json.dump(ranks, file, indent=2)
    file.write("\n")

print("\nUpdated ranks.json:")
for mode, rank in ranks.items():
    print(f"  {mode}: {rank}")
