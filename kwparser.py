#!/usr/bin/env python3

from pathlib import Path

def kwparse(kws: list[str], txtdesc: str, kwlst: str):
 txtdesc = Path(txtdesc).read_text()
 txtdesclower = txtdesc.lower()
 lst=[]
 for kw in kws:
  haystack: str
  needle: str
  if len(kw) <= 2:
   haystack = txtdesc
   needle = kw
  else:
   haystack = txtdesclower
   needle = kw.lower()
  chkbeg = kw[0].isalnum()
  chkend = kw[-1].isalnum()
  off = 0
  while True:
   idx = haystack.find(needle, off)
   if -1 == idx:
    break
   if chkbeg and idx != 0 and haystack[idx-1].isalnum():
    off=idx+1
    continue
   if chkend and idx+len(kw) != len(haystack) and haystack[idx+len(kw)].isalnum():
    off=idx+1
    continue
   lst.append((idx,kw,))
   break
 lst.sort()
 lstjoined = ', '.join([tup[1] for tup in lst])
 Path(kwlst).write_text(lstjoined)
