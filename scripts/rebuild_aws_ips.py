#!/usr/bin/env python3
import ipaddress as ip
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

AWS = "https://ip-ranges.amazonaws.com/ip-ranges.json"
REACH = "http://ec2-reachability.amazonaws.com/prefixes-ipv4.json"
OUT = Path("aws-ips.txt")

# Country, city, [(AWS Region, NetworkBorderGroup)]
LOCATIONS = [
    ("United States", "Ashburn, VA", [("us-east-1", "us-east-1")]),
    ("United States", "Boardman, OR", [("us-west-2", "us-west-2")]),
    ("United States", "Columbus, OH", [("us-east-2", "us-east-2")]),
    ("United States", "Miami, FL", [("us-east-1", x) for x in ("us-east-1-mia-1", "us-east-1-mia-2", "us-east-1-wl1-mia-wlz-1")]),
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

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "roblox-server-locations-ip-updater"})
    with urllib.request.urlopen(req, timeout=45) as r:
        if r.status != 200:
            raise RuntimeError(f"HTTP {r.status}: {url}")
        return json.load(r)

def main():
    aws, reach = fetch(AWS), fetch(REACH)
    if not isinstance(aws.get("prefixes"), list) or not aws.get("syncToken"):
        raise RuntimeError("Invalid AWS IP range feed")
    if not isinstance(reach, list):
        raise RuntimeError("Invalid AWS reachability feed")

    pingable = {}
    for item in reach:
        if not isinstance(item, dict):
            continue
        for region, values in item.items():
            if region in pingable or not isinstance(values, dict):
                continue
            for value in values.values():
                try:
                    pingable[region] = str(ip.IPv4Address(value))
                    break
                except (ValueError, TypeError):
                    pass

    groups = {}
    for p in aws["prefixes"]:
        try:
            key = (p["region"], p["network_border_group"])
            net = ip.IPv4Network(p["ip_prefix"], strict=False)
            groups.setdefault(key, set()).add(net)
        except (KeyError, ValueError, TypeError):
            continue

    lines = [
        "AWS IP Ranges Associated with Roblox Servers",
        "============================================",
        f"Last updated: {datetime.now(timezone.utc):%Y-%m-%d}", "",
    ]
    aws_count = ping_count = 0
    for country, city, pairs in LOCATIONS:
        lines += [country, "-" * len(country), f"- {city}"]
        # Only standard region endpoints; never borrow across border groups.
        for region, nbg in pairs:
            if region == nbg and region in pingable:
                lines.append(f"  - {pingable[region]}/32 (PINGABLE)")
                ping_count += 1
                break
        # Collapse within each exact Region + NetworkBorderGroup only.
        networks = set()
        for pair in pairs:
            networks.update(ip.collapse_addresses(groups.get(pair, set())))
        for net in sorted(networks, key=lambda n: (int(n.network_address), n.prefixlen)):
            lines.append(f"  - {net} (AWS)")
            aws_count += 1
        lines.append("")

    if not aws_count:
        raise RuntimeError("No AWS CIDRs matched; refusing to overwrite aws-ips.txt")
    if not ping_count:
        raise RuntimeError("No exact-region pingable endpoints matched; refusing to overwrite aws-ips.txt")
    OUT.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(f"Generated {OUT}: {aws_count} AWS CIDRs, {ping_count} exact-region PINGABLE endpoints; syncToken={aws['syncToken']}")

if __name__ == "__main__":
    main()
