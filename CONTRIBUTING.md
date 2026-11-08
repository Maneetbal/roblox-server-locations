# Contributing Roblox Server IPs and Location Evidence

Help improve this community-maintained **Roblox server IP address and location database**. We welcome reproducible game-instance IP observations, Roblox server IP range corrections, city-level location research, and Globalping latency evidence. Contributions must be clearly sourced and must distinguish direct observations from estimates.

This project is unofficial and is not affiliated with Roblox.

## 1. Capture a Roblox game-instance IP address

1. Join a Roblox experience and wait for the game instance to connect.
2. Focus the Roblox game window and press **Ctrl+Shift+F3**.
3. Locate the diagnostic line beginning with `Datacenter fetched IPV4,`.
4. Record the complete line, the IPv4 address, and the observation date.
5. Include a screenshot showing the diagnostic output.

The diagnostic address is the primary evidence that an IP was used by a live game instance.

<img width="671" height="296" alt="Roblox Ctrl+Shift+F3 diagnostic showing a datacenter IPv4 address" src="https://github.com/user-attachments/assets/7bd9fc48-1169-484a-a1a6-01e825cb8f1c" />

## 2. Research the Roblox server IP location

1. Look up the exact game-instance IP on [iplocation.net](https://www.iplocation.net/).
2. Review **Compare Results by Provider**.
3. Record each distinct location and the provider reporting it. Note providers that return no result.
4. Include the exact lookup URL in the evidence submitted for review.

Example lookup:

[https://www.iplocation.net/ip-lookup?query=128.116.115.33](https://www.iplocation.net/ip-lookup?query=128.116.115.33)

<img width="664" height="873" alt="Example IP geolocation provider results" src="https://github.com/user-attachments/assets/2930e495-3793-48ab-a277-f718da1a0ddf" />

Geolocation results are supporting evidence only. Provider agreement does not prove the physical location of a data center.

**San Mateo result caveat:** Some geolocation providers may list San Mateo, California. Roblox does not have data centers in San Mateo, so you can safely ignore that provider result or treat it as if the provider did not respond. Do not use a San Mateo result as evidence for the proposed location.

<img width="672" height="894" alt="Example iplocation.net results showing San Mateo as a reported location" src="https://github.com/user-attachments/assets/ac24ba6c-144e-42ec-8c71-123809fb80b6" />

## 3. Measure Roblox server IP latency with Globalping

Use [Globalping](https://globalping.io/) to run ICMP tests from probes in the locations reported by the geolocation providers.

Record:

- The exact target IP address.
- The Globalping measurement URL.
- Probe location and network/ASN.
- Packet loss and minimum, average, and maximum RTT for each probe.
- Which probe had the **lowest average RTT in each candidate city**.
- Any unusual results or excluded outliers, with the reason for exclusion.

For confidence scoring, compare the **average RTT of the single lowest-latency eligible probe in the candidate city**. Do not average the results from all probes in that city. The latency threshold is based on the lowest-latency node's average RTT, not the city-wide average.

Akamai Connected Cloud probes (for example, AS63949) can be particularly useful on Globalping because they provide additional network vantage points. They are recommended when available, but they are not required; use other suitable probes as well.

<img width="1336" height="700" alt="Example Globalping latency measurement" src="https://github.com/user-attachments/assets/00d3b21a-f689-4d42-8526-79b5f98b7b20" />

If the exact game-instance IP does not respond to ICMP, skip the ping test and record `ICMP=No response`. Do not interpret a timeout as proof that the address is invalid.

If you test a related address instead, identify it as a separate endpoint. For example, `ICMP=.3` may describe a related `.3` address when the game-instance address ends in `.33`. This is indirect location evidence, not a ping result for the instance IP.

## 4. Check Roblox's edge-term hostname

Look for a Roblox hostname matching this pattern:

```text
edge-term4-<identifier>.roblox.com
```

For the exact game-instance IPv4 address being evaluated:

1. Find the hostname whose identifier corresponds to the candidate location.
2. Query its DNS A record.
3. Record the hostname, the DNS answer, the lookup method, and the date checked.
4. Confirm that the A record contains the **exact game-instance IP**. An address elsewhere in the same /24 is not an exact match.
5. Compare the identifier's location with the city supported by the geolocation and latency evidence.

A matching hostname is the final 1% of the location-confidence assessment only when it resolves to the exact IP and its location identifier agrees with the independently selected city. Do not extend a hostname match to an entire CIDR range or to other IPs in that range.

**When hostname and latency disagree:** The measured location takes priority over the hostname identifier. For example, if a hostname identifies Frankfurt but the lowest-latency eligible probe is in Amsterdam, and the other location evidence supports Amsterdam, list the location as Amsterdam. The conflicting hostname does not qualify for the 100% rating; with a lowest-node average RTT of 1.5 ms or less, the location can be rated 99%.

A missing hostname, a hostname that does not resolve to the exact IP, or a hostname with a conflicting location does not earn the hostname point.

## 5. Submit evidence for review

Open a [GitHub issue](https://github.com/Maneetbal/roblox-server-locations/issues) before proposing a new verified entry. Include:

- Exact Ctrl+Shift+F3 diagnostic line and observation date.
- Screenshot of the diagnostic output.
- Exact iplocation.net lookup URL and provider results.
- Globalping measurement URL(s), probe cities/networks, and the lowest average RTT probe in each candidate city, or a note explaining why ICMP testing was skipped.
- Roblox `edge-term4` hostname, DNS A-record result, and lookup date, if one is found. State explicitly when no exact match is found.
- Proposed country, city/region, and CIDR range, if known.

Do not add an observation to the verified list until it has been reviewed.

## Entry format

The verification ledger uses this format:

```text
United States
-------------
- Seattle, WA
  - 128.116.115.0/24 (Confidence=100) (ICMP=.3) (Instance=.33)
```

- `Instance=.33` identifies the game-instance address reported by Roblox.
- `ICMP=.3` identifies a separate related address used for the ping measurement. It does not mean the instance address responded to ICMP.
- Use `ICMP=No response` when the exact address does not answer ICMP and no related endpoint is being reported.

## Confidence ratings

Use a whole-number rating from 0 to 100. Confidence is a maintainer's assessment of the reliability of the listed **location**, not an accuracy percentage, probability, or guarantee.

Use the average RTT of the **single lowest-latency eligible Globalping probe in the selected city** for the latency tier. Do not use the average across all probes in that city.

| Confidence | Requirement |
| ---: | --- |
| **100%** | All existing location checks pass; the selected city's lowest-latency eligible probe averages **1.5 ms or less**; and an `edge-term4-<identifier>.roblox.com` hostname resolves to the exact IP being evaluated and identifies the same city. |
| **99%** | The other location checks support the selected city and its lowest-latency probe averages **1.5 ms or less**, but no matching Roblox hostname is found, it does not resolve to the exact IP, or its identifier conflicts with the measured city. |
| **95%** | The selected city's lowest-latency eligible probe averages **more than 1.5 ms but less than 2.0 ms**. |
| **90%** | The selected city's lowest-latency eligible probe averages **2.0 ms or more**. |

The 95% and 90% latency tiers take precedence over the 99% and 100% tiers. A matching hostname cannot raise an entry to 100% when its selected city's lowest-latency probe averages more than 1.5 ms. The 90% tier is the lowest latency tier currently defined; reassess the entry if other evidence suggests the location itself is wrong.

## Network classification

- Put ranges registered to Roblox in `roblox-ips.txt`. Verify registration using the relevant Regional Internet Registry (RIR) RDAP service.
- If a Roblox-registered range is hosted on AWS, classify it by registrant and note its AWS hosting where relevant.
- For AWS-owned ranges, compare the prefix with the [AWS public IP ranges](https://ip-ranges.amazonaws.com/ip-ranges.json). The [AWS geolocation feed](https://ip-ranges.amazonaws.com/geo-ip-feed.csv) may be used as a location reference.
- Add AWS ranges only when there is evidence of Roblox use; do not include every AWS region automatically.
- Preserve intentional overlaps when they serve different purposes. For example, `3.80.0.0/32` is a latency-test endpoint within `3.80.0.0/12`, not an accidental duplicate.

## Maintaining the lists

When an approved change is made:

1. Update the relevant source list and `all-ips.txt`.
2. Update `roblox-verified-ips.txt` when verified game-instance evidence changes.
3. Keep the README and file dates consistent with the data.
4. Remove duplicates only when they represent the same network entry and purpose.
5. Reassess entries when new evidence conflicts with the existing location or classification.

Keep changes focused and include the supporting evidence in the issue or commit description.
