# Static JSON API

Endpoint:

`https://maneetbal.github.io/roblox-server-locations/api/v1/database.json`

The response is a compact JSON array. Every record contains exactly these six fields:

```json
{
  "ip": "128.116.115.33",
  "city": "Seattle",
  "region": "Washington",
  "country": "United States",
  "loc": "47.6062,-122.3321",
  "org": "AS22697 Roblox"
}
```

- `ip` is the listed network's assumed game-instance address, using the `.33` suffix from the source ledger.
- `city`, `region`, and `country` are estimated location labels.
- `loc` is the approximate city-centre latitude and longitude, not a verified data-centre coordinate.
- `org` is the Roblox ASN label.

**Important:** The source ledger assumes the `.33` instance suffix; it does not independently verify every generated address. Entries without a numeric instance suffix are omitted. The response is a static array, not a server-side IP query endpoint. Voidstrap should download and cache it, then find the matching `ip` locally.

The database is rebuilt by GitHub Actions whenever the source ledger or generator changes on `main`.

Unofficial community project; not affiliated with Roblox.
