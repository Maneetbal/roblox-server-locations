# Roblox Server IP Addresses and Locations

Community-maintained reference for Roblox game server IP addresses, CIDR ranges, and approximate network locations. This project is not an official Roblox resource.

## Current lists

| Dataset | Contents |
| --- | --- |
| [Roblox-registered IP addresses](roblox-owned-ip-addresses.txt) | 34 entries classified by Roblox registration/ownership evidence. |
| [AWS IP ranges used by Roblox](aws-roblox-server-ip-addresses.txt) | 2,043 existing AWS entries, including the Ashburn ICMP latency probe. |
| [Combined legacy list](robloxserveriplist.txt) | Both datasets in the original path for existing links and workflows. |

The combined list intentionally keeps 3.80.0.0/32 as an ICMP latency probe inside the broader 3.80.0.0/12 AWS range. The overlap is deliberate: the /32 is a single test address, while the /12 is a wider prefix.

## What the data means

“Roblox-registered” describes the network registrant shown in public Internet registry records. The Roblox-registered file includes 107.180.197.0/24, which is registered to Roblox and hosted on AWS; it is grouped by registrant. The AWS file contains the other AWS ranges associated with Roblox server use.

AWS usage in this dataset is maintainer-confirmed. AWS's published IP ranges and geo-IP feed help identify AWS network assignment and provide location hints; they do not identify the game service on their own. Ownership and geolocation are distinct from the evidence that an address is used by Roblox.

Country and city headings are approximate network locations, not verified physical data-center addresses. Entries retain uncertainty notes where present. Registry records, AWS ranges, and network assignments can change; this list may not contain every Roblox server IP and is not a complete inventory. No measured accuracy percentage or completeness claim is made.

## Sources and review

- [ARIN RDAP record for 128.116.115.33](https://rdap.arin.net/registry/ip/128.116.115.33)
- [ARIN RDAP record for 209.206.42.1](https://rdap.arin.net/registry/ip/209.206.42.1)
- [ARIN RDAP record for 107.180.197.1](https://rdap.arin.net/registry/ip/107.180.197.1)
- [AWS public IP ranges](https://ip-ranges.amazonaws.com/ip-ranges.json)
- [AWS geo-IP feed](https://ip-ranges.amazonaws.com/geo-ip-feed.csv)

Roblox Player logs and direct network observations can support Roblox-use attribution. An ICMP response measures reachability and latency to that address; it does not by itself prove that a Roblox game server is running there. See [CONTRIBUTING.md](CONTRIBUTING.md) for the update and verification process, and [CHANGELOG.md](CHANGELOG.md) for material dataset changes.

**Last updated: 2026-10-22** — split the active dataset into two clearly classified files, removed the decommissioned section, resolved one exact duplicate using the AWS geo-IP feed, and recorded the maintainer-provided Ashburn probe. No AWS regions were added.

Search terms: Roblox server IP addresses, Roblox server locations, Roblox game server IP list, Roblox data center locations, Roblox AWS server IP ranges, Roblox CIDR list.
