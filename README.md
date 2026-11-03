# Roblox Server IP Addresses and Locations

Community-maintained reference for Roblox game server IP addresses, CIDR ranges, and associated locations. This project is not an official Roblox resource.

**Status: Up to date.** The active ranges are based on testing and network observations, including Roblox game-instance addresses reported by the in-game diagnostics.

## Current lists

| Dataset | Contents |
| --- | --- |
| [roblox-ips.txt](https://github.com/Maneetbal/roblox-server-locations/blob/main/roblox-ips.txt "roblox-ips.txt") | Roblox-registered entries. |
| [AWS IP ranges used by Roblox](aws-ips.txt) | AWS entries associated with Roblox server use, including the Ashburn ICMP latency probe. |
| [Combined list](all-ips.txt) | Roblox-registered and AWS-associated entries in one file. |
| [Verified game-instance IPs](roblox-verified-ips.txt) | Individual IPs with direct game-instance and location evidence notes. |

## Roblox-owned IP addresses

The following list summarizes Roblox-registered entries. City labels are community location observations; the 107.180.197.0/24 entry is registered to Roblox and hosted on AWS.

### United States
#### Ashburn, VA
- 128.116.102.0/24
- 128.116.53.0/24
- 107.180.197.0/24 (Doesnt respond to icmp)
- 128.116.56.0/24
#### Atlanta, GA
- 128.116.2.0/24
#### Chicago, IL
- 128.116.48.0/24
- 128.116.84.0/24 (Not sure, around Chicago)
#### Dallas, TX
- 128.116.14.0/24
- 128.116.95.0/24
#### Los Angeles, CA
- 128.116.116.0/24
- 128.116.1.0/24
- 128.116.63.0/24
#### Miami, FL
- 128.116.45.0/24
- 128.116.127.0/24
#### New York City, NY
- 128.116.32.0/24
- 128.116.30.3 (observed endpoint; location based on network testing)
#### San Jose, CA (Reserved)
- 128.116.117.0/24
- 128.116.67.0/24
- 209.206.42.0/24
- 209.206.43.0/24
#### Seattle, WA
- 128.116.115.0/24 (.33)

### Australia
#### Sydney, AU
- 128.116.51.0/24

### Brazil
#### Sao Paulo, BR
- 128.116.86.0/24

### France
#### Paris, FR
- 128.116.13.0/24

### Germany
#### Frankfurt, DE
- 128.116.5.0/24
- 128.116.44.0/24

### India
#### Mumbai, IN
- 128.116.47.0/24

### Japan
#### Tokyo, JP
- 128.116.55.0/24
- 128.116.120.0/24

### Netherlands
#### Amsterdam, NL
- 128.116.21.0/24

### Singapore
#### Singapore, SG
- 128.116.46.0/24
- 128.116.50.0/24
- 128.116.54.0/24
- 128.116.97.0/24

### United Kingdom
#### London, UK
- 128.116.31.0/24

## Verified game-instance observations

See [roblox-verified-ips.txt](roblox-verified-ips.txt) for individual endpoints with recorded evidence. The list distinguishes direct game-instance evidence from location corroboration; a nearby or sibling IP responding to ping does not, by itself, prove that another address is a Roblox game server.

For a live game-instance check, press **Ctrl+Shift+F3 while focused on the Roblox game instance** and look for a line in this format:

`Datacenter fetched IPV4, 128.116.115.33`

The Ctrl+Shift+F3 datacenter-fetched IPv4 result is the primary source for identifying the game instance. Record the exact diagnostic line and IP. Do not treat a website connection or an IP merely sharing a subnet as direct game-instance proof.

### Location and latency cross-check

1. Open [iplocation.net](https://www.iplocation.net/) for the exact game-instance IP.
2. Review the **Compare Results by Provider** section. Record every distinct city/region shown and the providers that report it. Provider agreement is useful corroboration, not proof of a physical data-center address.
3. For each distinct location shown, run a ping to the exact IP from a Globalping probe in that location using [Globalping](https://globalping.io/). Record probe location, ASN/provider, packet count, loss, and min/average/max RTT. Use multiple probes where practical.
4. Prefer pings to the exact game-instance IP. If it does not answer ICMP, skip that ping, record `ICMP=No response`, and flag the IP for maintainer verification. Do not treat the lack of an ICMP reply as proof that the IP is invalid. A nearby or related endpoint can only be recorded as indirect location evidence; identify it separately and never claim it proves the game IP's reachability.

## Roblox IP observations

Ctrl+Shift+F3 game-instance diagnostics commonly report Roblox game-server connections using addresses ending in .33. The HTTPS website commonly uses an address ending in .3. For example, 128.116.115.33 is a game-server address and 128.116.115.3 is a website address; they are in the same location and have shown the same latency in my testing. The .33 game-instance addresses do not respond to ICMP. This .3/.33 pattern applies to some addresses, not all Roblox IPs.

Address 128.116.115.4 also responds to ICMP, but I have not identified which service it represents. The separate 3.80.0.0/32 entry is an AWS ICMP latency probe and intentionally overlaps the broader 3.80.0.0/12 prefix.

## Reserved capacity and AWS

The San Jose, CA and Boardman, OR entries are marked **Reserved** to indicate they are treated as reserve capacity in this community-maintained list. AWS-associated Roblox server entries are considered reserved capacity: they may be used when demand is high, a primary region is full, or service in another region is unavailable or degraded. This describes the maintainer's current understanding based on observations, not a guarantee of Roblox's internal deployment policy.

## Additional network observations

The following notes are README references only; they do not add or change entries in the active IP list files.

### Rare Roblox game-instance observations: 209.206.40.0/21

ARIN registers 209.206.40.0/21 to Roblox. In my game-instance diagnostic observations, Roblox use of this broader subnet has been rare: I have seen about four game instances so far, all located in San Jose. That is the only location I have observed to date, not evidence that the entire subnet is reserved to San Jose; it may be used in other locations. The existing narrower 209.206.42.0/24 and 209.206.43.0/24 entries remain as listed. [ARIN RDAP record](https://rdap.arin.net/registry/ip/209.206.40.0)

### Roblox-registered ranges not yet added to active lists

Public registration records list 107.180.192.0/20 to Roblox. Within it, 107.180.192.0/21 and 107.180.200.0/21 are named ROBLOX-AWS-PUBLIC and ROBLOX-AWS-PUBLIC-2. The separate 204.13.168.0/21 allocation is also registered to Roblox Corporation. These registry records establish registration; they do not by themselves identify which services use the ranges. These ranges are documented here only and have not been added to the active lists. [107.180.192.0/20 RDAP](https://rdap.arin.net/registry/ip/107.180.192.0) · [ROBLOX-AWS-PUBLIC-2 RDAP](https://rdap.arin.net/registry/ip/107.180.200.0) · [204.13.168.0/21 RDAP](https://rdap.arin.net/registry/ip/204.13.168.0)

### Unclassified candidate subnets

These additional subnets are documented for future investigation only. Their presence here does not confirm Roblox ownership or game-server use, and they are not in the active lists:

- 103.140.28.0/23
- 141.193.3.0/24
- 205.201.62.0/24

## Ownership and locations

“Roblox-registered” describes the network registrant shown in public Internet registry records. The Roblox-registered file includes 107.180.197.0/24, which is registered to Roblox and hosted on AWS; it is grouped by registrant. The AWS file contains the other AWS ranges associated with Roblox server use. AWS use of these entries is maintainer-confirmed.

The country and city groupings describe observed or estimated network locations, not verified physical data-center addresses. AWS public IP ranges and its geo-IP feed help identify network assignment and location hints. IP assignments and routing can change, and this list may not include every Roblox server IP.

## Sources and maintenance

- [ARIN RDAP: 128.116.115.33](https://rdap.arin.net/registry/ip/128.116.115.33)
- [ARIN RDAP: 209.206.42.1](https://rdap.arin.net/registry/ip/209.206.42.1)
- [ARIN RDAP: 107.180.197.1](https://rdap.arin.net/registry/ip/107.180.197.1)
- [AWS public IP ranges](https://ip-ranges.amazonaws.com/ip-ranges.json)
- [AWS geo-IP feed](https://ip-ranges.amazonaws.com/geo-ip-feed.csv)

See [CONTRIBUTING.md](CONTRIBUTING.md) for how entries are checked, verified, and kept synchronized.

Search terms: Roblox server IP addresses, Roblox server locations, Roblox game server IP list, Roblox data center locations, Roblox AWS server IP ranges, Roblox CIDR list.
