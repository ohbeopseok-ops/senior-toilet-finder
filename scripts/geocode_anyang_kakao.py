#!/usr/bin/env python3
from __future__ import annotations

import json, os, re, time, urllib.parse, urllib.request, urllib.error
from pathlib import Path
from datetime import datetime, timezone

SRC=Path("data/anyang-toilets.json")
OUT=Path("data/toilets-live.json")
KEY=os.environ.get("KAKAO_REST_API_KEY","").strip()
SLEEP=float(os.environ.get("KAKAO_GEOCODE_SLEEP","0.12"))

def request_json(url):
    req=urllib.request.Request(url,headers={"Authorization":f"KakaoAK {KEY}","User-Agent":"senior-toilet-finder/0.5"})
    with urllib.request.urlopen(req,timeout=15) as r:
        return json.loads(r.read().decode("utf-8"))

def clean(q):
    q=(q or "").strip()
    q=re.sub(r"\s+"," ",q)
    return q

def geocode(query):
    if not query: return None
    u="https://dapi.kakao.com/v2/local/search/address.json?"+urllib.parse.urlencode({"query":query,"size":5})
    body=request_json(u)
    docs=body.get("documents") or []
    if not docs: return None
    d=docs[0]
    return {
        "lat":float(d["y"]),"lng":float(d["x"]),
        "matchedAddress":d.get("address_name") or "",
        "roadAddress":(d.get("road_address") or {}).get("address_name") or "",
        "addressType":d.get("address_type") or ""
    }

def main():
    if not KEY:
        raise SystemExit("KAKAO_REST_API_KEY is required")
    src=json.loads(SRC.read_text(encoding="utf-8"))
    cols=src["columns"]
    items=[]; ok=0; fail=0; methods={}
    for i,row in enumerate(src["items"],1):
        r=dict(zip(cols,row))
        candidates=[]
        for method,key in [("roadAddress","roadAddress"),("lotAddress","lotAddress"),("address","address")]:
            q=clean(r.get(key))
            if q and q not in [x[1] for x in candidates]: candidates.append((method,q))
        hit=None; used_method=""; used_query=""; err=""
        for method,q in candidates:
            try:
                hit=geocode(q)
                if hit:
                    used_method=method; used_query=q; break
            except Exception as e:
                err=f"{type(e).__name__}: {e}"
            finally:
                time.sleep(SLEEP)
        if hit:
            ok+=1; methods[used_method]=methods.get(used_method,0)+1
        else:
            fail+=1
        open_hours=(r.get("openHours") or "").strip()
        open_cat=(r.get("openCategory") or "").strip()
        if not open_hours and open_cat=="상시": open_hours="24시간"
        items.append({
            "id":"anyang-"+str(r["id"]),
            "sourceIds":["anyang-"+str(r["id"])],
            "name":r["name"],"shortName":r["name"],
            "lat":hit["lat"] if hit else None,"lng":hit["lng"] if hit else None,
            "address":r.get("roadAddress") or r.get("lotAddress") or r.get("address") or "",
            "roadAddress":r.get("roadAddress") or "",
            "lotAddress":r.get("lotAddress") or "",
            "district":r.get("district") or "구 미분류",
            "sourceRegion":"안양시",
            "openCategory":open_cat,
            "openHours":open_hours or "개방시간 확인 필요",
            "isOpen":False,"openStatus":"unknown","openStatusVerified":False,
            "stairs":False,"stairsVerified":False,
            "ramp":False,"handrail":False,
            "emergencyBell":bool(r.get("bell")),
            "accessibleToilet":bool((r.get("maleAccessible") or 0)>0 or (r.get("femaleAccessible") or 0)>0),
            "maleAccessible":int(r.get("maleAccessible") or 0),
            "femaleAccessible":int(r.get("femaleAccessible") or 0),
            "tel":str(r.get("tel") or ""),
            "verified":True,
            "source":"공중화장실정보.csv",
            "geocodeStatus":"success" if hit else "failed",
            "geocodeProvider":"kakao-address",
            "geocodeMethod":used_method,
            "geocodeInput":used_query,
            "geocodeMatchedAddress":hit["matchedAddress"] if hit else "",
            "geocodeRoadAddress":hit["roadAddress"] if hit else "",
            "geocodeError":err
        })
        if i%25==0: print(f"processed {i}/{len(src['items'])} success={ok} fail={fail}")
    payload={
        "source":"anyang-public-restroom-seed+kakao-address",
        "region":"경기도 안양시",
        "generatedAt":datetime.now(timezone.utc).isoformat(),
        "syncStatus":"kakao-geocoded",
        "officialRecordCount":len(items),
        "usableCoordinateCount":ok,
        "geocode":{"provider":"Kakao Local address search","success":ok,"failed":fail,"successRate":round(ok/len(items)*100,1),"methods":methods},
        "items":items
    }
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"geocoded success={ok}/{len(items)} ({ok/len(items)*100:.1f}%) failed={fail}")

if __name__=="__main__": main()
