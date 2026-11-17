import json, statistics, collections
from fractions import Fraction

recs=json.load(open('/tmp/utwgc/recs.json'))
DRUM={(-7,'x'):49,(-6,'x'):42,(-5,'circlex'):46,(-5,'x'):42,(-4,'x'):51,
      (-2,'black'):48,(-1,'black'):38,(0,'black'):47,(1,'black'):50,(2,'black'):43,
      (4,'black'):36,(5,'x'):52}
bym=collections.defaultdict(list)
for r in recs: bym[r['m']].append(r)

measures={}
for m,ev in bym.items():
    w=ev[0]['w']
    xs=sorted(set(round(e['x'],1) for e in ev))
    n=len(xs)
    if n==1: D=8
    else:
        d=statistics.median([xs[i+1]-xs[i] for i in range(len(xs)-1)])
        D=min([4,8,16], key=lambda D: abs(d-w/D) if w/D>0 else 1e9)
        # ensure fit
        while D<32 and (xs[-1]-xs[0])/d > D-1: D*=2
    unit=(xs[-1]-xs[0])/(n-1) if n>1 else w/8
    idx={x:i for i,x in enumerate(xs)}
    hits=collections.defaultdict(set)
    for e in ev:
        i=idx[round(e['x'],1)]
        mid=DRUM.get((e['u'],e['g']))
        if mid: hits[i].add(mid)
    measures[m]=(D,hits)
print('measures',len(measures))
cov=sorted(measures)
for miss in [i for i in range(1,219) if i not in measures]:
    src=miss-1 if miss-1 in measures else miss+1
    measures[miss]=measures[src]
Ds=collections.Counter(v[0] for v in measures.values())
print('grids',Ds)
json.dump({str(k):[v[0],[sorted(x) for x in v[1].values()],[k2 for k2 in v[1]]] for k,v in measures.items()},open('/tmp/utwgc/drumbars.json','w'))
json.dump({str(k):[v[0],{str(i):sorted(s) for i,s in v[1].items()}] for k,v in measures.items()},open('/tmp/utwgc/drumbars2.json','w'))
