#!/usr/bin/env python3
"""Export the existing bass transcription and an approximate PDF-derived drum guide."""
import json, collections, statistics, struct
from fractions import Fraction
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
PPQ=10080
BAR=PPQ*4

def vlq(n):
    b=[n&127]; n >>= 7
    while n: b.insert(0, 128 | (n&127)); n >>= 7
    return bytes(b)
def meta(kind, data): return bytes([255,kind])+vlq(len(data))+data
def export(path, notes, channel, name, program=None):
    events=[(0,0,meta(3,name.encode())),(0,0,meta(0x51,(363636).to_bytes(3,'big'))),(0,0,meta(0x58,bytes([4,2,24,8])))]
    if program is not None: events.append((0,0,bytes([0xc0|channel,program])))
    for start,end,pitch,velocity in notes:
        events.extend([(start,2,bytes([0x90|channel,pitch,velocity])),(max(start+1,end),1,bytes([0x80|channel,pitch,0]))])
    events.append((218*BAR,3,meta(0x2f,b'')))
    events.sort(key=lambda e:(e[0],e[1]))
    track=bytearray(); last=0
    for tick,_,msg in events:
        track.extend(vlq(tick-last)); track.extend(msg); last=tick
    path.write_bytes(b'MThd'+struct.pack('>IHHH',6,0,1,PPQ)+b'MTrk'+struct.pack('>I',len(track))+track)

def tick(f): return round(Fraction(f)*BAR)
data=json.loads((ROOT/'transcription.json').read_text())
bass=next(t for t in data['tracks'] if t['track_id']==7)
tuning=[42,37,32,27,22]
notes=[]; muted=0
for m in bass['measures']:
    for v in m['voices']:
        for e in v['events']:
            for n in e['notes']:
                fret=n.get('fret'); muted += fret is None
                start=(m['measure']-1)*BAR+tick(e['start'])
                dur=tick(e['duration'])
                notes.append((start,start+dur,tuning[n['string']-1]+(fret or 0),55 if fret is None else 90))
export(ROOT/'bass_raw.mid',notes,0,'Bass',33)
print('Bass notes:',len(notes),'muted approximations:',muted)
recs=json.loads((ROOT/'midi_work/recs2.json').read_text()); bars=collections.defaultdict(list)
for r in recs: bars[r['m']].append(r)
# Percussion staff convention. Mapping is provisional; the PDF has no instrument legend.
map_={(-7,'x'):49,(-6,'x'):42,(-5,'circlex'):46,(-5,'x'):42,(-4,'x'):51,(-2,'black'):48,(-1,'black'):38,(0,'black'):47,(1,'black'):50,(2,'black'):43,(4,'black'):36,(5,'x'):44}
dnotes=[]
for m,rs in sorted(bars.items()):
    xs=sorted(set(r['x'] for r in rs)); w=rs[0]['w']
    if len(xs)>1:
        diffs=[b-a for a,b in zip(xs,xs[1:]) if b-a>5]
        step=statistics.median(diffs) if diffs else w/8
        grid=min([4,8,16,32],key=lambda d:abs(step-w/d))
        while grid<32 and (xs[-1]-xs[0])/step>grid-1: grid*=2
    else: grid=8; step=w/8
    seen=set()
    for r in rs:
        p=map_.get((r['u'],r['g']))
        if p is None: continue
        i=min(grid-1,max(0,round((r['x']-xs[0])/step)))
        start=(m-1)*BAR+round(i*BAR/grid)
        if (start,p) in seen: continue
        seen.add((start,p)); dnotes.append((start,start+PPQ//8,p,90))
export(ROOT/'drums_approximate.mid',dnotes,9,'Drums - approximate')
print('Drum notes:',len(dnotes),'missing bars:',[m for m in range(1,219) if m not in bars])
