#!/usr/bin/env python3
import ipaddress as ip
import json
import re
import time
import threading
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

AWS = "https://ip-ranges.amazonaws.com/ip-ranges.json"
REACH = "http://ec2-reachability.amazonaws.com/prefixes-ipv4.json"
GEO = "https://photon.komoot.io/api/"
NOMINATIM = "https://nominatim.openstreetmap.org/search"
CACHE_FILE = Path("scripts/cache.json")
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

def fetch(url, timeout=40, attempts=6):
    req = urllib.request.Request(url, headers={"User-Agent": "roblox-server-locations/1.0"})
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code not in (429, 500, 502, 503, 504) or attempt == attempts - 1:
                raise
        except urllib.error.URLError:
            if attempt == attempts - 1:
                raise
        time.sleep(min(2 ** attempt, 20))

def region(nbg):
    return "-".join(nbg.split("-")[:3])

def extract_entries(text):
    """Read either the legacy country/city layout or the flat sorted layout."""
    entries = []
    country = city = None
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if (line and not line.startswith((" ", "-")) and i + 1 < len(lines)
                and re.fullmatch(r"-{3,}", lines[i + 1])):
            country = line.strip()
            city = None
            continue
        if line.startswith("- ") and not line.startswith("  - "):
            city = re.sub(r"\s*\([^)]*\)", "", line[2:]).strip()
            continue
        if not line.startswith("  - "):
            continue

        raw = line[4:].strip()
        metadata = re.search(r"\s+\[City=(.*?); Country=(.*?)\]\s*$", raw)
        entry_city, entry_country = city, country
        if metadata:
            entry_city, entry_country = metadata.group(1).strip(), metadata.group(2).strip()
            raw = raw[:metadata.start()].rstrip()

        match = re.match(
            r"((?:\d{1,3}\.){3}\d{1,3}(?:/\d{1,2})?)(.*)$",
            raw,
        )
        if not match or not entry_city or not entry_country:
            continue
        try:
            network = ip.ip_network(match.group(1), strict=False)
        except ValueError:
            continue
        entries.append({
            "network": network,
            "address": match.group(1),
            "note": match.group(2).strip(),
            "raw": raw,
            "city": entry_city,
            "country": entry_country,
        })
    return entries


def entry_sort_key(entry):
    network = entry["network"]
    return (int(network.network_address), network.prefixlen, str(network),
            entry["country"], entry["city"], entry.get("display", entry.get("raw", "")))


def render_flat_file(title, separator, today, entries):
    """Render IP rows globally sorted by numeric network address."""
    out = [title, separator, f"Last updated: {today}", ""]
    for entry in sorted(entries, key=entry_sort_key):
        out.append(
            f"  - {entry['display']} [City={entry['city']}; Country={entry['country']}]"
        )
    return "\n".join(out).rstrip() + "\n"


def sort_existing_location_file(text):
    """Flatten and sort a manually maintained country/city IP file."""
    lines = text.splitlines()
    header = lines[:3]
    entries = extract_entries(text)
    footer = []
    for i, line in enumerate(lines[3:], 3):
        if not line.strip():
            if footer:
                footer.append("")
            continue
        if i + 1 < len(lines) and re.fullmatch(r"-{3,}", lines[i + 1]):
            continue
        if re.fullmatch(r"-{3,}", line):
            continue
        if line.startswith("- ") and not line.startswith("  - "):
            continue
        if line.startswith("  - "):
            continue
        footer.append(line)
    while footer and not footer[0].strip():
        footer.pop(0)
    while footer and not footer[-1].strip():
        footer.pop()
    out = header + [""]
    for entry in sorted(entries, key=entry_sort_key):
        out.append(
            f"  - {entry['raw']} [City={entry['city']}; Country={entry['country']}]"
        )
    if footer:
        out.extend(["", *footer])
    return "\n".join(out).rstrip() + "\n"


def parse_list(text, org):
    records = []
    for entry in extract_entries(text):
        network = entry["network"]
        records.append({
            "cdir": str(network),
            "city": entry["city"].split(",")[0].strip(),
            "geo_city": entry["city"],
            "country": entry["country"],
            "org": org,
        })
    return records


def geocode(key):
    global _last_nominatim
    city, country = key
    url = GEO + "?" + urllib.parse.urlencode({"q": f"{city}, {country}", "limit": 1})
    try:
        feature = fetch(url, timeout=8, attempts=1).get("features", [])
        if feature:
            p = feature[0].get("properties", {})
            state = p.get("state") or p.get("state_district") or p.get("county") or p.get("city") or p.get("district") or ""
            if state:
                lon, lat = feature[0]["geometry"]["coordinates"]
                return key, (state, f"{lat:.5f},{lon:.5f}")
    except urllib.error.URLError:
        pass

    # Use Nominatim when Photon is unavailable or has no region.
    with _geo_lock:
        delay = 1.1 - (time.monotonic() - _last_nominatim)
        if delay > 0:
            time.sleep(delay)
        fallback = NOMINATIM + "?" + urllib.parse.urlencode({
            "q": f"{city}, {country}", "format": "jsonv2", "limit": 1
        })
        result = fetch(fallback, timeout=12, attempts=1)
        _last_nominatim = time.monotonic()
    if not result:
        raise RuntimeError(f"Could not geocode {city}, {country} with Photon or Nominatim")
    item = result[0]
    address = item.get("address", {})
    state = (address.get("state") or address.get("state_district") or address.get("county")
             or address.get("municipality") or address.get("city") or address.get("town")
             or address.get("village") or address.get("city_district") or city.split(",")[0])
    return key, (state.strip(), f"{float(item['lat']):.5f},{float(item['lon']):.5f}")
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

    # Build globally sorted AWS and combined lists. Location metadata stays on
    # each row so sorting is independent of country/city grouping.
    all_entries = []
    aws_entries = []

    def add_entry(country, city, address, label, sort_address=None):
        network = ip.ip_network(sort_address or address, strict=False)
        entry = {
            "network": network,
            "display": f"{address} ({label})",
            "city": city,
            "country": country,
        }
        all_entries.append(entry)
        if label.startswith("AWS"):
            aws_entries.append(entry)

    aws_count = ping_count = 0
    for country, city, *nbgs in LOCATIONS:
        for n in nbgs:
            r = region(n)
            if r == n and r in ping:
                add_entry(country, city, f"{ping[r]}/32", "AWS, PINGABLE")
                ping_count += 1
                break
        nets = set()
        for n in nbgs:
            nets.update(ip.collapse_addresses(groups[(region(n), n)]))
        for net in nets:
            add_entry(country, city, str(net), "AWS")
            aws_count += 1
    if not aws_count or not ping_count:
        raise RuntimeError(f"AWS validation failed: {aws_count} CIDRs, {ping_count} pingable IPs")

    roblox_source_text = Path("roblox-ips.txt").read_text(encoding="utf-8")
    roblox_date_match = re.search(r"^Last updated:\\s*(.+)$", roblox_source_text, re.MULTILINE)
    roblox_date = roblox_date_match.group(1).strip() if roblox_date_match else today
    roblox_entries = extract_entries(roblox_source_text)
    roblox_flat_entries = []
    roblox_count = 0
    for entry in roblox_entries:
        network = entry["network"]
        note = entry["note"]
        label = "Roblox, PINGABLE" if "PINGABLE" in note.upper() else "Roblox"
        display = f"{network}{(' ' + note) if note else ''}"
        add_entry(entry["country"], entry["city"], display, label, str(network))
        roblox_flat_entries.append({
            "network": network,
            "display": entry["raw"],
            "city": entry["city"],
            "country": entry["country"],
        })
        roblox_count += 1

    all_text = render_flat_file(
        "Combined Roblox and AWS Server IP Addresses",
        "============================================",
        today,
        all_entries,
    )
    aws_text = render_flat_file(
        "AWS IP Ranges Associated with Roblox Servers",
        "============================================",
        today,
        aws_entries,
    )
    roblox_flat_text = render_flat_file(
        "Roblox Roblox Server IP Addresses",
        "============================================",
        roblox_date,
        roblox_flat_entries,
    )

    records = parse_list(aws_text, "AWS") + parse_list(roblox_source_text, "Roblox")
    keys = {(x["geo_city"], x["country"]) for x in records}
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
        candidates = (
            cache["locations"].get(f"{city}|{country}"),
            cache["locations"].get(f"{city.split(',')[0].strip()}|{country}"),
        )
        value = next((
            item for item in candidates
            if isinstance(item, dict)
            and isinstance(item.get("region"), str) and item["region"].strip()
            and isinstance(item.get("loc"), str) and item["loc"]
        ), None)
        if value:
            locations[(city, country)] = (value["region"].strip(), value["loc"])

    missing = keys - locations.keys()
    if missing:
        print(f"Geocoding {len(missing)} uncached locations; {len(locations)} loaded from cache.")
        with ThreadPoolExecutor(2) as pool:
            jobs = [pool.submit(geocode, key) for key in sorted(missing)]
            fresh = {}
            for done, future in enumerate(as_completed(jobs), 1):
                key, value = future.result()
                fresh[key] = value
                city, country = key
                state, coords = value
                cache["locations"][f"{city}|{country}"] = {"region": state, "loc": coords}
                CACHE_FILE.write_text(
                    json.dumps(cache, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
                )
                print(f"Geocoded {done}/{len(jobs)}: {city}, {country}", flush=True)
        locations.update(fresh)
    else:
        print(f"Loaded all {len(locations)} geocoding results from cache.")

    for item in records:
        item["region"], coords = locations[(item["geo_city"], item["country"])]
        lat, lon = map(float, coords.split(","))
        item["loc"] = f"{lat:.4f},{lon:.4f}"
        del item["geo_city"]
        item["region"] = item["region"]
    records = [{
        "cdir": x["cdir"], "city": x["city"], "region": x["region"],
        "country": x["country"], "loc": x["loc"], "org": x["org"]
    } for x in records]
    records.sort(key=lambda x: (int(ip.ip_network(x["cdir"]).network_address),
                                ip.ip_network(x["cdir"]).prefixlen, x["org"]))
    if len(records) < 10:
        raise RuntimeError(f"Database validation failed: only {len(records)} records")

    Path("aws-ips.txt").write_text(aws_text, encoding="utf-8")
    Path("all-ips.txt").write_text(all_text, encoding="utf-8")
    Path("roblox-ips.txt").write_text(roblox_flat_text, encoding="utf-8")
    verified_text = sort_existing_location_file(Path("roblox-verified-ips.txt").read_text(encoding="utf-8"))
    Path("roblox-verified-ips.txt").write_text(verified_text, encoding="utf-8")
    database = "\n".join(
        json.dumps(item, indent=2, ensure_ascii=False) for item in records
    ) + "\n"
    Path("database.json").write_text(database, encoding="utf-8")
    print(f"Built {aws_count} AWS ranges, {ping_count} pingable IPs, and {len(records)} database records; syncToken={aws['syncToken']}")

if __name__ == "__main__":
    main()
