# Roblox Server IP Addresses and Locations

A community-maintained reference of IP ranges associated with Roblox game servers, including network registration, observed locations, and game-instance evidence.

> **Disclaimer:** This project is unofficial and is not affiliated with or endorsed by Roblox. Locations are estimates, not confirmed physical data-center addresses.

## Datasets

| File | Description |
| --- | --- |
| [`roblox-ips.txt`](roblox-ips.txt) | IP ranges registered to Roblox, grouped by estimated location. |
| [`aws-ips.txt`](aws-ips.txt) | AWS IP ranges associated with Roblox server use. |
| [`all-ips.txt`](all-ips.txt) | Combined list of Roblox-registered and AWS-associated ranges. |
| [`roblox-verified-ips.txt`](roblox-verified-ips.txt) | Game-instance observations with supporting evidence and confidence ratings. |

## Identifying a game instance

The primary source for identifying an active game-instance address is Roblox's in-game performance diagnostic:

1. Join an experience and wait for the game instance to connect.
2. Focus the Roblox game window and press **Ctrl+Shift+F3**.
3. Find the line beginning with `Datacenter fetched IPV4,`.
4. Record the exact IPv4 address and retain a screenshot of the diagnostic.

Example:

```text
Datacenter fetched IPV4, 128.116.115.33
```

Do not treat an address as a confirmed game-instance IP solely because it belongs to a listed subnet or appears in a website connection.

## Location and latency checks

Location data should be treated as corroborating evidence:

- **IP location:** Check the exact address with [iplocation.net](https://www.iplocation.net/) and record the distinct results shown under **Compare Results by Provider**. Some providers may report **San Mateo, California**; Roblox does not have data centers in San Mateo, so this result can be safely disregarded or treated as if that provider returned no result. Do not use it as supporting location evidence.
- **Latency:** Use [Globalping](https://globalping.io/) to test the exact address from probes in the reported locations. Record the measurement URL, probe location, network/ASN, packet loss, and RTT statistics. Akamai Connected Cloud probes on Globalping can be especially useful for these tests, but using an Akamai probe is optional; other suitable probes are acceptable.
- **No ICMP response:** Some addresses do not respond to ping. Skip the ping test, record `ICMP=No response`, and flag the address for review. A timeout does not establish that an address is invalid.
- **Related addresses:** If a nearby or related address is tested instead, identify it separately. Its response is indirect evidence and must not be presented as a test of the game-instance IP.

## Classification and limitations

- **Roblox-registered** means the network is registered to Roblox in public Internet registry records. It does not, by itself, prove that every address in the range hosts a game server.
- **AWS-associated** entries are AWS ranges for which the project has evidence of Roblox server use. AWS ownership alone is not sufficient evidence.
- City and region labels are estimates based on available registry, geolocation, and network measurements. They do not identify a physical facility.
- IP assignments, routing, and service use can change. The lists may be incomplete or become outdated.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the evidence requirements and submission process.

## Reference sources

- [ARIN RDAP](https://www.arin.net/)
- [AWS public IP address ranges](https://ip-ranges.amazonaws.com/ip-ranges.json)
- [AWS IP address geolocation feed](https://ip-ranges.amazonaws.com/geo-ip-feed.csv)
- [iplocation.net](https://www.iplocation.net/)
- [Globalping](https://globalping.io/)
