#!/usr/bin/env python3
from __future__ import annotations
import json,re,math
from pathlib import Path

P=Path("data/toilets-live.json")

def norm(s):
    return re.sub(r"[^0-9a-z가-힣]","",str(s or "").lower())

def meters(a,b):
    R=6371000
    p1,p2=math.radians(a["lat"]),math.radians(b["lat"])
    dp=math.radians(b["lat"]-a["lat"]); dl=math.radians(b["lng"]-a["lng"])
    x=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return R*2*math.atan2(math.sqrt(x),math.sqrt(1-x))

def should_merge(a,b):
    if a.get("lat") is None or b.get("lat") is None: return False
    d=meters(a,b)
    same_name=norm(a.get("name")) and norm(a.get("name"))==norm(b.get("name"))
    same_addr=any(norm(a.get(k)) and norm(a.get(k))==norm(b.get(k)) for k in ("roadAddress","lotAddress"))
    return (same_name and d<=80) or (same_addr and d<=25)

def merge(a,b):
    a["sourceIds"]=sorted(set((a.get("sourceIds") or [a["id"]])+(b.get("sourceIds") or [b["id"]])))
    a["emergencyBell"]=bool(a.get("emergencyBell") or b.get("emergencyBell"))
    a["accessibleToilet"]=bool(a.get("accessibleToilet") or b.get("accessibleToilet"))
    a["maleAccessible"]=max(int(a.get("maleAccessible") or 0),int(b.get("maleAccessible") or 0))
    a["femaleAccessible"]=max(int(a.get("femaleAccessible") or 0),int(b.get("femaleAccessible") or 0))
    if not a.get("tel") and b.get("tel"): a["tel"]=b["tel"]
    return a

def main():
    data=json.loads(P.read_text(encoding="utf-8"))
    good=[x for x in data["items"] if x.get("lat") is not None and x.get("lng") is not None]
    failed=[x for x in data["items"] if x.get("lat") is None or x.get("lng") is None]
    merged=[]; duplicate_groups=[]
    for item in good:
        idx=next((i for i,x in enumerate(merged) if should_merge(x,item)),-1)
        if idx<0: merged.append(item)
        else:
            duplicate_groups.append({"kept":merged[idx]["id"],"merged":item["id"],"name":item.get("name","")})
            merged[idx]=merge(merged[idx],item)
    data["items"]=merged+failed
    data["usableCoordinateCount"]=len(merged)
    data["dedupe"]={
        "inputGeocoded":len(good),
        "uniqueGeocoded":len(merged),
        "mergedDuplicates":len(duplicate_groups),
        "groups":duplicate_groups
    }
    P.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"dedupe geocoded={len(good)} unique={len(merged)} merged={len(duplicate_groups)} failed={len(failed)}")

if __name__=="__main__": main()
