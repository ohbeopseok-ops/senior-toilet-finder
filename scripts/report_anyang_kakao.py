#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime

SRC=Path("data/toilets-live.json")
JOUT=Path("data/anyang-kakao-geocode-report.json")
MOUT=Path("docs/ANYANG_KAKAO_GEOCODE_REPORT.md")

def main():
    d=json.loads(SRC.read_text(encoding="utf-8"))
    items=d.get("items",[])
    success=[x for x in items if x.get("lat") is not None and x.get("lng") is not None]
    failed=[x for x in items if x.get("lat") is None or x.get("lng") is None]
    district={}
    for x in items:
        k=x.get("district") or "구 미분류"
        z=district.setdefault(k,{"total":0,"success":0,"failed":0})
        z["total"]+=1
        if x.get("lat") is not None and x.get("lng") is not None: z["success"]+=1
        else: z["failed"]+=1
    for z in district.values(): z["successRate"]=round(z["success"]/z["total"]*100,1) if z["total"] else 0
    report={
        "generatedAt":datetime.now().isoformat(),
        "officialRecordCount":d.get("officialRecordCount",len(items)),
        "uniqueUsableCoordinateCount":len(success),
        "failedCount":len(failed),
        "successRate":round(len(success)/max(1,d.get("officialRecordCount",len(items)))*100,1),
        "dedupe":d.get("dedupe",{}),
        "districts":district,
        "failures":[{"id":x.get("id"),"name":x.get("name"),"district":x.get("district"),"roadAddress":x.get("roadAddress"),"lotAddress":x.get("lotAddress"),"error":x.get("geocodeError","")} for x in failed]
    }
    JOUT.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    lines=[
        "# 안양시 249건 Kakao 지오코딩 결과",
        "",
        f"- 원본 공공데이터: **{report['officialRecordCount']}건**",
        f"- 좌표 사용 가능(중복 제거 후): **{report['uniqueUsableCoordinateCount']}건**",
        f"- 지오코딩 실패: **{report['failedCount']}건**",
        f"- 원본 대비 좌표 성공률: **{report['successRate']}%**",
        f"- 병합된 중복: **{report['dedupe'].get('mergedDuplicates',0)}건**",
        "",
        "## 구별",
        ""
    ]
    for k,z in sorted(district.items()):
        lines.append(f"- {k}: {z['success']}/{z['total']} 성공 ({z['successRate']}%), 실패 {z['failed']}")
    lines += ["","## 실패 주소",""]
    if not failed: lines.append("- 없음")
    else:
        for x in failed:
            lines.append(f"- **{x.get('name','')}** · {x.get('district','')} · {x.get('roadAddress') or x.get('lotAddress') or x.get('address','')}")
    MOUT.write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(f"report success={len(success)} failed={len(failed)}")

if __name__=="__main__": main()
