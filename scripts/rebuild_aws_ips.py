#!/usr/bin/env python3
import ipaddress
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

AWS_URL = "https://ip-ranges.amazonaws.com/ip-ranges.json"
REACH_URL = "http://ec2-reachability.amazonaws.com/prefixes-ipv4.json"
OUT = Path("aws-ips.txt")

# Only exact AWS Region + NetworkBorderGroup pairs are included.
LOCATIONS = [
    ("United States", "Ashburn, VA", [("us-east-1", "us-east-1")]),
    ("United States", "Boardman, OR", [("us-west-2", "us-west-2")]),
    ("United States", "Columbus, OH", [("us-east-2", "us-east-2")]),
    ("United States", "Miami, FL", [("us-east-1", "us-east-1-mia-1"), ("us-east-1", "us-east-1-mia-2"), ("us-east-1", "us-east-1-wl1-mia-wlz-1")]),
    ("United States", "San Jose, CA", [("us-west-1", "us-west-1")]),
    ("Argentina", "Buenos Aires, AR", [("us-east-1", "us-east-1-bue-1")]),
    ("Brazil", "Sao Paulo, BR", [("sa-east-1", "sa-east-1")]),
    ("Chile", "Santiago, CL", [("us-east-1", "us-east-1-scl-1")]),
    ("Germany", "Frankfurt, DE", [("eu-central-1", "eu-central-1")]),
    ("Greece", "Athens, GR", [("eu-central-1", "eu-central-1-ath-1")]),
    ("India", "Mumbai, IN", [("ap-south-1", "ap-south-1")]),
    ("Indonesia", "Jakarta, ID", [("ap-southeast-3", "ap-southeast-3")]),
    ("Ireland", "Dublin, IE", [("eu-west-1", "eu-west-1")]),
    ("Israel", "Tel Aviv, IL", [("il-central-1", "il-central-1")]),
    ("Italy", "Milan, IT", [("eu-south-1", "eu-south-1")]),
    ("Japan", "Osaka, JP", [("ap-northeast-3", "ap-northeast-3")]),
    ("Malaysia", "Kuala Lumpur, MY", [("ap-southeast-5", "ap-southeast-5")]),
    ("Mexico", "Queretaro, MX", [("mx-central-1", "mx-central-1"), ("us-east-1", "us-east-1-qro-1")]),
    ("Peru", "Lima, PE", [("us-east-1", "us-east-1-lim-1")]),
    ("Poland", "Warsaw, PL", [("eu-central-1", "eu-central-1-waw-1")]),
    ("Singapore", "Singapore, SG", [("ap-southeast-1", "ap-southeast-1")]),
    ("South Africa", "Cape Town, ZA", [("af-south-1", "af-south-1")]),
    ("Switzerland", "Zurich, CH", [("eu-central-2", "eu-central-2")]),
    ("Turkey", "Istanbul, TR", [("eu-central-1", "eu-central-1-ist-1")]),
]

def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "roblox-server-locations-ip-updater"})
    with urllib.request.urlopen(req, timeout=45) as response:
        if response.status != 200:
            raise RuntimeError(f"HTTP {response.status} from {url}")
        return json.load(response)

def main():
    aws = fetch_json(AWS_URL)
    if not isinstance(aws.get("prefixes"), list) or not aws.get("syncToken"):
        raise RuntimeError("AWS IP range feed failed validation")
    reach_data = fetch_json(REACH_URL)
    if not isinstance(reach_data, list):
        raise RuntimeError("AWS reachability feed failed validation")

    # Keep one valid IPv4 endpoint per exact AWS region key.
    pingable_by_region = {}
    for item in reach_data:
        if not isinstance(item, dict):
            continue
        for region, prefixes in item.items():
            if not isinstance(prefixes, dict) or region in pingable_by_region:
                continue
            for address in prefixes.values():
                try:
                    ip = ipaddress.IPv4Address(address)
                except (ipaddress.AddressValueError, TypeError):
                    continue
                pingable_by_region[region] = str(ip)
                break

    grouped = {}
    for p in aws["prefixes"]:
        region = p.get("region")
        nbg = p.get("network_border_group")
        cidr = p.get("ip_prefix")
        if not region or not nbg or not cidr:
            continue
        try:
            network = ipaddress.IPv4Network(cidr, strict=False)
        except ipaddress.AddressValueError:
            continue
        grouped.setdefault((region, nbg), []).append(network)

    lines = [
        "AWS IP Ranges Associated with Roblox Servers",
        "============================================",
        f"Last updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
        "",
    ]
    total_aws = 0
    total_pingable = 0
    for country, city, pairs in LOCATIONS:
        lines.extend([country, "-" * len(country), f"- {city}"])
        # Only show an endpoint when the reachability feed has the exact
        # region AND the location is the region's standard border group.
        # Special border groups (e.g. Istanbul, Athens, Miami) never borrow
        # a generic regional endpoint from another location.
        for region, nbg in pairs:
            if region == nbg and region in pingable_by_region:
                lines.append(f"  - {pingable_by_region[region]}/32 (PINGABLE)")
                total_pingable += 1
                break
        # Collapse each exact Region + NetworkBorderGroup separately.
        # Never combine adjacent ranges from different AWS location groups.
        location_networks = set()
        for pair in pairs:
            pair_networks = grouped.get(pair, [])
            if pair_networks:
                for network in ipaddress.collapse_addresses(set(pair_networks)):
                    location_networks.add(network)
        for network in sorted(location_networks, key=lambda n: (int(n.network_address), n.prefixlen)):
            lines.append(f"  - {network} (AWS)")
            total_aws += 1
        lines.append("")
    if total_aws == 0:
        raise RuntimeError("No AWS CIDRs matched; refusing to overwrite aws-ips.txt")
    if total_pingable == 0:
        raise RuntimeError("No exact-region pingable endpoints matched; refusing to overwrite aws-ips.txt")
    OUT.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(f"Generated {OUT}: {total_aws} AWS CIDRs, {total_pingable} exact-region PINGABLE endpoints; AWS syncToken={aws['syncToken']}")

if __name__ == "__main__":
    main()
