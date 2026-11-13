# Static JSON API

This repository publishes a static IPv4 location database through GitHub Pages. It does not run a server-side function and does not perform live geolocation requests.

## Base URL

After GitHub Pages is enabled with **Settings → Pages → Build and deployment → Source → GitHub Actions**, the database will be available at:

\`https://maneetbal.github.io/roblox-server-locations/api/v1/database.json\`

## Lookup

Download the JSON database and find the entry whose \`cidr\` contains the requested IPv4 address. If multiple prefixes match, use the most-specific prefix (the largest CIDR prefix length).

Example in C#:

\`\`\`csharp
using System.Net;
using System.Net.Http;
using System.Net.Sockets;
using System.Text.Json;

using var http = new HttpClient();
using var document = await http.GetStringAsync(
    "https://maneetbal.github.io/roblox-server-locations/api/v1/database.json"
);

using var json = JsonDocument.Parse(document);
var ip = IPAddress.Parse("128.116.115.33");

foreach (var entry in json.RootElement.GetProperty("entries").EnumerateArray())
{
    var cidr = entry.GetProperty("cidr").GetString()!;
    if (CidrContains(cidr, ip))
    {
        Console.WriteLine(entry);
        break;
    }
}

static bool CidrContains(string cidr, IPAddress address)
{
    var parts = cidr.Split('/');
    var network = IPAddress.Parse(parts[0]).GetAddressBytes();
    var candidate = address.GetAddressBytes();
    if (network.Length != 4 || candidate.Length != 4) return false;

    var prefix = int.Parse(parts[1]);
    for (var i = 0; i < 4; i++)
    {
        var bits = Math.Clamp(prefix - (i * 8), 0, 8);
        var mask = bits == 0 ? 0 : 0xFF << (8 - bits);
        if ((network[i] & mask) != (candidate[i] & mask)) return false;
    }
    return true;
}
\`\`\`

## Response fields

- \`cidr\`: network prefix used for the match.
- \`city\`, \`region\`, \`country\`, \`country_code\`: estimated location.
- \`confidence\`: maintainer-assessed location confidence from the verified-IP ledger; not a probability.
- \`icmp_endpoint_suffix\`: ICMP endpoint notation recorded in the source ledger.
- \`instance_suffix\`: instance suffix recorded in the source ledger.
- \`instance_suffix_is_assumed\`: true when the source ledger supplies an assumed suffix.
- \`hostname\`: recorded Roblox edge-term hostname, where available.
- \`hostname_evidence_for\`: clarifies that the repository's hostname evidence refers to the ICMP endpoint.

The API intentionally preserves the source ledger's limitations. A CIDR match does not prove that every address in that prefix is a live game server. The API does not fabricate a full instance IP from a suffix.

## Updates and hosting

GitHub Actions rebuilds and deploys the JSON database when \`roblox-verified-ips.txt\` changes on \`main\`, or when manually run. GitHub Pages serves the generated files over HTTPS. No separate server or API key is required.

This is a static database, not a dynamic query-parameter API. It is suitable for a client such as Voidstrap to download and cache the small database, then perform CIDR matching locally.

GitHub Pages has usage limits and rate limiting; see [GitHub Pages limits](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits).

Unofficial community project; not affiliated with Roblox. Locations are estimates.
