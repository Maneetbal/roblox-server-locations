# Maintaining the Roblox server IP lists

These files are community-maintained and are not an official Roblox inventory. Keep the three datasets, the verification ledger, and the README synchronized:

- `roblox-ips.txt` — Roblox-registered entries.
- `aws-ips.txt` — AWS entries associated with Roblox use.
- `all-ips.txt` — combined compatibility list.
- `roblox-verified-ips.txt` — game-instance IPs grouped by location, with confidence and ICMP/instance evidence.

## Identify the game-instance IP

1. Join a Roblox experience and wait until the game instance is connected.
2. With the Roblox game window focused, press **Ctrl+Shift+F3**.
3. Find the diagnostic line beginning with **`Datacenter fetched IPV4,`**. For example: **`Datacenter fetched IPV4, 128.116.115.33`**.
4. Record the IPv4 address exactly as displayed, along with the date and the exact diagnostic text. This is the primary game-instance evidence.

Do not substitute a website connection, a nearby address, or another address in the same subnet for the in-game diagnostic result.

## Verify the location

1. Open [iplocation.net](https://www.iplocation.net/) and look up the exact IPv4 address.
2. Inspect **Compare Results by Provider**. Record every distinct city/region shown and the providers reporting it, including providers that return no data. Provider agreement is useful corroboration, not proof of a physical data-center address.
3. For each distinct location shown, use [Globalping](https://globalping.io/) to run an ICMP ping to the exact game-instance IP from a probe in that location. Record probe location, ASN/provider, packet loss, and min/average/max RTT.
4. **If the exact IP does not respond to ICMP, skip the ping test for that IP.** Record `ICMP=No response` (or `ICMP=Skipped`) and flag it for maintainer verification. Do not substitute a different IP and present its response as if it came from the game-instance IP.
5. If a related address is tested instead, record it separately as indirect evidence, for example `ICMP=.3` when the instance address is `.33`. A related address responding to ICMP does not prove that the instance IP responds or is physically located at that probe.
6. Compare provider locations and network measurements. Preserve conflicting results and uncertainty rather than forcing a location.

## Example: Seattle

```text
United States
-------------
- Seattle, WA
  - 128.116.115.0/24 (Confidence=100) (ICMP=.3) (Instance=.33)
```

For this entry, `Instance=.33` identifies the game-instance endpoint reported by the in-game diagnostic. `ICMP=.3` identifies the separate related endpoint used for the Seattle ping measurement; it is not an exact-IP ping of `.33`.

## Confidence percentages

- Use a whole-number percentage from 0 to 100.
- **100 is the highest confidence rating.** The Seattle entry above is assigned 100 as requested.
- Confidence expresses how strongly the available evidence supports the classification/location judgment. **It is not an accuracy percentage, probability of being correct, or guarantee.** A contributor can be highly confident and still be wrong.
- Confidence is a maintainer assessment. Record the evidence and date so others can independently review it.
- A location estimate is not proof of a physical data-center address or a permanent IP assignment.

## Evidence and classification

1. Use the Ctrl+Shift+F3 `Datacenter fetched IPV4` output as the primary evidence that an IP belongs to a live game instance.
2. Check the network registrant with the relevant Regional Internet Registry (RIR) RDAP service. Put Roblox-registered networks in `roblox-ips.txt`. If a Roblox-registered block is hosted on AWS, note that fact; classify it by registrant to avoid duplicate listing.
3. For AWS-owned addresses, compare the prefix with [AWS public IP ranges](https://ip-ranges.amazonaws.com/ip-ranges.json) and use the [AWS geo-IP feed](https://ip-ranges.amazonaws.com/geo-ip-feed.csv) as a location hint.
4. Treat city names as estimates. Geo-IP data, registry records, and latency measurements do not identify a physical facility.
5. Keep intentional overlaps when they serve a distinct purpose. For example, `3.80.0.0/32` is an ICMP test probe within `3.80.0.0/12`; it is not a duplicate.
6. Do not add every AWS region automatically. Add only regions with evidence of Roblox use and maintainer approval.

## Updates

- Recheck records and observed endpoints periodically; note the source and date.
- If an IP does not answer ICMP, skip that ping test and report the IP for maintainer verification; do not assume it is invalid.
- Remove an entry only when there is sufficient evidence it is no longer relevant.
- Deduplicate exact repeated CIDRs when they refer to the same listed range. If locations conflict, retain the best-supported label and record the basis in the changelog.
- When the data changes, update all three list files, the verification ledger, the README, their dates, and `CHANGELOG.md`.
- Preserve `all-ips.txt` as the combined compatibility list.
