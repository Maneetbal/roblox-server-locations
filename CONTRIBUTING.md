# Contributing

Thank you for helping improve this community-maintained Roblox server IP reference. Contributions should be reproducible, clearly sourced, and careful to distinguish direct observations from estimates.

This project is unofficial and is not affiliated with Roblox.

## 1. Capture the game-instance address

1. Join a Roblox experience and wait for the game instance to connect.
2. Focus the Roblox game window and press **Ctrl+Shift+F3**.
3. Locate the diagnostic line beginning with `Datacenter fetched IPV4,`.
4. Record the complete line, the IPv4 address, and the observation date.
5. Include a screenshot showing the diagnostic output.

The diagnostic address is the primary evidence that an IP was used by a live game instance.

<img width="671" height="296" alt="Roblox Ctrl+Shift+F3 diagnostic showing a datacenter IPv4 address" src="https://github.com/user-attachments/assets/7bd9fc48-1169-484a-a1a6-01e825cb8f1c" />

## 2. Research the reported location

1. Look up the exact game-instance IP on [iplocation.net](https://www.iplocation.net/).
2. Review **Compare Results by Provider**.
3. Record each distinct location and the provider reporting it. Note providers that return no result.
4. Include the exact lookup URL in the evidence submitted for review.

Example lookup:

[https://www.iplocation.net/ip-lookup?query=128.116.115.33](https://www.iplocation.net/ip-lookup?query=128.116.115.33)

<img width="664" height="873" alt="Example IP geolocation provider results" src="https://github.com/user-attachments/assets/2930e495-3793-48ab-a277-f718da1a0ddf" />

Geolocation results are supporting evidence only. Provider agreement does not prove the physical location of a data center.

## 3. Run latency measurements

Use [Globalping](https://globalping.io/) to run ICMP tests from probes in the locations reported by the geolocation providers.

Record:

- The exact target IP address.
- The Globalping measurement URL.
- Probe location and network/ASN.
- Packet loss and minimum, average, and maximum RTT.
- Any unusual results or excluded outliers, with the reason for exclusion.

<img width="1336" height="700" alt="Example Globalping latency measurement" src="https://github.com/user-attachments/assets/00d3b21a-f689-4d42-8526-79b5f98b7b20" />

If the exact game-instance IP does not respond to ICMP, skip the ping test and record `ICMP=No response`. Do not interpret a timeout as proof that the address is invalid.

If you test a related address instead, identify it as a separate endpoint. For example, `ICMP=.3` may describe a related `.3` address when the game-instance address ends in `.33`. This is indirect location evidence, not a ping result for the instance IP.

## 4. Submit evidence for review

Open a [GitHub issue](https://github.com/Maneetbal/roblox-server-locations/issues) before proposing a new verified entry. Include:

- Exact Ctrl+Shift+F3 diagnostic line and observation date.
- Screenshot of the diagnostic output.
- Exact iplocation.net lookup URL and provider results.
- Globalping measurement URL(s), or a note explaining why ICMP testing was skipped.
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

Use a whole-number rating from 0 to 100. Confidence is a maintainer's assessment of the strength and consistency of the available evidence.

A confidence rating is **not** an accuracy percentage, probability, or guarantee. Record the evidence so other contributors can independently assess the conclusion.

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
