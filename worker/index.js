const DATABASE_URL =
  "https://raw.githubusercontent.com/Maneetbal/roblox-server-locations/main/database.json";

let databaseCache;
let databaseCacheExpires = 0;
let databasePromise;
let lastGlobalLookupAt = 0;
const lastUserLookupAt = new Map();

const DATABASE_TTL = 120_000;
const USER_LOOKUP_INTERVAL = 2_000;
const GLOBAL_LOOKUP_INTERVAL = 1_000;

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
    if (!/^\d{1,3}$/.test(part)) return null;
    const octet = Number(part);
    if (octet > 255) return null;
    result = ((result << 8) | octet) >>> 0;
  }
  return result;
}

function parseIPv6(value) {
  if (!value || value.includes("%") || (value.match(/::/g) || []).length > 1) return null;

  if (value.includes(".")) {
    const lastColon = value.lastIndexOf(":");
    if (lastColon < 0) return null;
    const ipv4 = parseIPv4(value.slice(lastColon + 1));
    if (ipv4 === null) return null;
    value = value.slice(0, lastColon + 1) +
      ((ipv4 >>> 16) & 0xffff).toString(16) + ":" +
      (ipv4 & 0xffff).toString(16);
  }

  const compressed = value.includes("::");
  const halves = value.split("::");
  const left = halves[0] ? halves[0].split(":") : [];
  const right = compressed && halves[1] ? halves[1].split(":") : [];
  const missing = 8 - left.length - right.length;

  if ((compressed && missing < 1) || (!compressed && missing !== 0)) return null;
  const groups = [...left, ...Array(compressed ? missing : 0).fill("0"), ...right];
  if (groups.length !== 8 || groups.some(group => !/^[0-9a-f]{1,4}$/i.test(group))) return null;

  return groups.reduce((result, group) => (result << 16n) | BigInt("0x" + group), 0n);
}

function matchesCIDR(ip, cidr, version) {
  const [address, prefixText] = cidr.split("/");
  const bits = version === 4 ? 32 : 128;
  const network = version === 4 ? parseIPv4(address) : parseIPv6(address);
  const prefix = prefixText === undefined ? bits : Number(prefixText);

  if (network === null || !Number.isInteger(prefix) || prefix < 0 || prefix > bits) return false;

  if (version === 4) {
    const mask = prefix === 0 ? 0 : (0xffffffff << (32 - prefix)) >>> 0;
    return ((ip & mask) >>> 0) === ((network & mask) >>> 0);
  }

  const mask = prefix === 0 ? 0n : ((1n << BigInt(prefix)) - 1n) << BigInt(bits - prefix);
  return (ip & mask) === (network & mask);
}

function parseDatabase(text) {
  const records = [];
  let start = -1;
  let depth = 0;
  let inString = false;
  let escaped = false;

  for (let i = 0; i < text.length; i++) {
    const char = text[i];

    if (inString) {
      if (escaped) escaped = false;
      else if (char === "\\") escaped = true;
      else if (char === '"') inString = false;
      continue;
    }

    if (char === '"') {
      inString = true;
    } else if (char === "{") {
      if (depth === 0) start = i;
      depth++;
    } else if (char === "}") {
      depth--;
      if (depth < 0) throw new Error("Invalid database");
      if (depth === 0 && start !== -1) {
        records.push(JSON.parse(text.slice(start, i + 1)));
        start = -1;
      }
    }
  }

  if (depth !== 0 || inString || !records.length) {
    throw new Error("Invalid database");
  }
  return records;
}

async function getDatabaseText() {
  const response = await fetch(DATABASE_URL, {
    cf: { cacheTtl: 120, cacheEverything: true }
  });
  if (!response.ok) throw new Error("Database unavailable");
  return response.text();
}

async function getDatabase() {
  const now = Date.now();
  if (databaseCache && now < databaseCacheExpires) return databaseCache;
  if (databasePromise) return databasePromise;

  databasePromise = (async () => {
    const records = parseDatabase(await getDatabaseText());
    databaseCache = records;
    databaseCacheExpires = Date.now() + DATABASE_TTL;
    return records;
  })();

  try {
    return await databasePromise;
  } finally {
    databasePromise = null;
  }
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

    if (url.pathname === "/") {
      return Response.redirect(new URL("/database.json", url), 302);
    }

    if (url.pathname === "/database.json") {
      try {
        return new Response(await getDatabaseText(), {
          headers: {
            ...HEADERS,
            "cache-control": "public, max-age=120"
          }
        });
      } catch {
        return json({ error: "Could not load database" }, 502);
      }
    }

    const match = url.pathname.match(/^\/([^/]+)\/json\/?$/);
    if (!match) return json({ error: "Use /{ip}/json" }, 400);

    let requestedIP;
    try {
      requestedIP = decodeURIComponent(match[1]);
    } catch {
      return json({ error: "Invalid IP address" }, 400);
    }

    const ipv4 = parseIPv4(requestedIP);
    const ipv6 = ipv4 === null ? parseIPv6(requestedIP) : null;
    const version = ipv4 !== null ? 4 : ipv6 !== null ? 6 : 0;
    const ip = version === 4 ? ipv4 : ipv6;
    if (!version) return json({ error: "Invalid IP address" }, 400);

    const now = Date.now();
    const userIP = request.headers.get("CF-Connecting-IP") || "unknown";
    const lastUserLookup = lastUserLookupAt.get(userIP) || 0;

    if (
      now - lastUserLookup < USER_LOOKUP_INTERVAL ||
      now - lastGlobalLookupAt < GLOBAL_LOOKUP_INTERVAL
    ) {
      return new Response(
        '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Error 429</title><style>body{font-family:Arial,sans-serif;background:Canvas;color:CanvasText;margin:0;padding:40px}h1{font-size:24px;font-weight:500}p{color:GrayText;font-size:14px}</style><script>setTimeout(() => location.reload(), 2000)</script></head><body><h1>Error 429</h1><p>Too many requests. Please wait a moment.</p></body></html>',
        {
          status: 429,
          headers: {
            "content-type": "text/html; charset=utf-8",
            "cache-control": "no-store"
          }
        }
      );
    }

    lastUserLookupAt.set(userIP, now);
    lastGlobalLookupAt = now;

    for (const [ip, timestamp] of lastUserLookupAt) {
      if (now - timestamp >= USER_LOOKUP_INTERVAL) lastUserLookupAt.delete(ip);
    }

    try {
      const database = await getDatabase();
      const entry = database.find(item =>
        typeof item.cdir === "string" && matchesCIDR(ip, item.cdir, version)
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
