# Roblox Server IP Addresses, Locations, and Datacenter Reference

Find **Roblox game server IP ranges**, estimated **Roblox server locations**, and documented **game-instance IP observations** in one community-maintained reference. The project organizes known Roblox-associated IPv4 ranges by country and city, separates Roblox-registered networks from AWS-associated ranges, and provides evidence notes to help readers judge location reliability.

> **Unofficial community project:** This repository is not affiliated with, endorsed by, or maintained by Roblox. City labels are estimates based on available evidence; they are not confirmation of a physical Roblox data center.

## Quick links: Roblox server IP lists

| File | What it contains | Use it for |
| --- | --- | --- |
| [`roblox-verified-ips.txt`](roblox-verified-ips.txt) | Game-instance IP observations, estimated locations, ICMP endpoint notes, and location confidence | Best starting point when looking for documented Roblox game-server IPs and location evidence |
| [`roblox-ips.txt`](roblox-ips.txt) | IPv4 ranges registered to Roblox, grouped by estimated location | Finding Roblox-registered server IP ranges by city or region |
| [`aws-ips.txt`](aws-ips.txt) | AWS-owned ranges associated with Roblox server use | Reviewing Roblox-associated Amazon Web Services IP ranges |
| [`all-ips.txt`](all-ips.txt) | Combined Roblox-registered and AWS-associated IP range list | Searching the broadest consolidated list of Roblox-associated IPs |

**Looking for a specific city?** Open the relevant list and use your browser's Find feature (Ctrl+F) to search for a city, country, or IP prefix.

## JSON API

The repository publishes a compact static JSON API through GitHub Pages. See [`api/README.md`](api/README.md) for the endpoint and six-field response format (`ip`, `city`, `region`, `country`, `loc`, `org`). The API is generated from `all-ips.txt` by GitHub Actions; each record preserves its source IPv4 address or CIDR range, and clients download and cache the JSON array for local IP/CIDR matching.

## How to identify a Roblox game-server IP

The primary evidence for an IP used by a live Roblox game instance is Roblox's in-game performance diagnostic:

1. Join a Roblox experience and wait for the game instance to connect.
2. Focus the Roblox game window and press **Ctrl+Shift+F3**.
3. Find the diagnostic line beginning with `Datacenter fetched IPV4,`.
4. Record the exact IPv4 address and keep a screenshot of the diagnostic.

Example:

```text
Datacenter fetched IPV4, 128.116.115.33
```

This is direct evidence that the address was reported by a game instance. A subnet match, registry record, geolocation result, or website connection alone does not prove that an IP hosted that game instance.

## How Roblox server locations are researched

Location labels are estimates supported by multiple types of evidence. No single lookup should be treated as definitive.

- **IP geolocation databases:** Check the exact IP with [iplocation.net](https://www.iplocation.net/) and review **Compare Results by Provider**. Record provider disagreements rather than assuming every result is correct.
- **San Mateo geolocation results:** Some providers may report San Mateo, California. Roblox does not have data centers in San Mateo; ignore that result or treat it as if the provider did not return a usable location. Do not use it as location evidence.
- **Globalping latency tests:** Use [Globalping](https://globalping.io/) to test the exact target from probes in relevant locations. Record the measurement URL, probe city, network/ASN, packet loss, and RTT statistics. Akamai Connected Cloud probes can provide useful additional vantage points, but they are optional.
- **Latency comparison:** For a candidate city, use the **average RTT of the single lowest-latency eligible probe in that city**. Do not average the RTTs of all probes in that city for the confidence threshold. Record the selected probe and its average RTT.
- **ICMP limitations:** Some IPs do not answer ping. Record `ICMP=No response` when appropriate. A timeout does not prove that an IP is invalid or unused.
- **Related endpoints:** If a nearby address is tested instead of the exact game-instance IP, label it separately. For example, an `.3` endpoint is not the same address as an instance ending in `.33`; its result is indirect evidence only.

## Roblox hostname verification

Roblox hostname verification is an additional location check. The hostname pattern is:

```text
edge-term4-<identifier>.roblox.com
```

A hostname contributes the final confidence point only when all of the following are true:

1. The hostname matches the `edge-term4-<identifier>.roblox.com` pattern.
2. Its DNS A record resolves to the **exact IPv4 address being evaluated**. A different address in the same /24 is not an exact match.
3. The location represented by the identifier agrees with the city selected by the latency and other location evidence.
4. The selected city's lowest-latency probe has an average RTT of **1.5 ms or less**.

A hostname resolving to a different IP, no matching hostname being found, or an identifier that conflicts with the measured location does not qualify for 100% confidence. Do not apply a hostname match to every address in a CIDR range: verify each exact IP separately.

**Conflicting evidence example:** If `edge-term4-fra2.roblox.com` resolves to the evaluated IP but the lowest-latency eligible probe is in Amsterdam rather than Frankfurt, classify the IP in Amsterdam when the other location evidence supports Amsterdam. The Frankfurt identifier is contradictory evidence, so it does not earn the hostname bonus; the location can receive 99% confidence when its latency is 1.5 ms or less.

## Location confidence ratings

Confidence is a maintainer's assessment of the reliability of the **listed location**, not a statistical probability or guarantee. Apply the following rules using the selected city's lowest-latency eligible probe (the probe's average RTT):

| Confidence | Requirement |
| ---: | --- |
| **100%** | All existing location checks pass; the lowest-latency probe in the selected city averages **1.5 ms or less**; and a matching `edge-term4` hostname resolves to the exact evaluated IP and identifies that same city. |
| **99%** | The other location checks support the selected city and its lowest-latency probe averages **1.5 ms or less**, but the Roblox hostname check is absent, does not resolve to the exact IP, or conflicts with the measured city. |
| **95%** | The selected city's lowest-latency eligible probe averages **more than 1.5 ms but less than 2.0 ms**. |
| **90%** | The selected city's lowest-latency eligible probe averages **2.0 ms or more**. |

The latency-based 95% and 90% tiers take precedence over the 99% and 100% tiers. In particular, a matching hostname cannot restore 100% confidence when the selected city's lowest-latency probe averages more than 1.5 ms. The 90% tier is the lowest latency tier currently defined; reassess the entry if other evidence suggests the location itself is wrong.

## Understanding the verified IP list

The verified list distinguishes three separate details:

- **Instance:** The address reported by Roblox's game diagnostic.
- **ICMP:** The address used for a ping measurement. It may be a related endpoint rather than the instance address.
- **Confidence:** The maintainer's assessment of how reliable the listed **location** is, following the confidence rules above. It does not rate confidence in the ICMP endpoint or the game-instance IP observation.

A location confidence rating should reflect the consistency and quality of the available evidence. Review the linked or submitted evidence before relying on a location label.

## Network ownership and classification

- **Roblox-registered ranges** are assigned to Roblox according to public Internet registry records. Registration does not prove that every IP in a range runs a Roblox game server.
- **AWS-associated ranges** are owned by Amazon Web Services and included only where there is evidence connecting the range to Roblox server use. AWS ownership alone is not enough.
- **Estimated city labels** are based on geolocation, registry information, and network measurements. They do not identify a building or physical data-center facility.

IP assignments, routing, and service usage can change. Lists may be incomplete or become outdated; use the evidence and dates when evaluating results.

## Contributing new Roblox server IP evidence

Have a game-instance IP or better location evidence? Read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting. Contributions should include the exact diagnostic observation, geolocation provider results, Roblox hostname/DNS evidence where available, and Globalping measurements.

## Reference sources

- [Roblox](https://www.roblox.com/)
- [ARIN RDAP](https://www.arin.net/)
- [AWS public IP address ranges](https://ip-ranges.amazonaws.com/ip-ranges.json)
- [AWS IP address geolocation feed](https://ip-ranges.amazonaws.com/geo-ip-feed.csv)
- [iplocation.net](https://www.iplocation.net/)
- [Globalping](https://globalping.io/)

---

*Search topics: Roblox server IP addresses, Roblox server IP list, Roblox game server IP lookup, Roblox datacenter locations, Roblox server locations by city, Roblox game-instance IPs, Roblox IPv4 ranges, Roblox AWS server IPs, and Roblox server location research.*
