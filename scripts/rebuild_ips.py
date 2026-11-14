#!/usr/bin/env python3
import ipaddress as ip
import json
import re
import time
import threading
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

AWS = "https://ip-ranges.amazonaws.com/ip-ranges.json"
REACH = "http://ec2-reachability.amazonaws.com/prefixes-ipv4.json"
GEO = "https://photon.komoot.io/api/"
NOMINATIM = "https://nominatim.openstreetmap.org/search"
CACHE_FILE = Path("geocode-cache.json")
_geo_lock = threading.Lock()
_last_nominatim = 0
LOCATIONS = [
    ("United States", "Ashburn, VA", "us-east-1"),
    ("United States", "Boardman, OR", "us-west-2"),
    ("United States", "Columbus, OH", "us-east-2"),
    ("United States", "Miami, FL", "us-east-1-mia-1", "us-east-1-mia-2", "us-east-1-wl1-mia-wlz-1"),
    ("United States", "San Jose, CA", "us-west-1"),
    ("Argentina", "Buenos Aires, AR", "us-east-1-bue-1"),
    ("Brazil", "Sao Paulo, BR", "sa-east-1"),
    ("Chile", "Santiago, CL", "us-east-1-scl-1"),
    ("Germany", "Frankfurt, DE", "eu-central-1"),
    ("Greece", "Athens, GR", "eu-central-1-ath-1"),
    ("India", "Mumbai, IN", "ap-south-1"),
    ("Indonesia", "Jakarta, ID", "ap-southeast-3"),
    ("Ireland", "Dublin, IE", "eu-west-1"),
    ("Israel", "Tel Aviv, IL", "il-central-1"),
    ("Italy", "Milan, IT", "eu-south-1"),
    ("Japan", "Osaka, JP", "ap-northeast-3"),
    ("Malaysia", "Kuala Lumpur, MY", "ap-southeast-5"),
    ("Mexico", "Queretaro, MX", "mx-central-1", "us-east-1-qro-1"),
    ("Peru", "Lima, PE", "us-east-1-lim-1"),
    ("Poland", "Warsaw, PL", "eu-central-1-waw-1"),
    ("Singapore", "Singapore, SG", "ap-southeast-1"),
    ("South Africa", "Cape Town, ZA", "af-south-1"),
    ("Switzerland", "Zurich, CH", "eu-central-2"),
    ("Turkey", "Istanbul, TR", "eu-central-1-ist-1"),
]

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "roblox-server-locations/1.0"})
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code not in (429, 500, 502, 503, 504) or attempt == 5:
                raise
        except urllib.error.URLError:
            if attempt == 5:
                raise
        time.sleep(min(2 ** attempt, 20))

def region(nbg):
    return "-".join(nbg.split("-")[:3])

def parse_list(text, org):
    country = city = None
    records = []
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line and not line.startswith((" ", "-")) and i + 1 < len(lines) and re.fullmatch(r"-{3,}", lines[i + 1]):
            country = line.strip()
        elif line.startswith("- ") and not line.startswith("  - "):
            city = re.sub(r"\s*\([^)]*\)", "", line[2:]).split(",")[0].strip()
        elif line.startswith("  - ") and country and city:
            m = re.match(r"\s*-\s*((?:\d{1,3}\.){3}\d{1,3}(?:/\d{1,2})?)", line)
            if m:
                try:
                    records.append({"cidr": str(ip.ip_network(m[1], strict=False)),
                                    "city": city, "country": country, "org": org})
                except ValueError:
                    pass
    return records

def geocode(key):
    global _last_nominatim
    city, country = key
    url = GEO + "?" + urllib.parse.urlencode({"q": f"{city}, {country}", "limit": 1})
    try:
        feature = fetch(url).get("features", [])
        if feature:
            p = feature[0].get("properties", {})
            lon, lat = feature[0]["geometry"]["coordinates"]
            return key, (p.get("state") or p.get("county") or "", f"{lat:.5f},{lon:.5f}")
    except urllib.error.URLError:
        pass

    # Use Nominatim if Photon is unavailable.
    with _geo_lock:
        delay = 1.1 - (time.monotonic() - _last_nominatim)
        if delay > 0:
            time.sleep(delay)
        fallback = NOMINATIM + "?" + urllib.parse.urlencode({
            "q": f"{city}, {country}", "format": "jsonv2", "limit": 1
        })
        result = fetch(fallback)
        _last_nominatim = time.monotonic()
    if not result:
        raise RuntimeError(f"Could not geocode {city}, {country} with Photon or Nominatim")
    item = result[0]
    address = item.get("address", {})
    state = address.get("state") or address.get("state_district") or address.get("county") or ""
    return key, (state, f"{float(item['lat']):.5f},{float(item['lon']):.5f}")
def main():
    with ThreadPoolExecutor(2) as pool:
        aws, reach = (f.result() for f in (pool.submit(fetch, AWS), pool.submit(fetch, REACH)))
    if not aws.get("syncToken") or not isinstance(aws.get("prefixes"), list) or not isinstance(reach, list):
        raise RuntimeError("Invalid AWS feeds")

    ping = {}
    for item in reach:
        if isinstance(item, dict):
            for r, values in item.items():
                if r not in ping and isinstance(values, dict):
                    for value in values.values():
                        try:
                            ping[r] = str(ip.IPv4Address(value))
                            break
                        except (ValueError, TypeError):
                            pass

    wanted = {(region(n), n) for row in LOCATIONS for n in row[2:]}
    groups = {key: set() for key in wanted}
    for p in aws["prefixes"]:
        key = (p.get("region"), p.get("network_border_group"))
        if key in groups:
            try:
                groups[key].add(ip.IPv4Network(p["ip_prefix"], strict=False))
            except (KeyError, ValueError, TypeError):
                pass

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out = ["AWS IP Ranges Associated with Roblox Servers", "============================================",
           f"Last updated: {today}", ""]
    aws_count = ping_count = 0
    for country, city, *nbgs in LOCATIONS:
        out += [country, "-" * len(country), f"- {city}"]
        for n in nbgs:
            r = region(n)
            if r == n and r in ping:
                out.append(f"  - {ping[r]}/32 (PINGABLE)")
                ping_count += 1
                break
        nets = set()
        for n in nbgs:
            nets.update(ip.collapse_addresses(groups[(region(n), n)]))
        for net in sorted(nets, key=lambda x: (int(x.network_address), x.prefixlen)):
            out.append(f"  - {net} (AWS)")
            aws_count += 1
        out.append("")
    if not aws_count or not ping_count:
        raise RuntimeError(f"AWS validation failed: {aws_count} CIDRs, {ping_count} pingable IPs")

    aws_text = "\n".join(out).rstrip() + "\n"
    roblox_text = Path("roblox-ips.txt").read_text(encoding="utf-8")
    all_text = ("Combined Roblox and AWS Server IP Addresses\n"
                "============================================\n"
                f"Last updated: {today}\n\nAWS IP RANGES\n==============\n\n"
                + aws_text + "\nROBLOX-REGISTERED IP RANGES\n===========================\n\n"
                + roblox_text.rstrip() + "\n")

    records = parse_list(aws_text, "AWS") + parse_list(roblox_text, "Roblox")
    keys = {(x["city"], x["country"]) for x in records}
    cache = {"version": 1, "locations": {}}
    if CACHE_FILE.exists():
        try:
            loaded = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
            if isinstance(loaded, dict) and isinstance(loaded.get("locations"), dict):
                cache = loaded
        except (OSError, json.JSONDecodeError):
            print("Geocode cache unreadable; rebuilding it.")

    locations = {}
    for city, country in keys:
        value = cache["locations"].get(f"{city}|{country}")
        if (isinstance(value, dict) and isinstance(value.get("region"), str)
                and isinstance(value.get("loc"), str)):
            locations[(city, country)] = (value["region"], value["loc"])

    missing = keys - locations.keys()
    if missing:
        print(f"Geocoding {len(missing)} uncached locations; {len(locations)} loaded from cache.")
        with ThreadPoolExecutor(2) as pool:
            fresh = dict(f.result() for f in (pool.submit(geocode, key) for key in missing))
        locations.update(fresh)
        for (city, country), (state, coords) in fresh.items():
            cache["locations"][f"{city}|{country}"] = {"region": state, "loc": coords}
        CACHE_FILE.write_text(
            json.dumps(cache, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
    else:
        print(f"Loaded all {len(locations)} geocoding results from cache.")

    for item in records:
        item["region"], item["loc"] = locations[(item["city"], item["country"])]
    records.sort(key=lambda x: (int(ip.ip_network(x["cidr"]).network_address),
                                ip.ip_network(x["cidr"]).prefixlen, x["org"]))
    if len(records) < 10:
        raise RuntimeError(f"Database validation failed: only {len(records)} records")

    Path("aws-ips.txt").write_text(aws_text, encoding="utf-8")
    Path("all-ips.txt").write_text(all_text, encoding="utf-8")
    Path("database.json").write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Built {aws_count} AWS ranges, {ping_count} pingable IPs, and {len(records)} database records; syncToken={aws['syncToken']}")

if __name__ == "__main__":
    main()
