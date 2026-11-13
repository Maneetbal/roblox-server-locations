# Static JSON API

Endpoint:

`https://raw.githubusercontent.com/Maneetbal/roblox-server-locations/api/v1/database.json`

The response is a compact, minified JSON array generated from **[`all-ips.txt`](../all-ips.txt)**. Every record contains exactly these six fields:

```json
{
  "ip": "128.116.115.0/24",
  "city": "Seattle",
  "region": "Washington",
  "country": "United States",
  "loc": "47.6062,-122.3321",
  "org": "AS22697 Roblox"
}
```

- `ip` contains the exact IPv4 address or CIDR range listed in `all-ips.txt`; ranges are not converted into assumed `.33` instance addresses.
- `city`, `region`, and `country` are estimated location labels.
- `loc` is the approximate city-centre latitude and longitude, not a verified data-centre coordinate.
- `org` is `Amazon AWS` for entries marked `(AWS)` in the source list, otherwise `AS22697 Roblox`.

The API includes the Roblox-associated and AWS-associated ranges in `all-ips.txt`, including entries marked as reserved. A range being listed does not prove that every address in it currently hosts a Roblox game server.

The response is a static array, not a server-side IP query endpoint. Voidstrap should download and cache it, then match an address against the listed IP/CIDR ranges locally.

The JSON file is stored on the `api` branch. When `all-ips.txt` changes, regenerate and publish `v1/database.json` to keep this endpoint current.

Unofficial community project; not affiliated with Roblox.
