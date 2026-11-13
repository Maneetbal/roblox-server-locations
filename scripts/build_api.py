#!/usr/bin/env python3
"""Build a compact static Roblox server-location JSON database."""

from __future__ import annotations

import ipaddress
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "roblox-verified-ips.txt"
OUTPUT = ROOT / "_site" / "api" / "v1" / "database.json"

# Approximate city-centre coordinates; these are location labels, not
# confirmed physical Roblox data-centre coordinates.
CITY_DATA = {
    ("United States", "Ashburn"): ("Virginia", "39.0438,-77.4874"),
    ("United States", "Atlanta"): ("Georgia", "33.7490,-84.3880"),
    ("United States", "Chicago"): ("Illinois", "41.8781,-87.6298"),
    ("United States", "Dallas"): ("Texas", "32.7767,-96.7970"),
    ("United States", "Los Angeles"): ("California", "34.0522,-118.2437"),
    ("United States", "Miami"): ("Florida", "25.7617,-80.1918"),
    ("United States", "New York City"): ("New York", "40.7128,-74.0060"),
    ("United States", "Seattle"): ("Washington", "47.6062,-122.3321"),
    ("Australia", "Sydney"): ("New South Wales", "-33.8688,151.2093"),
    ("Brazil", "Sao Paulo"): ("Sao Paulo", "-23.5505,-46.6333"),
    ("France", "Paris"): ("Ile-de-France", "48.8566,2.3522"),
    ("Germany", "Frankfurt"): ("Hesse", "50.1109,8.6821"),
    ("India", "Mumbai"): ("Maharashtra", "19.0760,72.8777"),
    ("Japan", "Tokyo"): ("Tokyo", "35.6762,139.6503"),
    ("Netherlands", "Amsterdam"): ("North Holland", "52.3676,4.9041"),
    ("Singapore", "Singapore"): ("Singapore", "1.3521,103.8198"),
    ("United Kingdom", "London"): ("England", "51.5072,-0.1276"),
}

ORG = "AS22697 Roblox"


def parse_database(text: str) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    country = None
    city = None

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if not line or line.startswith(("=", "**", "#")) or line.startswith("Last updated:"):
            continue

        if not line.startswith((" ", "\t", "-")):
            country = line.strip()
            city = None
            continue

        city_match = re.match(r"^-\s+(.+)$", line)
        if city_match:
            city = city_match.group(1).strip().partition(",")[0].strip()
            continue

        ip_match = re.match(
            r"^\s+-\s+((?:\d{1,3}\.){3}\d{1,3}(?:/\d{1,2})?)"
            r".*?\(Instance=([^)]*)\)",
            line,
        )
        if not ip_match or not country or not city:
            continue

        # Only publish entries with a numeric instance suffix. The repository
        # currently assumes .33; this is not independent proof of the IP.
        suffix_text = ip_match.group(2).strip()
        suffix_match = re.fullmatch(r"\.(\d{1,3})", suffix_text)
        if not suffix_match:
            continue

        network = ipaddress.ip_network(ip_match.group(1), strict=False)
        if network.version != 4 or network.prefixlen < 24:
            continue

        location = CITY_DATA.get((country, city))
        if location is None:
            raise SystemExit(f"Missing city metadata for {country}, {city}")

        region, coordinates = location
        octets = str(network.network_address).split(".")
        ip = ".".join(octets[:3] + [suffix_match.group(1)])

        entries.append({
            "ip": ip,
            "city": city,
            "region": region,
            "country": country,
            "loc": coordinates,
            "org": ORG,
        })

    # Keep the response compact and deterministic.
    entries.sort(key=lambda item: tuple(int(part) for part in item["ip"].split(".")))
    if not entries:
        raise SystemExit("No IP entries were parsed; refusing to publish an empty API.")
    return entries


def main() -> None:
    if not SOURCE.is_file():
        raise SystemExit(f"Missing source database: {SOURCE}")

    entries = parse_database(SOURCE.read_text(encoding="utf-8"))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(entries, separators=(",", ":"), ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    site_index = ROOT / "_site" / "index.html"
    site_index.parent.mkdir(parents=True, exist_ok=True)
    site_index.write_text(
        """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Roblox Server Locations API</title>
</head>
<body>
  <h1>Roblox Server Locations API</h1>
  <p><a href="./api/v1/database.json">JSON database</a></p>
</body>
</html>
""",
        encoding="utf-8",
    )

    print(f"Generated {len(entries)} compact API entries at {OUTPUT}")


if __name__ == "__main__":
    main()
