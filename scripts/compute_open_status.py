#!/usr/bin/env python3
"""
Compute current open/closing-soon/closed status from normalized openHours.

This parser is intentionally conservative:
- If the schedule cannot be parsed, status remains 'unknown'.
- Only a successfully parsed schedule sets isOpen.
- 'closing-soon' means <= 30 minutes until close.
"""

from __future__ import annotations
import json,re
from datetime import datetime,time,timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

SRC=Path("data/toilets-live.json")
SEOUL=ZoneInfo("Asia/Seoul")

def hm(text):
    m=re.match(r"^(\d{1,2})(?::?(\d{2}))?$",text.strip())
    if not m:return None
    h=int(m.group(1)); mi=int(m.group(2) or 0)
    if 0<=h<=24 and 0<=mi<60:
        if h==24:h=0
        return time(h,mi)
    return None

def parse_window(text):
    s=(text or "").strip()
    if not s:return None
    if any(x in s for x in ["24시간","00:00~24:00","00:00-24:00","상시"]):
        return ("always",None,None)
    s=s.replace("～","~").replace("–","-").replace("—","-")
    m=re.search(r"(\d{1,2}:?\d{0,2})\s*[~-]\s*(\d{1,2}:?\d{0,2})",s)
    if not m:return None
    a,b=hm(m.group(1)),hm(m.group(2))
    return ("window",a,b) if a and b else None

def status_for(text,now):
    parsed=parse_window(text)
    if not parsed:return {"openStatus":"unknown","isOpen":False,"closingSoon":False}
    if parsed[0]=="always":
        return {"openStatus":"open","isOpen":True,"closingSoon":False}
    _,start,end=parsed
    cur=now.time()
    if start<=end:
        opened=start<=cur<end
    else:
        opened=cur>=start or cur<end
    if not opened:
        return {"openStatus":"closed","isOpen":False,"closingSoon":False}
    end_dt=datetime.combine(now.date(),end,tzinfo=SEOUL)
    if start>end and cur>=start:
        end_dt+=timedelta(days=1)
    mins=(end_dt-now).total_seconds()/60
    soon=0<=mins<=30
    return {"openStatus":"closing-soon" if soon else "open","isOpen":True,"closingSoon":soon}

def main():
    payload=json.loads(SRC.read_text(encoding="utf-8"))
    now=datetime.now(SEOUL)
    parsed=0
    for item in payload.get("items",[]):
        st=status_for(item.get("openHours",""),now)
        item.update(st)
        if st["openStatus"]!="unknown":parsed+=1
    payload["openStatusComputedAt"]=now.isoformat()
    payload["openStatusParsedCount"]=parsed
    SRC.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"open-hours parsed={parsed}/{len(payload.get('items',[]))}")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
