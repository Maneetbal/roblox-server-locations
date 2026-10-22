# Roblox Server IP Addresses and Locations

Community-maintained reference for Roblox game server IP addresses, CIDR ranges, and associated locations. This project is not an official Roblox resource.

**Status: Up to date.** The active ranges are based on testing and network observations, including Roblox game-instance connections observed with GlassWire.

## Current lists

| Dataset | Contents |
| --- | --- |
| [roblox-owned-ip-addresses.txt](https://github.com/Maneetbal/roblox-server-locations/blob/main/roblox-owned-ip-addresses.txt "roblox-owned-ip-addresses.txt") | 34 Roblox-registered entries. |
| [AWS IP ranges used by Roblox](aws-roblox-server-ip-addresses.txt) | 2,043 existing AWS entries, including the Ashburn ICMP latency probe. |
| [Combined legacy list](robloxserveriplist.txt) | Both datasets in the original path for existing links and workflows. |

I am confident that at least 95% of the listed IP ranges are correct. This is my estimate based on testing and observations, not a percentage from an independent statistical audit.

## Roblox IP observations

GlassWire observations of game instances commonly show Roblox game-server connections using addresses ending in .33. The HTTPS website commonly uses an address ending in .3. For example, 128.116.115.33 is a game-server address and 128.116.115.3 is a website address; they are in the same location and have shown the same latency in my testing. The .33 game-instance addresses do not respond to ICMP. This .3/.33 pattern applies to some addresses, not all Roblox IPs.

Address 128.116.115.4 also responds to ICMP, but I have not identified which service it represents. The separate 3.80.0.0/32 entry is an AWS ICMP latency probe and intentionally overlaps the broader 3.80.0.0/12 prefix.

## Ownership and locations

“Roblox-registered” describes the network registrant shown in public Internet registry records. The Roblox-registered file includes 107.180.197.0/24, which is registered to Roblox and hosted on AWS; it is grouped by registrant. The AWS file contains the other AWS ranges associated with Roblox server use. AWS use of these entries is maintainer-confirmed.

The country and city groupings describe observed or estimated network locations, not verified physical data-center addresses. AWS public IP ranges and its geo-IP feed help identify network assignment and location hints. IP assignments and routing can change, and this list may not include every Roblox server IP.

## Sources and maintenance

- [ARIN RDAP: 128.116.115.33](https://rdap.arin.net/registry/ip/128.116.115.33)
- [ARIN RDAP: 209.206.42.1](https://rdap.arin.net/registry/ip/209.206.42.1)
- [ARIN RDAP: 107.180.197.1](https://rdap.arin.net/registry/ip/107.180.197.1)
- [AWS public IP ranges](https://ip-ranges.amazonaws.com/ip-ranges.json)
- [AWS geo-IP feed](https://ip-ranges.amazonaws.com/geo-ip-feed.csv)

See [CONTRIBUTING.md](CONTRIBUTING.md) for how entries are checked and the three lists kept synchronized. [CHANGELOG.md](CHANGELOG.md) records significant dataset changes.

Search terms: Roblox server IP addresses, Roblox server locations, Roblox game server IP list, Roblox data center locations, Roblox AWS server IP ranges, Roblox CIDR list.
