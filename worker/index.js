const DATABASE_URL =
  "https://raw.githubusercontent.com/Maneetbal/roblox-server-locations/main/v1/database.json";

const HEADERS = {
  "content-type": "application/json; charset=utf-8",
  "access-control-allow-origin": "*",
  "cache-control": "public, max-age=300"
};

function json(data, status = 200) {
  return new Response(JSON.stringify(data, null, 2), {
    status,
    headers: HEADERS
  });
}

function parseIPv4(value) {
  const parts = value.split(".");
  if (parts.length !== 4) return null;
  let result = 0;
  for (const part of parts) {
    if (!/^\\d{1,3}$/.test(part)) return null;
    const octet = Number(part);
    if (octet > 255) return null;
    result = ((result << 8) | octet) >>> 0;
  }
  return result;
}

function matchesCIDR(ip, cidr) {
  const [address, prefixText] = cidr.split("/");
  const network = parseIPv4(address);
  const prefix = prefixText === undefined ? 32 : Number(prefixText);
  if (network === null || !Number.isInteger(prefix) || prefix < 0 || prefix > 32) return false;
  const mask = prefix === 0 ? 0 : (0xffffffff << (32 - prefix)) >>> 0;
  return ((ip & mask) >>> 0) === ((network & mask) >>> 0);
}

async function getDatabase() {
  const response = await fetch(DATABASE_URL, {
    cf: { cacheTtl: 120, cacheEverything: true }
  });
  if (!response.ok) throw new Error("Database unavailable");
  const data = await response.json();
  if (!Array.isArray(data)) throw new Error("Invalid database");
  return data;
}

async function getExternalLocation(ip) {
  const response = await fetch(`https://ipinfo.io/${encodeURIComponent(ip)}/json`, {
    cf: { cacheTtl: 3600, cacheEverything: true }
  });
  if (!response.ok) throw new Error("IPinfo lookup failed");
  const data = await response.json();
  if (!data.ip || data.error) throw new Error("IPinfo returned no result");
  return {
    api: "ipinfo",
    ip,
    city: data.city || "",
    region: data.region || "",
    country: data.country || "",
    ...(data.loc ? { loc: data.loc } : {}),
    ...(data.org ? { org: data.org } : {})
  };
}

export default {
  async fetch(request) {
    const url = new URL(request.url);

    if (request.method === "OPTIONS") {
      return new Response(null, {
        headers: {
          "access-control-allow-origin": "*",
          "access-control-allow-methods": "GET, OPTIONS",
          "access-control-allow-headers": "Content-Type",
          "access-control-max-age": "86400"
        }
      });
    }

    if (request.method !== "GET") return json({ error: "Method not allowed" }, 405);

    const match = url.pathname.match(/^\\/((?:\\d{1,3}\\.){3}\\d{1,3})\\/json\\/?$/);
    if (!match) return json({ error: "Use /{ip}/json" }, 400);

    const requestedIP = match[1];
    const ip = parseIPv4(requestedIP);
    if (ip === null) return json({ error: "Invalid IPv4 address" }, 400);

    try {
      const database = await getDatabase();
      const entry = database.find(item =>
        typeof item.cidr === "string" && matchesCIDR(ip, item.cidr)
      );

      if (entry) {
        return json({
          api: "local",
          ip: requestedIP,
          city: entry.city || "",
          region: entry.region || "",
          country: entry.country || "",
          loc: entry.loc || "",
          org: entry.org || ""
        });
      }

      return json(await getExternalLocation(requestedIP));
    } catch {
      return json({ error: "Could not load IP location data" }, 502);
    }
  }
};
