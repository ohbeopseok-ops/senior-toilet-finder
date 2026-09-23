#!/usr/bin/env python3
from pathlib import Path
import base64,gzip,json

p1=Path("data/bootstrap/anyang.part1.b64").read_text(encoding="utf-8").strip()
p2=Path("data/bootstrap/anyang.part2.b64").read_text(encoding="utf-8").strip()
raw=gzip.decompress(base64.b64decode(p1+p2)).decode("utf-8")
payload=json.loads(raw)

if payload.get("region")!="경기도 안양시" or payload.get("count")!=249:
    raise SystemExit("unexpected Anyang payload")

out=Path("data/anyang-toilets.json")
out.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
print(f"wrote {out} with {payload['count']} records")
