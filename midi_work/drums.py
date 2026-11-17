import json
pages=json.load(open('/tmp/utwgc/pages.json'))
PAD=200
recs=[]
for pno,sysh,heads,vl,nums in pages:
    syss=[]
    for s in sysh:
        top=s[0]; bot=s[-1]; mid=s[2]; spc=s[1]-s[0]
        xs=sorted(set(x for x,y in vl if abs(y-top)<6))
        syss.append({'top':top,'bot':bot,'mid':mid,'spc':spc,'bars':xs})
    # assign measure numbers to system by y
    for n,nx,ny in nums:
        cand=[s for s in syss if s['top']-120<ny<s['bot']+120]
        if not cand: continue
        s=min(cand,key=lambda s:abs(s['top']-ny))
        bars=s['bars']
        i=min(range(len(bars)),key=lambda j:abs(bars[j]-nx))
        s.setdefault('anchors',[]).append((n,bars[i]))
    # sort measures per system
    ms=[]
    for s in syss:
        a=s.get('anchors',[])
        if not a: continue
        a.sort(key=lambda t:t[1])
        for k,(n,x0) in enumerate(a):
            x1 = a[k+1][1] if k+1<len(a) else s['bars'][-1]
            ms.append({'n':n,'x0':x0,'x1':x1,'top':s['top'],'bot':s['bot'],'mid':s['mid'],'spc':s['spc']})
    for x,y,g in heads:
        best=None
        for m in ms:
            if m['x0']-40<=x<=m['x1']+40 and m['top']-200<y<m['bot']+200:
                d=abs((m['top']+m['bot'])/2 - y)
                if best is None or d<best[0]: best=(d,m)
        if best is None: continue
        m=best[1]
        u=round((y-m['mid'])/m['spc']*2)
        recs.append({'m':m['n'],'x':x,'u':u,'g':g,'w':m['x1']-m['x0'],'x0':m['x0']})
print('recs',len(recs),'measures covered',len(set(r['m'] for r in recs)))
cov=sorted(set(r['m'] for r in recs))
print('missing',[i for i in range(1,219) if i not in cov][:40])
import collections
c=collections.Counter((r['u'],r['g']) for r in recs)
for k,v in sorted(c.items()): print(k,v)
json.dump(recs,open('/tmp/utwgc/recs.json','w'))
