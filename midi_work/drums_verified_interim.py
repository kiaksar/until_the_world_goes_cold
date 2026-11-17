#!/usr/bin/env python3
"""Interim extraction: a few score-verified bars corrected; remaining timing estimates."""
import collections, json, statistics, struct
from pathlib import Path
import pymupdf
ROOT=Path(__file__).resolve().parent.parent
R=json.loads((ROOT/'midi_work/recs2.json').read_text())
# Supplement noteheads omitted by the first extractor. Locate them relative to the
# nearest already identified staff and measure, using the PDF's own coordinates.
doc=pymupdf.open(str(ROOT/'Trivium - Until The World Goes Cold - Pro - Drums.pdf'))
# Reuse the geometry detector (its output file is an intermediate only).
import sys
sys.path.insert(0,str(ROOT/'midi_work'))
import regeo
R=[]
for page in doc:
 systems,heads,nums=regeo.page(page)
 for s in systems:
  s['mid']=(s['top']+s['bot'])/2; s['anch']=[]
 for n,nx,ny in nums:
  cand=[s for s in systems if s['top']-140<ny<s['bot']+140 and s['bars']]
  if cand:
   s=min(cand,key=lambda s:abs(s['mid']-ny)); s['anch'].append((n,min(s['bars'],key=lambda b:abs(b-nx))))
 extras=[]
 for st in page.get_texttrace():
  for c in st['chars']:
   if ('Bravura' in st['font'] and c[0]==0xe0f9) or ('Leland' in st['font'] and c[0]==0xe0a3):
    extras.append((c[2][0],c[2][1],'diamondx' if c[0]==0xe0f9 else 'half'))
 for s in systems:
  a=sorted(s['anch'])
  for k,(n,x0) in enumerate(a):
   x1=a[k+1][1] if k+1<len(a) else s['bars'][-1]
   if x1-x0<40: continue
   for x,y,g in heads+extras:
    if x0-25<=x<=x1+25 and s['top']-210<y<s['bot']+210:
     R.append(dict(m=n,x=x,x0=x0,w=x1-x0,u=round((y-s['mid'])/82.7*2),g=g))
# General MIDI assignments inferred from percussion staff position; the source
# does not provide a drum key. Diamond-x is interpreted as a cymbal.
MAP={(-7,'x'):49,(-6,'x'):42,(-5,'circlex'):46,(-5,'x'):42,(-4,'x'):51,(-2,'black'):48,(-1,'black'):38,(0,'black'):47,(1,'black'):50,(2,'black'):43,(4,'black'):36,(5,'x'):44,(-7,'diamondx'):52,(-6,'diamondx'):52,(-1,'half'):38,(0,'half'):47,(1,'half'):50,(2,'half'):43,(4,'half'):36}
bars=collections.defaultdict(list)
for r in R: bars[r['m']].append(r)
print('heads',len(R),'supplemental',collections.Counter(r['g'] for r in R if r['g'] in ('half','diamondx')))
print('unmapped',collections.Counter((r['u'],r['g']) for r in R if (r['u'],r['g']) not in MAP))
PPQ=10080; BAR=4*PPQ; notes=[]; grids={}; applied=set()
for m,rs in sorted(bars.items()):
 # Offset cymbal heads in repeated eighth-note passages.
 if m in (33,37,41,81,85,89,93,211):
  xx = sorted(set(r['x'] for r in rs))
  if 75 < xx[1]-xx[0] < 110:
   for r in rs:
    if r['x'] == xx[1]: r['x'] = xx[0]
 # Adjacent noteheads in these chords are offset in the engraving.
 if m in (17,19,21,23,24,65,67,69,71,72,129,131,133,135,137,139,141,143,201,203,205,207,213,215):
  xx = sorted(set(r['x'] for r in rs))
  if m not in (24,72): left, right = xx[0], xx[1]
  else: left, right = xx[-2], xx[-1]
  if 75 < right-left < 120:
   for r in rs:
    if r['x'] == right: r['x'] = left
 # In bar 217, tom heads are displaced to the right of their chord.
 if m == 217:
  for r in rs:
   if r['u'] == 1:
    near = [q['x'] for q in rs if q['u'] == 2 and 75 < r['x'] - q['x'] < 120]
    if near: r['x'] = min(near, key=lambda x: r['x'] - x)
 # Diamond-x belongs to a chord displaced slightly to the left of its stem.
 for r in rs:
  if r['g']=='diamondx':
   close=[q['x'] for q in rs if q is not r and abs(q['x']-r['x'])<60]
   if close: r['x']=min(close,key=lambda x:abs(x-r['x']))
 if m == 139:
  xx = sorted(set(r['x'] for r in rs))
  if 75 < xx[1]-xx[0] < 110:
   for r in rs:
    if r['x'] == xx[1]: r['x'] = xx[0]
 xs=sorted(set(r['x'] for r in rs))
 # Move adjacent x-noteheads in the same chord to the same time. The engraved
 # upper head sits to the right of a lower cymbal when their stems conflict.
 for i,x in enumerate(xs[:-1]):
  y=xs[i+1]; left=[r for r in rs if r['x']==x]; right=[r for r in rs if r['x']==y]
  if 70<y-x<125 and any(q['u']==-6 and q['g']=='x' for q in left) and any(q['u']==-7 and q['g']=='x' for q in right) and any(q['u']==4 for q in left+right):
   for q in right: q['x']=x
 xs=sorted(set(r['x'] for r in rs)); diffs=[b-a for a,b in zip(xs,xs[1:]) if b-a>35]
 # Most passages use eighths; use the most frequent local engraving step.
 # Each beat is still quantized locally: irregular spacing, tuplets and sparse
 # rests can defeat the estimate and require a score review.
 if diffs:
  candidates=sorted(diffs)
  def score(s): return sum(abs(d/s-round(d/s))<0.18 for d in diffs)
  step=max(candidates,key=lambda s:(score(s),s))
  # Prefer the eighth-note step for bars where an eighth grid fits the span.
  span=xs[-1]-xs[0]
  possible=[d for d in diffs if 5.4<=span/d<=7.6]
  if possible: step=statistics.median(possible)
  if span/step>7.6: step*=2
 else: step=rs[0]['w']/8
 grids[m]=step
 seen=set()
 for r in rs:
  pitch=MAP.get((r['u'],r['g']))
  if pitch is None: continue
  i=max(0,min(15,round((r['x']-xs[0])/step*2)))
  # Leave all rests and the full seven unprinted bars empty.
  fraction=(i/16)
  # Independently checked against the printed beams, rests, and chords.
  verified = {2:[0,1,2], 16:[0,1,2,2.5,3,3.5],
              18:[0,.5,.75,1,1.5,2,2.5,3,3.5], 26:[0,1,2,3],
              32:[0,.5,.75,1,1.5,2,2.5,3,3.5],
              48:[0,.5,1,1.25,1.5,1.75,2],
              199:[j/4 for j in range(16)], 217:[0,.5,1,2,2.5,3]}
  for n in (1,3,5,7,9,11,13,15,25,27,29,31): verified[n] = [j/2 for j in range(8)]
  for n in (2,4,6,8,10,12,14): verified[n] = [0,1,2]
  for n in (17,19,21,23): verified[n] = [0,.5,1,2,2.5,3]
  for n in (18,22): verified[n] = [0,.5,.75,1,1.5,2,2.5,3,3.5]
  for n in (20,24): verified[n] = [0,.5,.75,1,1.5,2,2.5,3]
  verified[30] = [0,1,2,3]
  for n in (73,75,77,79,95): verified[n] = [j/2 for j in range(8)]
  for n in (33,34,35,37,38,39,40,41,43,44,45,46,47,81,82,83,85,86,87,88,89,91,92,93,94,95):
   verified[n] = [j/2 for j in range(8)]
  for n in (36,42,84,90): verified[n] = [0,.5,1,1.5,2,2.5,3,3.5,3.75]
  for n in (49,57,97): verified[n] = [0,.5,1,1.5,2,3,3.5]
  for n in (50,58,98,106): verified[n] = [0,.5,1,2,2.5,3]
  for n in (51,53,55,59,61,99,101,103,107,109,111): verified[n] = [0,1,2,3,3.5]
  for n in (52,54,60,62,100,102,108,110): verified[n] = [0,1,2,2.5,3]
  for n in list(range(113,120))+list(range(121,128))+list(range(185,192))+list(range(193,196))+[197,198]:
   verified[n] = [j/2 for j in range(8)]
  for n in range(153,159): verified[n] = [j/4 for j in range(16)]
  verified[120] = [0,.5,1,1.5,2,2.5,3,3.25,3.5,3.75]
  for n in (169,177): verified[n] = [0,.5,1,1.5,2,3,3.5]
  for n in (170,178): verified[n] = [0,.5,1,2,2.5,3]
  for n in (171,173,175,179,181,183): verified[n] = [0,1,2,3,3.5]
  for n in (172,174,180,182): verified[n] = [0,1,2,2.5,3]
  verified[28] = [0,2/3,1,1.5,2,3]
  for n in (56,176): verified[n] = [0,.5,.75,1,1.25,1.5,1.75,2,2.25,2.5,2.75,3,3.25,3.5,3.75]
  verified[63] = [0,.5,1,1.5,2]
  verified[74] = [0,.5,1,1.5,2,3]
  verified[104] = [0,.5,1,1.5,2,2.25,2.5,2.75,3,3.5]
  verified[105] = [0,.5,1,1.5,2,3,3.5]
  for n in (112,184): verified[n] = [0,1,2,2.25,2.5,2.75,3,3.25,3.5,3.75]
  verified[128] = [0,.5,1,2,2.25,2.5,2.75,3,3.25,3.5,3.75]
  verified[144] = [0,.5,.75,1,1.5,2,2.5,3,3.5]
  for n in (145,147,149,151): verified[n] = [0,.25,.5,.75,1,1.25,1.5,1.75,2,3,3.25,3.5,3.75]
  for n in (146,148,150): verified[n] = [0,.25,.5,1,2,2.25,2.5,3]
  verified[159] = [j/2 for j in range(8)]
  verified[160] = [0,.5,1,1.5,2,2.25,2.5,2.75,3,3.25,3.5,3.75]
  verified[167] = [0,.5,1.5,2.5,3,3.5]
  verified[168] = [.5,1.5,2,2.25,2.5,2.75,3,3.25,3.5,3.75]
  verified[192] = [0,.5,1,1.5,2,2.5,3,3.25,3.5,3.75]
  verified[196] = [0,.5,1,1.5,2,2.5,2.75,3,3.5]
  verified[136] = [0,.5,.75,1,1.5,2,2.25,2.5,2.75,3,3.25,3.5,3.75]
  verified[152] = verified[56]
  verified[200] = [0,.25,.5,.75,1,1.25,1.5,1.75,2,2.25,2.5,3,3.5]
  for n in (209,210,211): verified[n] = [j/2 for j in range(8)]
  verified[212] = [0,.5,1,1.5,2,2.5,3]
  verified[161] = [0]
  verified[76] = [0,.5,.75,1,1.5,2,3]
  verified[78] = [0,1,2,3]
  verified[80] = verified[32]
  verified[96] = verified[48]
  for n in (65,67,69,71,129,131,133,135,137,139,141,143,201,203,205,207,213,215):
   verified[n] = [0,.5,1,2,2.5,3]
  for n in (66,70,130,134,142,202,206,214):
   verified[n] = [0,.5,.75,1,1.5,2,2.5,3,3.5]
  for n in (68,72,132,204,208,216):
   verified[n] = [0,.5,.75,1,1.5,2,2.5,3]
  verified[138] = [0,.5,.75,1,1.5,2,2.5,3,3.5]
  verified[140] = [0,.5,.75,1,1.5,2,2.5,3]
  if m in verified and r is rs[0] and len(xs) != len(verified[m]):
   print("TEMPLATE MISMATCH",m,len(xs),len(verified[m]))
  if m in verified and len(xs) == len(verified[m]):
   applied.add(m)
   fraction = verified[m][xs.index(r['x'])]/4
  # The first beat of bar 28 is an explicitly bracketed eighth-note triplet.
  if m==28 and len(xs)==6: fraction=[0,1/6,1/4,3/8,1/2,3/4][xs.index(r['x'])]
  start=(m-1)*BAR+round(fraction*BAR); end=min(start+PPQ//8,m*BAR)
  if (start,pitch) in seen: continue
  seen.add((start,pitch)); notes.append((start,end,pitch,90))
print('TEMPLATE APPLIED',len(applied),sorted(applied))
print('UNREVIEWED',sorted(set(range(1,219))-applied-{64,162,163,164,165,166,218}))
def vlq(n):
 b=[n&127]; n>>=7
 while n: b.insert(0,(n&127)|128); n>>=7
 return bytes(b)
def meta(k,b): return bytes([255,k])+vlq(len(b))+b
events=[(0,0,meta(3,b'Drums - partially verified interim')),(0,0,meta(0x51,(363636).to_bytes(3,'big'))),(0,0,meta(0x58,bytes([4,2,24,8])))]
for start,end,p,v in notes: events += [(start,2,bytes([0x99,p,v])),(end,1,bytes([0x89,p,0]))]
events.append((218*BAR,3,meta(0x2f,b''))); events.sort(key=lambda e:(e[0],e[1]))
track=bytearray(); last=0
for t,_,msg in events: track.extend(vlq(t-last)); track.extend(msg); last=t
(ROOT/'drums_verified_interim.mid').write_bytes(b'MThd'+struct.pack('>IHHH',6,0,1,PPQ)+b'MTrk'+struct.pack('>I',len(track))+track)
print('notes',len(notes),'bars',len(bars),'missing',[n for n in range(1,219) if n not in bars]); print('bar1',[(round((s%BAR)/BAR,4),p) for s,e,p,v in notes if s<BAR])
