# Maintaining the Roblox server IP lists

These files are community-maintained and are not an official Roblox inventory. Keep the three datasets, the verification ledger, and the README synchronized:

- `roblox-ips.txt` — Roblox-registered entries.
- `aws-ips.txt` — AWS entries associated with Roblox use.
- `all-ips.txt` — combined compatibility list.
- `verified-ips.txt` — individual game-instance IPs with evidence and confidence notes.

## Identify the game-instance IP

1. Join a Roblox experience and wait until the game instance is connected.
2. With the Roblox game window focused, press **Ctrl+Shift+F3**.
3. Find the diagnostic line beginning with **`Datacenter fetched IPV4,`**. For example: **`Datacenter fetched IPV4, 128.116.115.33`**.
4. Record the IPv4 address exactly as displayed, along with the date, experience/session context if useful, and the fact that it came from the Ctrl+Shift+F3 game-instance diagnostics.
5. Open GlassWire and inspect the Roblox Player/game-instance process connections. Record whether it shows the same remote IPv4 address. Treat this as an independent cross-check.

**Evidence priority:** the Ctrl+Shift+F3 **Datacenter fetched IPV4** result is the preferred direct indicator of the game instance. A matching GlassWire process connection strengthens the record. GlassWire-only observations are useful, but label them as such and seek the in-game diagnostic result before marking an address fully verified.

## Verify the location

1. Open [iplocation.net](https://www.iplocation.net/) and look up the exact IPv4 address.
2. Inspect **Compare Results by Provider**. Record the location and ISP/organization returned by each provider, including providers that return no data. Do not silently discard conflicting results.
3. Build a list of every distinct city/region shown in that section.
4. In [Globalping](https://globalping.io/), run ICMP pings to the exact IP from probes located in **each** of those locations. Where possible, use more than one probe per location. Record the probe's displayed city, ASN/provider, packet loss, and min/average/max RTT.
5. Prefer an exact-IP ping. If the game-instance IP blocks ICMP, record that fact. A ping to a related address (for example, another address ending in `.3` in the same subnet) is **indirect evidence only** and must be listed separately. It cannot prove the exact game-instance IP is reachable or physically located there.
6. Compare the location-provider results with the Globalping probe results. Record disagreements and retain uncertainty instead of forcing a single location.

### Example: 128.116.115.33

The supplied iplocation.net **Compare Results by Provider** results report **Seattle, Washington** for IP2Location, DB-IP, IPAPI.co, IPapi.is, IPData, IPGeolocation.io, IPinfo, IPLocate.io, Ipregistry, and Criminal IP. IPBase returned no data.

The supplied Globalping test was to **128.116.115.3**, not the game-instance address `128.116.115.33`:

- Probe location: Seattle, WA, US
- ASN/provider: AS63949 — Akamai Connected Cloud
- Target: `128.116.115.3`
- Packets: 3 sent, 3 received, 0% loss
- RTT: min 0.394 ms, average 0.437 ms, max 0.469 ms

This supports Seattle as a location for the related `128.116.115.3` endpoint and is consistent with the provider results for the `128.116.115.0/24` range. It is **not** an exact-IP ping of `128.116.115.33`. Keep the two addresses and their evidence separate in `verified-ips.txt`.

## Evidence and classification

1. Record observable game-instance evidence. An ICMP reply alone does not establish Roblox use.
2. Check the network registrant with the relevant Regional Internet Registry (RIR) RDAP service. Put Roblox-registered networks in `roblox-ips.txt`. If a Roblox-registered block is hosted on AWS, note that fact; classify it by registrant to avoid duplicate listing.
3. For AWS-owned addresses, compare the prefix with [AWS public IP ranges](https://ip-ranges.amazonaws.com/ip-ranges.json) and use the [AWS geo-IP feed](https://ip-ranges.amazonaws.com/geo-ip-feed.csv) as a location hint.
4. Treat city names as estimates unless supported by independent network measurements. Geo-IP data and registry records do not identify a physical facility.
5. Keep intentional overlaps when they serve a distinct purpose. For example, `3.80.0.0/32` is an ICMP test probe within `3.80.0.0/12`; it is not a duplicate.
6. Do not add every AWS region automatically. Add only regions with evidence of Roblox use and maintainer approval.

## Confidence labels

- **High — game-instance association:** Ctrl+Shift+F3 reports the exact IP and GlassWire independently shows the Roblox game process connecting to it.
- **Medium — game-instance association:** one direct source is available, but the independent cross-check is missing.
- **Low / candidate:** evidence is indirect, ambiguous, or limited to registration, geo-IP, subnet similarity, or a ping response.
- **Location confidence is separate:** provider agreement and geographically distributed pings support a location estimate; they do not prove a physical data-center address.

Do not use “100% confidence” for physical location or permanent assignment. IP allocations, routes, and service roles can change.

## Updates

- Recheck records and observed endpoints periodically; note the source and date.
- Remove an entry only when there is sufficient evidence it is no longer relevant.
- Deduplicate exact repeated CIDRs when they refer to the same listed range. If locations conflict, retain the best-supported label and record the basis in the changelog.
- When the data changes, update all three list files, the verification ledger, the README, their dates, and `CHANGELOG.md`.
- Preserve `all-ips.txt` as the combined compatibility list.
