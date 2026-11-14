#!/usr/bin/env python3
import ipaddress as ip
import json
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

AWS = "https://ip-ranges.amazonaws.com/ip-ranges.json"
REACH = "http://ec2-reachability.amazonaws.com/prefixes-ipv4.json"
LOCATIONS = [
    ("United States", "Ashburn, VA", [("us-east-1", "us-east-1")]),
    ("United States", "Boardman, OR", [("us-west-2", "us-west-2")]),
    ("United States", "Columbus, OH", [("us-east-2", "us-east-2")]),
    ("United States", "Miami, FL", [("us-east-1", n) for n in ("us-east-1-mia-1", "us-east-1-mia-2", "us-east-1-wl1-mia-wlz-1")]),
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
    req = urllib.request.Request(url, headers={"User-Agent": "roblox-server-locations"})
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.load(r)

def main():
    with ThreadPoolExecutor(2) as pool:
        aws, reach = (f.result() for f in (pool.submit(fetch, AWS), pool.submit(fetch, REACH)))
    if not aws.get("syncToken") or not isinstance(aws.get("prefixes"), list) or not isinstance(reach, list):
        raise RuntimeError("Invalid AWS feed")

    ping = {}
    for item in reach:
        if isinstance(item, dict):
            for region, values in item.items():
                if region not in ping and isinstance(values, dict):
                    for value in values.values():
                        try:
                            ping[region] = str(ip.IPv4Address(value))
                            break
                        except (ValueError, TypeError):
                            pass

    wanted = {pair for _, _, pairs in LOCATIONS for pair in pairs}
    groups = {pair: set() for pair in wanted}
    for p in aws["prefixes"]:
        key = (p.get("region"), p.get("network_border_group"))
        if key in groups:
            try:
                groups[key].add(ip.IPv4Network(p["ip_prefix"], strict=False))
            except (KeyError, ValueError, TypeError):
                pass

    out = ["AWS IP Ranges Associated with Roblox Servers", "============================================",
           f"Last updated: {datetime.now(timezone.utc):%Y-%m-%d}", ""]
    aws_count = ping_count = 0
    for country, city, pairs in LOCATIONS:
        out += [country, "-" * len(country), f"- {city}"]
        for region, nbg in pairs:
            if region == nbg and region in ping:
                out.append(f"  - {ping[region]}/32 (PINGABLE)")
                ping_count += 1
                break
        nets = set()
        for pair in pairs:
            nets.update(ip.collapse_addresses(groups[pair]))
        for net in sorted(nets, key=lambda n: (int(n.network_address), n.prefixlen)):
            out.append(f"  - {net} (AWS)")
            aws_count += 1
        out.append("")

    if not aws_count or not ping_count:
        raise RuntimeError(f"Feed validation failed: {aws_count} CIDRs, {ping_count} pingable IPs")
    Path("aws-ips.txt").write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")
    print(f"Built {aws_count} CIDRs and {ping_count} PINGABLE IPs; syncToken={aws['syncToken']}")

if __name__ == "__main__":
    main()
