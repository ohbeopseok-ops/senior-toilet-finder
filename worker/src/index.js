export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const allowedOrigins = (env.ALLOWED_ORIGINS || "https://ohbeopseok-ops.github.io,https://toilet.aijoylab.kr")
      .split(",").map(x=>x.trim()).filter(Boolean);
    const origin = request.headers.get("Origin") || "";
    const corsOrigin = allowedOrigins.includes(origin) ? origin : allowedOrigins[0];

    const cors = {
      "Access-Control-Allow-Origin": corsOrigin,
      "Access-Control-Allow-Methods": "GET,OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
      "Cache-Control": "no-store"
    };

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: cors });
    }
    if (request.method !== "GET" || url.pathname !== "/nearby") {
      return json({ error: "not_found" }, 404, cors);
    }
    if (!env.KAKAO_REST_API_KEY) {
      return json({ error: "kakao_key_missing" }, 503, cors);
    }

    const lat = Number(url.searchParams.get("lat"));
    const lng = Number(url.searchParams.get("lng"));
    const radius = Math.min(5000, Math.max(300, Number(url.searchParams.get("radius") || 3000)));

    if (!Number.isFinite(lat) || !Number.isFinite(lng) || lat < 33 || lat > 39 || lng < 124 || lng > 132) {
      return json({ error: "invalid_coordinates" }, 400, cors);
    }

    const queries = ["공중화장실", "화장실", "개방화장실"];
    const all = [];
    const upstreamErrors = [];

    for (const query of queries) {
      const endpoint = new URL("https://dapi.kakao.com/v2/local/search/keyword.json");
      endpoint.searchParams.set("query", query);
      endpoint.searchParams.set("x", String(lng));
      endpoint.searchParams.set("y", String(lat));
      endpoint.searchParams.set("radius", String(radius));
      endpoint.searchParams.set("sort", "distance");
      endpoint.searchParams.set("size", "15");

      const res = await fetch(endpoint.toString(), {
        headers: { Authorization: `KakaoAK ${env.KAKAO_REST_API_KEY}` }
      });
      if (!res.ok) {
        let detail = "";
        try { detail = (await res.text()).slice(0, 300); } catch {}
        upstreamErrors.push({ query, status: res.status, detail });
        continue;
      }
      const body = await res.json();
      for (const d of body.documents || []) all.push(d);
    }

    const seen = new Set();
    const items = [];
    for (const d of all) {
      const name = String(d.place_name || "").trim();
      const x = Number(d.x);
      const y = Number(d.y);
      if (!name || !Number.isFinite(x) || !Number.isFinite(y)) continue;

      const idKey = d.id ? `id:${d.id}` : `xy:${x.toFixed(5)}:${y.toFixed(5)}:${name.replace(/\s+/g,"")}`;
      if (seen.has(idKey)) continue;
      seen.add(idKey);

      // Keep candidates that are plausibly toilet-related.
      const text = [name, d.category_name, d.address_name, d.road_address_name].join(" ");
      if (!/화장실/.test(text)) continue;

      items.push({
        id: `kakao-${d.id || items.length + 1}`,
        name,
        shortName: name,
        lat: y,
        lng: x,
        distance: Number(d.distance || 0),
        address: d.road_address_name || d.address_name || "",
        tel: d.phone || "",
        placeUrl: d.place_url || "",
        categoryName: d.category_name || "",
        source: "kakao-local",
        verified: false,
        openHours: "개방시간 확인 필요",
        openStatus: "unknown",
        isOpen: false,
        openStatusVerified: false,
        stairs: false,
        stairsVerified: false,
        ramp: false,
        handrail: false,
        emergencyBell: false,
        accessibleToilet: false
      });
    }

    items.sort((a,b) => a.distance - b.distance);

    if (!items.length && upstreamErrors.length === queries.length) {
      const first = upstreamErrors[0] || {};
      return json({
        error: "kakao_upstream_error",
        hint: first.status === 401 || first.status === 403
          ? "Kakao Map API activation or REST API key settings may be required."
          : "Kakao Local API request failed.",
        upstreamStatus: first.status || 0,
        upstreamErrors
      }, 502, cors);
    }

    return json({
      source: "kakao-local",
      center: { lat, lng },
      radius,
      count: Math.min(items.length, 20),
      items: items.slice(0, 20)
    }, 200, cors);
  }
};

function json(data, status, headers) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { ...headers, "Content-Type": "application/json; charset=utf-8" }
  });
}
