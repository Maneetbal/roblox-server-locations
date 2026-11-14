#!/usr/bin/env python3
import ipaddress as ip
import json
import re
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
CITY = {
    "ashburn": ("Virginia", "39.0438,-77.4874"),
    "atlanta": ("Georgia", "33.7490,-84.3880"),
    "boardman": ("Oregon", "45.8399,-119.7006"),
    "chicago": ("Illinois", "41.8781,-87.6298"),
    "columbus": ("Ohio", "39.9612,-82.9988"),
    "dallas": ("Texas", "32.7767,-96.7970"),
    "los angeles": ("California", "34.0522,-118.2437"),
    "miami": ("Florida", "25.7617,-80.1918"),
    "new york city": ("New York", "40.7128,-74.0060"),
    "san jose": ("California", "37.3382,-121.8863"),
    "seattle": ("Washington", "47.6062,-122.3321"),
    "buenos aires": ("Buenos Aires", "-34.6037,-58.3816"),
    "sydney": ("New South Wales", "-33.8688,151.2093"),
    "sao paulo": ("Sao Paulo", "-23.5505,-46.6333"),
    "santiago": ("Santiago Metropolitan Region", "-33.4489,-70.6693"),
    "paris": ("Ile-de-France", "48.8566,2.3522"),
    "frankfurt": ("Hesse", "50.1109,8.6821"),
    "athens": ("Attica", "37.9838,23.7275"),
    "mumbai": ("Maharashtra", "19.0760,72.8777"),
    "jakarta": ("Jakarta", "-6.2088,106.8456"),
    "dublin": ("Leinster", "53.3498,-6.2603"),
    "tel aviv": ("Tel Aviv District", "32.0853,34.7818"),
    "milan": ("Lombardy", "45.4642,9.1900"),
    "osaka": ("Osaka Prefecture", "34.6937,135.5023"),
    "tokyo": ("Tokyo", "35.6762,139.6503"),
    "kuala lumpur": ("Federal Territory of Kuala Lumpur", "3.1390,101.6869"),
    "queretaro": ("Queretaro", "20.5888,-100.3899"),
    "lima": ("Lima", "-12.0464,-77.0428"),
    "warsaw": ("Masovian Voivodeship", "52.2297,21.0122"),
    "singapore": ("", "1.3521,103.8198"),
    "cape town": ("Western Cape", "-33.9249,18.4241"),
    "zurich": ("Zurich", "47.3769,8.5417"),
    "istanbul": ("Istanbul", "41.0082,28.9784"),
    "amsterdam": ("North Holland", "52.3676,4.9041"),
    "london": ("England", "51.5072,-0.1276"),
}

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "roblox-server-locations"})
    with urllib.request.urlopen(req, timeout=45) as response:
        return json.load(response)

def city_key(label):
    label = re.sub(r"\\s*\\([^)]*\\)", "", label).strip()
    return label.split(",")[0].strip().lower()

def parse_list(path, org):
    country = city = None
    records = []
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines):
        if line and not line.startswith((" ", "-")) and i + 1 < len(lines) and re.fullmatch(r"-{3,}", lines[i + 1]):
            country = line.strip()
        elif line.startswith("- ") and not line.startswith("  - "):
            city = line[2:].strip()
        elif line.startswith("  - ") and country and city:
            match = re.match(r"\\s*-\\s*((?:\\d{1,3}\\.){3}\\d{1,3}(?:/\\d{1,2})?)", line)
            if not match:
                continue
            try:
                network = ip.ip_network(match.group(1), strict=False)
            except ValueError:
                continue
            key = city_key(city)
            region, loc = CITY.get(key, ("", ""))
            records.append({
                "cidr": str(network),
                "city": city.split(",")[0].strip(),
                "region": region,
                "country": country,
                "loc": loc,
                "org": org,
            })
    return records

def main():
    with ThreadPoolExecutor(2) as pool:
        aws, reach = (future.result() for future in (
            pool.submit(fetch, AWS), pool.submit(fetch, REACH)
        ))
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
    for prefix in aws["prefixes"]:
        key = (prefix.get("region"), prefix.get("network_border_group"))
        if key in groups:
            try:
                groups[key].add(ip.IPv4Network(prefix["ip_prefix"], strict=False))
            except (KeyError, ValueError, TypeError):
                pass

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out = ["AWS IP Ranges Associated with Roblox Servers", "============================================",
           f"Last updated: {today}", ""]
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
        for network in sorted(nets, key=lambda n: (int(n.network_address), n.prefixlen)):
            out.append(f"  - {network} (AWS)")
            aws_count += 1
        out.append("")
    if not aws_count or not ping_count:
        raise RuntimeError(f"AWS validation failed: {aws_count} CIDRs, {ping_count} pingable IPs")

    aws_text = "\\n".join(out).rstrip() + "\\n"
    roblox_text = Path("roblox-ips.txt").read_text(encoding="utf-8")
    all_text = (
        "Combined Roblox and AWS Server IP Addresses\\n"
        "============================================\\n"
        f"Last updated: {today}\\n\\n"
        "AWS IP RANGES\\n==============\\n\\n"
        + aws_text + "\\n"
        + "ROBLOX-REGISTERED IP RANGES\\n===========================\\n\\n"
        + roblox_text.rstrip() + "\\n"
    )
    Path("aws-ips.txt").write_text(aws_text, encoding="utf-8")
    Path("all-ips.txt").write_text(all_text, encoding="utf-8")

    database = parse_list("aws-ips.txt", "Amazon AWS") + parse_list("roblox-ips.txt", "AS22697 Roblox")
    if not database or len(database) < 10:
        raise RuntimeError(f"Database validation failed: only {len(database)} records")
    database.sort(key=lambda item: (int(ip.ip_network(item["cidr"]).network_address),
                                    ip.ip_network(item["cidr"]).prefixlen, item["org"]))
    Path("database.json").write_text(json.dumps(database, indent=2, ensure_ascii=False) + "\\n", encoding="utf-8")
    print(f"Built aws-ips.txt ({aws_count} AWS ranges, {ping_count} pingable endpoints), "
          f"all-ips.txt, and database.json ({len(database)} records); syncToken={aws['syncToken']}")

if __name__ == "__main__":
    main()
