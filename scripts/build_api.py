#!/usr/bin/env python3
"""Build a compact static Roblox-associated IP-location JSON database."""

from __future__ import annotations

import ipaddress
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "all-ips.txt"
OUTPUT = ROOT / "_site" / "api" / "v1" / "database.json"

# Approximate city-centre coordinates; these are location labels, not
# confirmed physical Roblox data-centre coordinates.
CITY_DATA = {
    ("United States", "Ashburn"): ("Virginia", "39.0438,-77.4874"),
    ("United States", "Atlanta"): ("Georgia", "33.7490,-84.3880"),
    ("United States", "Boardman"): ("Oregon", "45.8399,-119.7006"),
    ("United States", "Chicago"): ("Illinois", "41.8781,-87.6298"),
    ("United States", "Columbus"): ("Ohio", "39.9612,-82.9988"),
    ("United States", "Dallas"): ("Texas", "32.7767,-96.7970"),
    ("United States", "Los Angeles"): ("California", "34.0522,-118.2437"),
    ("United States", "Miami"): ("Florida", "25.7617,-80.1918"),
    ("United States", "New York City"): ("New York", "40.7128,-74.0060"),
    ("United States", "San Jose"): ("California", "37.3382,-121.8863"),
    ("United States", "Seattle"): ("Washington", "47.6062,-122.3321"),
    ("Argentina", "Buenos Aires"): ("Buenos Aires", "-34.6037,-58.3816"),
    ("Australia", "Sydney"): ("New South Wales", "-33.8688,151.2093"),
    ("Brazil", "Sao Paulo"): ("Sao Paulo", "-23.5505,-46.6333"),
    ("Chile", "Santiago"): ("Santiago Metropolitan", "-33.4489,-70.6693"),
    ("France", "Paris"): ("Ile-de-France", "48.8566,2.3522"),
    ("Germany", "Frankfurt"): ("Hesse", "50.1109,8.6821"),
    ("India", "Mumbai"): ("Maharashtra", "19.0760,72.8777"),
    ("Ireland", "Dublin"): ("Leinster", "53.3498,-6.2603"),
    ("Israel", "Tel Aviv"): ("Tel Aviv District", "32.0853,34.7818"),
    ("Japan", "Osaka"): ("Osaka", "34.6937,135.5023"),
    ("Japan", "Tokyo"): ("Tokyo", "35.6762,139.6503"),
    ("Malaysia", "Kuala Lumpur"): ("Kuala Lumpur", "3.1390,101.6869"),
    ("Mexico", "Queretaro"): ("Queretaro", "20.5888,-100.3899"),
    ("Netherlands", "Amsterdam"): ("North Holland", "52.3676,4.9041"),
    ("Singapore", "Singapore"): ("Singapore", "1.3521,103.8198"),
    ("Switzerland", "Zurich"): ("Zurich", "47.3769,8.5417"),
    ("Turkey", "Istanbul"): ("Istanbul", "41.0082,28.9784"),
    ("United Kingdom", "London"): ("England", "51.5072,-0.1276"),
}

IP_PATTERN = re.compile(r"^\s+-\s+((?:\d{1,3}\.){3}\d{1,3}(?:/\d{1,2})?)(.*)$")


def parse_city(label: str) -> str:
    # Strip the region code and optional status annotation from the city heading.
    return label.split(",", 1)[0].replace("(Reserved)", "").strip()


def parse_database(text: str) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    country: str | None = None
    city: str | None = None
    seen: set[tuple[str, str, str]] = set()

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if not line or line.startswith(("=", "**", "#")) or line.startswith("Last updated:"):
            continue

        # Country headings are unindented. Ignore the document title.
        if not line.startswith((" ", "\t", "-")):
            heading = line.strip()
            if heading != "Roblox Server IP List":
                country = heading
                city = None
            continue

        # City headings begin at column zero; IP entries are indented.
        city_match = re.match(r"^-\s+(.+)$", line)
        if city_match:
            city = parse_city(city_match.group(1))
            continue

        ip_match = IP_PATTERN.match(line)
        if not ip_match or not country or not city:
            continue

        ip_or_cidr, notes = ip_match.groups()
        try:
            network = ipaddress.ip_network(ip_or_cidr, strict=False)
        except ValueError:
            continue
        if network.version != 4:
            continue

        location = CITY_DATA.get((country, city))
        if location is None:
            raise SystemExit(f"Missing city metadata for {country}, {city}")

        region, coordinates = location
        org = "Amazon AWS" if "(AWS)" in notes else "AS22697 Roblox"
        key = (str(network), country, city)
        if key in seen:
            continue
        seen.add(key)

        entries.append({
            "ip": str(network),
            "city": city,
            "region": region,
            "country": country,
            "loc": coordinates,
            "org": org,
        })

    # Deterministic output, sorted by network address and prefix length.
    entries.sort(key=lambda item: (
        int(ipaddress.ip_network(item["ip"]).network_address),
        ipaddress.ip_network(item["ip"]).prefixlen,
        item["country"],
        item["city"],
    ))
    if not entries:
        raise SystemExit("No IP ranges were parsed; refusing to publish an empty API.")
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

    print(f"Generated {len(entries)} compact API entries from all-ips.txt")


if __name__ == "__main__":
    main()
