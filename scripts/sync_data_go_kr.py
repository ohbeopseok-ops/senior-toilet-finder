#!/usr/bin/env python3
"""
V0.4.2 DATA.GO.KR public-restroom adapter.

Required:
  DATA_GO_KR_SERVICE_KEY (GitHub Secret)
  DATA_GO_KR_ENDPOINT    (GitHub Actions variable)

The endpoint is deliberately configurable instead of hard-coded because
data.go.kr OpenAPI operation paths can differ by product/version.

Pipeline:
  data.go.kr API -> normalize restroom fields -> preserve address/opening info
  -> write data/toilets-live.json
  -> JUSO geocoding workflow enriches coordinates separately.

This script also writes data/schema-report.json so the real response schema
can be reviewed without ever exposing the service key.
"""

from __future__ import annotations

import json
import os
import re
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

KEY = os.getenv("DATA_GO_KR_SERVICE_KEY", "").strip()
ENDPOINT = os.getenv("DATA_GO_KR_ENDPOINT", "").strip()
OUT = Path("data/toilets-live.json")
SCHEMA = Path("data/schema-report.json")
UA = "SeniorToiletFinder/0.4.2"

ALIASES = {
    "name": ["toiletName","toiletNm","화장실명","공중화장실명","개방화장실명","name"],
    "road": ["rdnmadr","roadAddr","소재지도로명주소","도로명주소"],
    "lot": ["lnmadr","jibunAddr","소재지지번주소","지번주소"],
    "open": ["openTime","openHours","개방시간","운영시간","평일운영시간"],
    "tel": ["phoneNumber","telno","관리기관전화번호","전화번호"],
    "agency": ["institutionName","manageAgency","관리기관명","제공기관명"],
    "lat": ["latitude","lat","WGS84위도","위도"],
    "lng": ["longitude","lng","lon","WGS84경도","경도"],
    "maleDisabled": ["maleDisableToilet","남성용장애인화장실대변기수"],
    "femaleDisabled": ["femaleDisableToilet","여성용장애인화장실대변기수"],
    "emergencyBell": ["emergencyBellYn","비상벨설치여부","비상벨유무"],
}

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def pick(row, names):
    normalized={str(k).replace(" ","").lower():v for k,v in row.items()}
    for n in names:
        k=n.replace(" ","").lower()
        if k in normalized and normalized[k] not in (None,""):
            return normalized[k]
    return ""

def to_float(v):
    try: return float(v)
    except Exception: return None

def truthy(v):
    s=str(v or "").strip().lower()
    return s in {"y","yes","true","1","있음","설치","설치됨"}

def fetch_page(page=1, per_page=1000):
    params={
        "serviceKey":KEY,
        "pageNo":page,
        "numOfRows":per_page,
        "type":"json",
        "_type":"json",
        "resultType":"json",
    }
    sep="&" if "?" in ENDPOINT else "?"
    url=ENDPOINT+sep+urllib.parse.urlencode(params, safe="%")
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/json, text/json, */*"})
    with urllib.request.urlopen(req,timeout=45) as res:
        raw=res.read()
    text=raw.decode("utf-8-sig",errors="replace")
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise RuntimeError("API response was not JSON: "+text[:300]) from e

def locate_rows(obj):
    candidates=[]
    def walk(x,path="root"):
        if isinstance(x,list) and x and all(isinstance(i,dict) for i in x[:5]):
            candidates.append((path,x))
        elif isinstance(x,dict):
            for k,v in x.items():
                walk(v,path+"."+str(k))
    walk(obj)
    if not candidates:
        return [],""
    candidates.sort(key=lambda t:len(t[1]),reverse=True)
    return candidates[0][1],candidates[0][0]

def schema_report(obj, rows, row_path):
    return {
        "generatedAt":now_iso(),
        "endpointConfigured":bool(ENDPOINT),
        "topLevelKeys":list(obj.keys()) if isinstance(obj,dict) else [],
        "rowPath":row_path,
        "rowCountInFirstResponse":len(rows),
        "sampleFieldNames":sorted({str(k) for r in rows[:5] for k in r.keys()}),
    }

def normalize(rows):
    items=[]
    for i,row in enumerate(rows):
        name=str(pick(row,ALIASES["name"]) or "공중화장실").strip()
        road=str(pick(row,ALIASES["road"]) or "").strip()
        lot=str(pick(row,ALIASES["lot"]) or "").strip()
        open_hours=str(pick(row,ALIASES["open"]) or "개방시간 확인 필요").strip()
        lat=to_float(pick(row,ALIASES["lat"]))
        lng=to_float(pick(row,ALIASES["lng"]))
        disabled=(str(pick(row,ALIASES["maleDisabled"]) or "") not in ("","0")) or (str(pick(row,ALIASES["femaleDisabled"]) or "") not in ("","0"))
        items.append({
            "id":f"data-go-kr-{i+1}",
            "name":name,
            "shortName":name,
            "lat":lat,
            "lng":lng,
            "openHours":open_hours,
            "isOpen":False,
            "openStatus":"unknown",
            "openStatusVerified":open_hours not in ("","개방시간 확인 필요"),
            "stairs":False,
            "stairsVerified":False,
            "ramp":False,
            "handrail":False,
            "emergencyBell":truthy(pick(row,ALIASES["emergencyBell"])),
            "accessibleToilet":disabled,
            "tel":str(pick(row,ALIASES["tel"]) or "").strip(),
            "address":road or lot,
            "agency":str(pick(row,ALIASES["agency"]) or "").strip(),
            "verified":True,
            "source":"data.go.kr",
        })
    return items

def main():
    if not KEY:
        print("DATA_GO_KR_SERVICE_KEY not configured; sync skipped.")
        return 0
    if not ENDPOINT:
        print("DATA_GO_KR_ENDPOINT not configured; sync skipped.")
        return 0

    obj=fetch_page()
    rows,row_path=locate_rows(obj)
    SCHEMA.write_text(json.dumps(schema_report(obj,rows,row_path),ensure_ascii=False,indent=2),encoding="utf-8")

    if not rows:
        raise RuntimeError("No record list found in API response; inspect data/schema-report.json")

    payload={
        "source":"data.go.kr-public-restroom-api",
        "sourceUrl":ENDPOINT,
        "generatedAt":now_iso(),
        "syncStatus":"ok",
        "officialRecordCount":len(rows),
        "usableCoordinateCount":sum(1 for x in normalize(rows) if x.get("lat") is not None and x.get("lng") is not None),
        "items":normalize(rows),
    }
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"rows={len(rows)}, rowPath={row_path}")
    print("fields="+",".join(SCHEMA.exists() and json.loads(SCHEMA.read_text(encoding="utf-8"))["sampleFieldNames"] or []))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
