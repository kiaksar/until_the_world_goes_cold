#!/usr/bin/env python3
"""Best-effort extraction of percussion glyphs. Timing and GM mapping are estimates."""
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
PPQ=10080; BAR=4*PPQ; notes=[]; grids={}
for m,rs in sorted(bars.items()):
 # Diamond-x belongs to a chord displaced slightly to the left of its stem.
 for r in rs:
  if r['g']=='diamondx':
   close=[q['x'] for q in rs if q is not r and abs(q['x']-r['x'])<60]
   if close: r['x']=min(close,key=lambda x:abs(x-r['x']))
 xs=sorted(set(r['x'] for r in rs))
 # Move adjacent x-noteheads in the same chord to the same time. The engraved
 # upper head sits to the right of a lower cymbal when their stems conflict.
 for i,x in enumerate(xs[:-1]):
  y=xs[i+1]; left=[r for r in rs if r['x']==x]; right=[r for r in rs if r['x']==y]
  if 70<y-x<125 and any(q['u']==-6 and q['g']=='x' for q in left) and any(q['u']==-7 and q['g']=='x' for q in right) and any(q['u']==4 for q in left):
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
  # The first beat of bar 28 is an explicitly bracketed eighth-note triplet.
  if m==28 and len(xs)==6: fraction=[0,1/6,1/4,3/8,1/2,3/4][xs.index(r['x'])]
  start=(m-1)*BAR+round(fraction*BAR); end=min(start+PPQ//8,m*BAR)
  if (start,pitch) in seen: continue
  seen.add((start,pitch)); notes.append((start,end,pitch,90))
def vlq(n):
 b=[n&127]; n>>=7
 while n: b.insert(0,(n&127)|128); n>>=7
 return bytes(b)
def meta(k,b): return bytes([255,k])+vlq(len(b))+b
events=[(0,0,meta(3,b'Drums - best effort')),(0,0,meta(0x51,(363636).to_bytes(3,'big'))),(0,0,meta(0x58,bytes([4,2,24,8])))]
for start,end,p,v in notes: events += [(start,2,bytes([0x99,p,v])),(end,1,bytes([0x89,p,0]))]
events.append((218*BAR,3,meta(0x2f,b''))); events.sort(key=lambda e:(e[0],e[1]))
track=bytearray(); last=0
for t,_,msg in events: track.extend(vlq(t-last)); track.extend(msg); last=t
(ROOT/'drums_best_effort.mid').write_bytes(b'MThd'+struct.pack('>IHHH',6,0,1,PPQ)+b'MTrk'+struct.pack('>I',len(track))+track)
print('notes',len(notes),'bars',len(bars),'missing',[n for n in range(1,219) if n not in bars]); print('bar1',[(round((s%BAR)/BAR,4),p) for s,e,p,v in notes if s<BAR])
