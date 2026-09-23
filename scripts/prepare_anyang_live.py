#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone

SRC=Path("data/anyang-toilets.json")
OUT=Path("data/toilets-live.json")

def main():
    src=json.loads(SRC.read_text(encoding="utf-8"))
    cols=src["columns"]
    items=[]
    for row in src["items"]:
        r=dict(zip(cols,row))
        open_hours=(r.get("openHours") or "").strip()
        open_cat=(r.get("openCategory") or "").strip()
        if not open_hours and open_cat=="상시":
            open_hours="24시간"
        items.append({
            "id":"anyang-"+str(r["id"]),
            "name":r["name"], "shortName":r["name"],
            "lat":None, "lng":None,
            "address":r.get("roadAddress") or r.get("lotAddress") or r.get("address") or "",
            "roadAddress":r.get("roadAddress") or "",
            "lotAddress":r.get("lotAddress") or "",
            "district":r.get("district") or "구 미분류",
            "sourceRegion":"안양시",
            "openCategory":open_cat,
            "openHours":open_hours or "개방시간 확인 필요",
            "isOpen":False, "openStatus":"unknown", "openStatusVerified":False,
            "stairs":False, "stairsVerified":False,
            "ramp":False, "handrail":False,
            "emergencyBell":bool(r.get("bell")),
            "accessibleToilet":bool((r.get("maleAccessible") or 0)>0 or (r.get("femaleAccessible") or 0)>0),
            "maleAccessible":int(r.get("maleAccessible") or 0),
            "femaleAccessible":int(r.get("femaleAccessible") or 0),
            "tel":str(r.get("tel") or ""),
            "verified":True,
            "source":"공중화장실정보.csv",
            "geocodeStatus":"pending"
        })
    payload={
        "source":"anyang-public-restroom-seed",
        "region":"경기도 안양시",
        "generatedAt":datetime.now(timezone.utc).isoformat(),
        "syncStatus":"seeded-for-geocoding",
        "officialRecordCount":len(items),
        "usableCoordinateCount":0,
        "items":items
    }
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
    print("seeded",len(items),"Anyang records")
if __name__=="__main__":
    main()
