# Maintaining the Roblox server IP lists

These files are community-maintained and are not an official Roblox inventory. Keep the three datasets synchronized:

- roblox-owned-ip-addresses.txt
- aws-roblox-server-ip-addresses.txt
- robloxserveriplist.txt (combined compatibility list)

## Evidence and classification

1. Record how a candidate address was observed. Roblox Player connection logs or a captured Roblox game-session endpoint support Roblox-use attribution. An ICMP reply alone does not establish Roblox use.
2. Check the network registrant with the relevant Regional Internet Registry (RIR) RDAP service. Put Roblox-registered networks in the Roblox-registered list. If a Roblox-registered block is hosted on AWS, note that fact; classify it by registrant to avoid duplicate listing.
3. For AWS-owned addresses, compare the prefix with [AWS public IP ranges](https://ip-ranges.amazonaws.com/ip-ranges.json) and use the [AWS geo-IP feed](https://ip-ranges.amazonaws.com/geo-ip-feed.csv) as a location hint. AWS use of the entries already in this dataset is maintainer-confirmed.
4. Treat city names as estimates unless independently supported by stronger location evidence. A registry record or geo-IP city is not proof of a physical facility. Preserve existing uncertainty and reachability notes.
5. Keep intentional overlaps when they serve a distinct purpose. For example, 3.80.0.0/32 is an ICMP test probe within 3.80.0.0/12; it is not a duplicate.
6. Do not add every AWS region automatically. Add only regions with evidence of Roblox use and maintainer approval.

## Updates

- Recheck records and observed endpoints periodically; note the source and date.
- Remove an entry only when there is sufficient evidence it is no longer relevant.
- Deduplicate exact repeated CIDRs when they refer to the same listed range. If locations conflict, retain the best-supported label and record the basis in the changelog.
- When the data changes, update all three files, their dates, and CHANGELOG.md.
- Do not claim completeness or a statistical accuracy rate unless measured and documented.
