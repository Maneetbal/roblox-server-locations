#!/usr/bin/env python3
"""Build the static Roblox Server Locations JSON API for GitHub Pages."""

from __future__ import annotations

import ipaddress
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "roblox-verified-ips.txt"
OUTPUT = ROOT / "_site" / "api" / "v1" / "database.json"

COUNTRY_CODE = {
    "United States": "US",
    "Australia": "AU",
    "Brazil": "BR",
    "France": "FR",
    "Germany": "DE",
    "India": "IN",
    "Japan": "JP",
    "Netherlands": "NL",
    "Singapore": "SG",
    "United Kingdom": "GB",
}


def parse_database(text: str) -> list[dict]:
    entries: list[dict] = []
    country = None
    city = None

    for raw_line in text.splitlines():
        line = raw_line.rstrip()

        if not line or line.startswith(("=", "**", "#")) or line.startswith("Last updated:"):
            continue

        # Country headings are unindented plain text.
        if not line.startswith((" ", "\t", "-")):
            country = line.strip()
            city = None
            continue

        # City headings use a single leading dash; IP rows are indented.
        city_match = re.match(r"^-\\s+(.+)$", line)
        if city_match:
            city = city_match.group(1).strip()
            continue

        ip_match = re.match(
            r"^\\s+-\\s+((?:\\d{1,3}\\.){3}\\d{1,3}(?:/\\d{1,2})?)"
            r"(?:\\s+\\(Confidence=(\\d{1,3})\\))?"
            r"(?:\\s+\\(ICMP=([^)]*)\\))?"
            r"(?:\\s+\\(Instance=([^)]*)\\))?"
            r"(?:\\s+\\(Hostname=([^)]*)\\))?",
            line,
        )
        if not ip_match or not country or not city:
            continue

        network = ipaddress.ip_network(ip_match.group(1), strict=False)
        city_name, _, region = city.partition(",")
        confidence = int(ip_match.group(2)) if ip_match.group(2) else None
        icmp = ip_match.group(3)
        instance = ip_match.group(4)
        hostname = ip_match.group(5)

        entry = {
            "cidr": str(network),
            "city": city_name.strip(),
            "region": region.strip() or None,
            "country": country,
            "country_code": COUNTRY_CODE.get(country),
            "confidence": confidence,
            "confidence_type": "maintainer-assessed-location-confidence" if confidence is not None else None,
            "icmp_endpoint_suffix": icmp,
            "instance_suffix": instance,
            "instance_suffix_is_assumed": bool(instance),
            "hostname": hostname,
            "hostname_evidence_for": "ICMP endpoint" if hostname else None,
        }
        entries.append(entry)

    # Most-specific prefixes must be checked first by API consumers.
    entries.sort(key=lambda item: (-ipaddress.ip_network(item["cidr"]).prefixlen,
                                   int(ipaddress.ip_network(item["cidr"]).network_address)))
    return entries


def main() -> None:
    if not SOURCE.is_file():
        raise SystemExit(f"Missing source database: {SOURCE}")

    entries = parse_database(SOURCE.read_text(encoding="utf-8"))
    if not entries:
        raise SystemExit("No IP entries were parsed; refusing to publish an empty API.")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "name": "Roblox Server Locations API",
        "description": "Static CIDR location reference built from the repository's reviewed verified-IP ledger.",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "source": "https://github.com/Maneetbal/roblox-server-locations/blob/main/roblox-verified-ips.txt",
        "lookup_method": "Match the queried IPv4 address against entries[].cidr; use the most-specific matching prefix.",
        "important_notes": [
            "Locations are estimates, not confirmation of a physical Roblox data center.",
            "confidence is a maintainer-assessed location score, not a statistical probability.",
            "instance_suffix values in the source ledger are maintainer assumptions, not independently captured full game-instance IPs.",
            "hostname evidence in the source ledger refers to the ICMP endpoint, not necessarily the game-instance address.",
            "A CIDR match identifies a network location entry; it does not prove that every address in the prefix hosts a Roblox game instance."
        ],
        "entries": entries,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

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
  <p>A static, community-maintained IPv4 CIDR location reference.</p>
  <p><a href="./api/v1/database.json">API database (JSON)</a></p>
  <p>See the <a href="https://github.com/Maneetbal/roblox-server-locations">GitHub repository</a>
  for methodology, verification notes, and contributions.</p>
  <p>Unofficial project; not affiliated with Roblox. Locations are estimates.</p>
</body>
</html>
""",
        encoding="utf-8",
    )

    print(f"Generated {len(entries)} API entries at {OUTPUT}")


if __name__ == "__main__":
    main()
