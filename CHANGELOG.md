# Changelog

## 2026-10-22

- Added separate Roblox-registered and AWS Roblox-use lists; kept robloxserveriplist.txt as the combined compatibility list.
- Retained the existing AWS ranges and regions; no new regions were added.
- Added the maintainer-provided 3.80.0.0/32 ICMP latency probe next to the Ashburn entries. Its overlap with 3.80.0.0/12 is intentional.
- Removed the former “Decommissioned?” section from the active dataset.
- Removed the repeated 136.18.142.0/24 entry from Frankfurt; AWS geo-IP data identifies the range with Istanbul, so the Istanbul entry remains.
- Replaced the README's full inline dump with links, scope, methodology, limitations, and maintenance guidance.

## 2026-10-23

- Added the observed endpoint 128.116.30.3 under New York City, with a note that the location is based on network testing.
- Marked San Jose, CA and Boardman, OR as reserved in the lists.
- Documented AWS-associated Roblox server entries as reserve capacity that may be used during high demand, full regions, or regional outages/degradation; this is a maintainer interpretation, not a confirmed statement of Roblox's internal policy.
