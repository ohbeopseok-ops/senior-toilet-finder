#!/usr/bin/env python3
import json
from pathlib import Path
LIVE=Path("data/toilets-live.json")
FALLBACK=Path("data/toilets-fallback.json")

p=json.loads(LIVE.read_text(encoding="utf-8"))
usable=sum(1 for r in p.get("items",[]) if r.get("lat") not in (None,"") and r.get("lng") not in (None,""))
p["usableCoordinateCount"]=usable
p["syncStatus"]="live-anyang" if usable else "geocode-pending"
LIVE.write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding="utf-8")

if usable:
    fallback={
      "source":"retired-prototype-fallback",
      "generatedAt":None,
      "note":"The original 3-record Anyang prototype cache was retired after real Anyang coordinates became available.",
      "items":[]
    }
    FALLBACK.write_text(json.dumps(fallback,ensure_ascii=False,indent=2),encoding="utf-8")
    print("PROMOTED: usable coordinates=",usable)
else:
    print("NOT PROMOTED: no usable coordinates yet")
