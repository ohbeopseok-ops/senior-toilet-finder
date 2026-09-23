#!/usr/bin/env python3
from __future__ import annotations
import json
from collections import Counter,defaultdict
from pathlib import Path
from datetime import datetime, timezone

SRC=Path("data/toilets-live.json")
OUT=Path("data/anyang-geocode-report.json")
MD=Path("docs/ANYANG_GEOCODE_REPORT.md")

def main():
    p=json.loads(SRC.read_text(encoding="utf-8"))
    rows=p.get("items",[])
    by=defaultdict(list)
    for r in rows:
        by[r.get("district") or "구 미분류"].append(r)
    summary={}
    for d,arr in sorted(by.items()):
        success=[r for r in arr if r.get("lat") not in (None,"") and r.get("lng") not in (None,"")]
        failed=[r for r in arr if r.get("lat") in (None,"") or r.get("lng") in (None,"")]
        summary[d]={
            "total":len(arr),
            "success":len(success),
            "successRate":round(len(success)*100/len(arr),1) if arr else 0,
            "statusCounts":dict(Counter(r.get("geocodeStatus","unknown") for r in arr)),
            "failures":[{"name":r.get("name"),"address":r.get("address"),"status":r.get("geocodeStatus"),"error":r.get("geocodeError","")} for r in failed[:20]]
        }
    total=len(rows)
    success=sum(1 for r in rows if r.get("lat") not in (None,"") and r.get("lng") not in (None,""))
    result={"generatedAt":datetime.now(timezone.utc).isoformat(),"total":total,"success":success,"successRate":round(success*100/total,1) if total else 0,"districts":summary}
    OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")

    lines=["# 안양시 JUSO 지오코딩 결과","",f"- 전체: **{success}/{total} ({result['successRate']}%)**","",
           "| 구 | 전체 | 성공 | 성공률 |","|---|---:|---:|---:|"]
    for d,s in summary.items():
        lines.append(f"| {d} | {s['total']} | {s['success']} | {s['successRate']}% |")
    lines+=["","## 실패 주소 TOP"]
    for d,s in summary.items():
        lines+=["",f"### {d}"]
        if not s["failures"]:
            lines.append("- 실패 없음")
        else:
            for x in s["failures"][:10]:
                lines.append(f"- {x['name']} — {x['address']} — {x['status']}")
    MD.write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(f"geocode success={success}/{total} ({result['successRate']}%)")
if __name__=="__main__":
    main()
