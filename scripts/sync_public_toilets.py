#!/usr/bin/env python3
"""
Sync official public-restroom data into data/toilets-live.json.

Default source:
  Ministry of the Interior and Safety / LOCALDATA public restroom CSV download URL.

Important:
  The national standard dataset stopped providing WGS84 latitude/longitude
  from February 2025. This script therefore records the official row count
  but publishes only rows that contain usable coordinates. If none are
  available, the web app intentionally falls back to the curated geo cache.

Override PUBLIC_TOILET_SOURCE_URL with a regional/official CSV endpoint that
contains coordinates and the same adapter will publish live geolocated rows.
"""

from __future__ import annotations

import csv
import io
import json
import os
import sys
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

SOURCE_URL = os.getenv(
    "PUBLIC_TOILET_SOURCE_URL",
    "https://file.localdata.go.kr/file/public_restroom_info/info",
)
OUT = Path("data/toilets-live.json")
UA = "SeniorToiletFinder/0.2 (+https://github.com/ohbeopseok-ops/senior-toilet-finder)"

NAME_KEYS = ["화장실명", "공중화장실명", "개방화장실명", "toilet_name"]
ROAD_KEYS = ["소재지도로명주소", "도로명주소", "소재지도로명주소명"]
LOT_KEYS = ["소재지지번주소", "지번주소", "소재지지번주소명"]
OPEN_KEYS = ["개방시간", "운영시간", "평일운영시간"]
TEL_KEYS = ["관리기관전화번호", "전화번호", "관리기관전화"]
LAT_KEYS = ["WGS84위도", "위도", "latitude", "lat"]
LNG_KEYS = ["WGS84경도", "경도", "longitude", "lng"]
AGENCY_KEYS = ["관리기관명", "관리기관", "제공기관명"]


def pick(row: dict[str, str], keys: list[str]) -> str:
    normalized = {str(k).replace(" ", "").strip(): (v or "").strip() for k, v in row.items()}
    for key in keys:
        v = normalized.get(key.replace(" ", ""))
        if v:
            return v
    return ""


def to_float(value: str):
    try:
        n = float(value)
        if n == n:
            return n
    except Exception:
        return None
    return None


def decode_csv(raw: bytes) -> str:
    for enc in ("utf-8-sig", "utf-8", "cp949", "euc-kr"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def extract_csv(raw: bytes) -> bytes:
    if raw[:2] == b"PK":
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            candidates = [n for n in z.namelist() if n.lower().endswith(".csv")]
            if not candidates:
                raise RuntimeError("ZIP archive contains no CSV")
            return z.read(candidates[0])
    return raw


def fetch() -> bytes:
    req = urllib.request.Request(
        SOURCE_URL,
        headers={
            "User-Agent": UA,
            "Accept": "text/csv,application/zip,application/octet-stream,*/*",
        },
    )
    with urllib.request.urlopen(req, timeout=45) as res:
        return res.read()


def load_previous() -> dict:
    try:
        return json.loads(OUT.read_text(encoding="utf-8"))
    except Exception:
        return {"items": []}


def write(payload: dict) -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    now = datetime.now(timezone.utc).isoformat()
    previous = load_previous()

    try:
        raw = extract_csv(fetch())
        text = decode_csv(raw)
        reader = csv.DictReader(io.StringIO(text))
        rows = list(reader)

        items = []
        for i, row in enumerate(rows):
            lat = to_float(pick(row, LAT_KEYS))
            lng = to_float(pick(row, LNG_KEYS))
            if lat is None or lng is None:
                continue
            if not (-90 <= lat <= 90 and -180 <= lng <= 180):
                continue

            name = pick(row, NAME_KEYS) or "공중화장실"
            items.append(
                {
                    "id": f"official-{i+1}",
                    "name": name,
                    "shortName": name,
                    "lat": lat,
                    "lng": lng,
                    "openHours": pick(row, OPEN_KEYS) or "개방시간 확인 필요",
                    "isOpen": True,
                    "stairs": False,
                    "ramp": False,
                    "handrail": False,
                    "emergencyBell": False,
                    "tel": pick(row, TEL_KEYS),
                    "address": pick(row, ROAD_KEYS) or pick(row, LOT_KEYS),
                    "agency": pick(row, AGENCY_KEYS),
                    "verified": True,
                    "openStatusVerified": bool(pick(row, OPEN_KEYS)),
                    "stairsVerified": False,
                    "sourceRegion": pick(row, ["시군명", "시군", "지역명"]),
                }
            )

        payload = {
            "source": "mois-localdata-public-restroom",
            "sourceUrl": SOURCE_URL,
            "generatedAt": now,
            "syncStatus": "ok",
            "officialRecordCount": len(rows),
            "usableCoordinateCount": len(items),
            "note": (
                "Official dataset synced. Only records with usable coordinates are published. "
                "The national standard dataset has not provided WGS84 coordinates since Feb 2025, "
                "so usableCoordinateCount may be 0 until a coordinate-bearing official regional source is configured."
            ),
            "items": items,
        }
        write(payload)
        print(f"official rows={len(rows)}, coordinate rows={len(items)}")
        return 0

    except Exception as exc:
        # Preserve last known-good coordinate records; expose sync failure as metadata.
        payload = {
            **previous,
            "source": previous.get("source", "mois-localdata-public-restroom"),
            "sourceUrl": SOURCE_URL,
            "generatedAt": previous.get("generatedAt"),
            "lastSyncAttemptAt": now,
            "syncStatus": "source-unavailable",
            "syncError": str(exc)[:500],
            "items": previous.get("items", []),
        }
        write(payload)
        print(f"sync unavailable: {exc}", file=sys.stderr)
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
