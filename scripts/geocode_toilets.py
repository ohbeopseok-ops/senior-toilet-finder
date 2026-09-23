#!/usr/bin/env python3
"""
V0.4 geocoding pipeline.

Input:
  data/toilets-live.json

Behavior:
  - Keeps existing lat/lng.
  - For rows without coordinates but with an address, resolves the road-name address
    through the Ministry of the Interior and Safety Juso Search API.
  - Uses the Juso Coordinate API to get UTM-K(GRS80) entX/entY.
  - Converts EPSG:5179 -> WGS84(EPSG:4326) using pyproj.
  - Writes enriched records back to data/toilets-live.json.

Required GitHub Actions secrets:
  JUSO_SEARCH_KEY   : approval key for road-name address Search API
  JUSO_COORD_KEY    : approval key for Coordinate API

Optional:
  GEOCODE_REGIONS   : comma-separated regions such as "고양시,수원시"
  GEOCODE_MAX       : maximum rows per run (default 100)

Safety:
  A geocoded coordinate does NOT imply barrier-free verification.
  stairsVerified/openStatusVerified remain independent fields.
"""

from __future__ import annotations

import json
import os
import time
import urllib.parse
import urllib.request
from pathlib import Path

from pyproj import Transformer

SRC = Path("data/toilets-live.json")
SEARCH_KEY = os.getenv("JUSO_SEARCH_KEY", "").strip()
COORD_KEY = os.getenv("JUSO_COORD_KEY", "").strip()
REGIONS = [x.strip() for x in os.getenv("GEOCODE_REGIONS", "고양시,수원시").split(",") if x.strip()]
MAX_ROWS = int(os.getenv("GEOCODE_MAX", "100"))

SEARCH_URL = "https://business.juso.go.kr/addrlink/addrLinkApi.do"
COORD_URL = "https://business.juso.go.kr/addrlink/addrCoordApi.do"

transformer = Transformer.from_crs("EPSG:5179", "EPSG:4326", always_xy=True)


def http_json(url: str, params: dict) -> dict:
    qs = urllib.parse.urlencode(params)
    req = urllib.request.Request(
        f"{url}?{qs}",
        headers={"User-Agent": "SeniorToiletFinder/0.4"},
    )
    with urllib.request.urlopen(req, timeout=20) as res:
        raw = res.read()
    for enc in ("utf-8", "euc-kr", "cp949"):
        try:
            return json.loads(raw.decode(enc))
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
    raise RuntimeError("Juso API response could not be decoded as JSON")


def find_road_address(address: str) -> dict | None:
    data = http_json(
        SEARCH_URL,
        {
            "confmKey": SEARCH_KEY,
            "currentPage": 1,
            "countPerPage": 5,
            "keyword": address,
            "resultType": "json",
        },
    )
    common = data.get("results", {}).get("common", {})
    if common.get("errorCode") not in (None, "", "0"):
        raise RuntimeError(f"search API: {common.get('errorCode')} {common.get('errorMessage')}")
    rows = data.get("results", {}).get("juso", []) or []
    return rows[0] if rows else None


def find_coordinates(juso: dict) -> tuple[float, float] | None:
    data = http_json(
        COORD_URL,
        {
            "confmKey": COORD_KEY,
            "admCd": juso.get("admCd", ""),
            "rnMgtSn": juso.get("rnMgtSn", ""),
            "udrtYn": juso.get("udrtYn", "0"),
            "buldMnnm": juso.get("buldMnnm", "0"),
            "buldSlno": juso.get("buldSlno", "0"),
            "resultType": "json",
        },
    )
    common = data.get("results", {}).get("common", {})
    if common.get("errorCode") not in (None, "", "0"):
        raise RuntimeError(f"coord API: {common.get('errorCode')} {common.get('errorMessage')}")
    rows = data.get("results", {}).get("juso", []) or []
    if not rows:
        return None
    x = rows[0].get("entX")
    y = rows[0].get("entY")
    if x in (None, "") or y in (None, ""):
        return None
    lon, lat = transformer.transform(float(x), float(y))
    if not (33 <= lat <= 39 and 124 <= lon <= 132):
        raise RuntimeError(f"converted coordinate out of Korea bounds: {lat}, {lon}")
    return lat, lon


def in_scope(item: dict) -> bool:
    if not REGIONS:
        return True
    hay = " ".join(
        str(item.get(k, "") or "")
        for k in ("address", "name", "shortName", "sourceRegion", "agency")
    )
    return any(region in hay for region in REGIONS)


def main() -> int:
    if not SEARCH_KEY or not COORD_KEY:
        print("JUSO_SEARCH_KEY / JUSO_COORD_KEY are not configured; geocoding skipped.")
        return 0
    payload = json.loads(SRC.read_text(encoding="utf-8"))
    items = payload.get("items", [])
    changed = 0
    attempted = 0

    for item in items:
        if attempted >= MAX_ROWS:
            break
        if item.get("lat") not in (None, "") and item.get("lng") not in (None, ""):
            continue
        address = (item.get("address") or "").strip()
        if not address or not in_scope(item):
            continue

        attempted += 1
        try:
            road = find_road_address(address)
            if not road:
                item["geocodeStatus"] = "address-not-found"
                continue
            coord = find_coordinates(road)
            if not coord:
                item["geocodeStatus"] = "coordinate-not-provided"
                continue

            lat, lng = coord
            item["lat"] = round(lat, 7)
            item["lng"] = round(lng, 7)
            item["geocodeStatus"] = "official-juso-coordinate"
            item["geocodeProvider"] = "MOIS-Juso"
            item["geocodeRoadAddr"] = road.get("roadAddr", "")
            item["geocodeAdmCd"] = road.get("admCd", "")
            changed += 1
        except Exception as exc:
            item["geocodeStatus"] = "error"
            item["geocodeError"] = str(exc)[:300]

        # Coordinate API limit is 10 calls / 5 seconds. Keep a conservative pace.
        time.sleep(0.6)

    payload["geocode"] = {
        "provider": "MOIS-Juso",
        "regions": REGIONS,
        "attempted": attempted,
        "updated": changed,
    }
    SRC.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"geocoding attempted={attempted}, updated={changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
