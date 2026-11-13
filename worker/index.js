const DATABASE_URL =
  "https://maneetbal.github.io/roblox-server-locations/api/v1/database.json";

const JSON_HEADERS = {
  "content-type": "application/json; charset=utf-8",
  "access-control-allow-origin": "*",
  "cache-control": "public, max-age=300"
};

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: JSON_HEADERS
  });
}

function parseIPv4(value) {
  const parts = value.split(".");
  if (parts.length !== 4) return null;

  let result = 0;
  for (const part of parts) {
    if (!/^\d{1,3}$/.test(part)) return null;
    const octet = Number(part);
    if (octet > 255) return null;
    result = ((result << 8) | octet) >>> 0;
  }
  return result;
}

function matchesCIDR(ipNumber, cidr) {
  const [address, prefixText] = cidr.split("/");
  const networkNumber = parseIPv4(address);
  if (networkNumber === null) return false;

  const prefix = prefixText === undefined ? 32 : Number(prefixText);
  if (!Number.isInteger(prefix) || prefix < 0 || prefix > 32) return false;

  const mask = prefix === 0 ? 0 : (0xffffffff << (32 - prefix)) >>> 0;
  return (ipNumber & mask) >>> 0 === (networkNumber & mask) >>> 0;
}

async function getDatabase() {
  const response = await fetch(DATABASE_URL, {
    cf: { cacheTtl: 300, cacheEverything: true }
  });

  if (!response.ok) {
    throw new Error("IP database is unavailable");
  }

  const database = await response.json();
  if (!Array.isArray(database)) {
    throw new Error("IP database has an invalid format");
  }

  return database;
}

async function getExternalLocation(ip) {
  // Prefer IP2Location.io's keyless API (up to 1,000 requests/day).
  try {
    const response = await fetch(
      `https://api.ip2location.io/?ip=${encodeURIComponent(ip)}&format=json`,
      { cf: { cacheTtl: 3600, cacheEverything: true } }
    );

    if (!response.ok) {
      console.warn("IP2Location HTTP error:", response.status);
    } else {
      const data = await response.json();
      if (data.error) {
        console.warn("IP2Location API error:", JSON.stringify(data.error));
      }
      if (data.ip && !data.error) {
        const asn = data.asn ? `AS${data.asn}` : "";
        const org = [asn, data.as, data.isp].filter(Boolean).join(" ");
        const loc =
          data.latitude != null && data.longitude != null
            ? `${data.latitude},${data.longitude}`
            : undefined;

        return {
          api: "ip2loc",
          ip,
          city: data.city_name || "",
          region: data.region_name || "",
          country: data.country_name || data.country_code || "",
          ...(loc ? { loc } : {}),
          ...(org ? { org } : {})
        };
      }
    }
  } catch (error) {
    console.warn("IP2Location request failed:", String(error));
  }

  // Keyless IPinfo legacy endpoint; limited to 1,000 requests/day.
  const response = await fetch(
    `https://ipinfo.io/${encodeURIComponent(ip)}/json`,
    { cf: { cacheTtl: 3600, cacheEverything: true } }
  );

  if (!response.ok) {
    throw new Error("External IP lookup failed");
  }

  const data = await response.json();
  if (!data.ip || data.error) {
    throw new Error("External IP lookup returned no result");
  }

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

    if (request.method !== "GET") {
      return json({ error: "Method not allowed" }, 405);
    }

    const match = url.pathname.match(/^\/((?:\d{1,3}\.){3}\d{1,3})\/json\/?$/);
    if (!match) {
      return json({ error: "Use /{ip}/json" }, 400);
    }

    const requestedIP = match[1];
    const ipNumber = parseIPv4(requestedIP);
    if (ipNumber === null) {
      return json({ error: "Invalid IPv4 address" }, 400);
    }

    try {
      const database = await getDatabase();
      const entry = database.find((item) =>
        typeof item.ip === "string" && matchesCIDR(ipNumber, item.ip)
      );

      if (entry) {
        return json({
          api: "local",
          ip: requestedIP,
          city: entry.city,
          region: entry.region,
          country: entry.country,
          loc: entry.loc,
          org: entry.org
        });
      }

      return json(await getExternalLocation(requestedIP));
    } catch {
      return json({ error: "Could not load IP location data" }, 502);
    }
  }
};
