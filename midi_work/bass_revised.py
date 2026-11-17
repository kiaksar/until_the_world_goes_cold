#!/usr/bin/env python3
"""Partial score-checked corrections to the prior bass transcription.
Remaining bars are unverified; tuplets inferred by the prior transcription are approximations.
"""
import json, struct
from fractions import Fraction as F
from pathlib import Path
R=Path(__file__).resolve().parent.parent
P=10080; B=4*P
bars=json.loads((R/'transcription.json').read_text())['tracks'][6]['measures']
notes=[]
for bar in bars:
 m=bar['measure']; es=[e for e in bar['voices'][0]['events'] if not e['notes'] or all(n.get('fret') is not None for n in e['notes'])]
 if 161 <= m <= 166: continue  # source shows no notation here
 if m in (9,11,13,15,25,27,29,31,73,75,77,79,217):
  ds=[F(1,8)]*6+[F(1,4)]
 elif m in (18,20,22,24,66,70,72,130,132,134,136,142,144,202,204,206,208,214,216):
  ds=[F(1,8),F(1,16),F(1,16)]+[F(1,8)]*6
 elif m in (68,140):
  ds=[F(1,8),F(1,16),F(1,16)]+[F(1,8)]*4+[F(1,4)]
 elif m in (82,83,84,108,135):
  ds=[F(1,8)]*len(es)
 elif m in (80,): ds=[F(1,2)]+[F(1,8)]*4
 elif m in (113,115,117,119,121,123,125,185,187,189,191,193,195,197):
  ds=[F(1,8),F(1,4),F(1,8),F(1,8),F(1,4),F(1,8)]
 elif m in (114,116,118,120,122,124,126,186,188,190,194,196,198):
  ds=[F(1,8),F(1,4)]+[F(1,8)]*5
 elif m==128: ds=[F(1,8)]*6+[F(1,4)]
 elif m in (137,139,209,211): ds=[F(1,8),F(1,8),F(1,4),F(1,8),F(1,8),F(1,4)]
 elif m==138: ds=[F(1,8),F(1,16),F(1,16)]+[F(1,8)]*4+[F(1,4)]
 elif m in (210,212): ds=[F(1,8),F(1,16),F(1,16)]+[F(1,8)]*6
 elif m in (145,147,149,151): ds=[F(1,16)]*9+[F(3,16)]+[F(1,16)]*4
 elif m in (146,148): ds=([F(1,16)]*4+[F(1,4)])*2
 elif m==150: ds=([F(1,16)]*3+[F(5,16)])*2
 elif m==152: ds=[F(1,16)]*6+[F(1,8)]*3+[F(1,4)]
 elif m in (48,63,96):
  ds=[F(1,8)]*5+[F(3,8)]
 else: ds=[F(e['duration']) for e in es]
 if sum(ds)!=1: print("WARNING",m,"duration",sum(ds),"events",len(es),"durations",len(ds))
 pos=F(0)
 for e,d in zip(es,ds):
  for n in e['notes']:
   pitch=[42,37,32,27,22][n['string']-1]+(n.get('fret') or 0)
   start=round(((m-1)+pos)*B); end=round(((m-1)+pos+d)*B)
   # A parenthesized open note following the tied quarter is a continuation.
   if m in (10,12,14,16,26,28,30,32,74,76,78,80,138,140,210,212,218) and pos==0 and pitch==22:
    prior=next((x for x in reversed(notes) if x[2]==pitch and x[1]==start),None)
    if prior: prior[1]=end; continue
   notes.append([start,end,pitch,90 if n.get('fret') is not None else 55])
  pos+=d
assert all(0<=n[2]<128 and n[1]>n[0] for n in notes)
def vlq(n):
 b=[n&127];n>>=7
 while n:b.insert(0,128|(n&127));n>>=7
 return bytes(b)
def meta(t,d):return bytes([255,t])+vlq(len(d))+d
events=[(0,0,meta(3,b'Bass - partially corrected')), (0,0,meta(0x51,(363636).to_bytes(3,'big'))),(0,0,meta(0x58,bytes([4,2,24,8]))),(0,0,bytes([0xc0,33]))]
for a,b,p,v in notes:events.extend([(a,2,bytes([0x90,p,v])),(b,1,bytes([0x80,p,0]))])
events.append((218*B,3,meta(0x2f,b'')));events.sort(key=lambda e:(e[0],e[1]));track=bytearray();last=0
for tick,_,msg in events:track.extend(vlq(tick-last));track.extend(msg);last=tick
out=R/'bass_raw.mid';out.write_bytes(b'MThd'+struct.pack('>IHHH',6,0,1,P)+b'MTrk'+struct.pack('>I',len(track))+track)
print('notes',len(notes),'end tick',last,'bars',last//B)
