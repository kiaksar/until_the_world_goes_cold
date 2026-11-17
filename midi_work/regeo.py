import pymupdf, json, collections, statistics

P='Trivium - Until The World Goes Cold - Pro - Drums.pdf'
DOC=pymupdf.open(P)
HEADS={0xE0A4:'black',0xE0A9:'x',0xE0B3:'circlex'}

def page(p):
    hl=[]; vl=[]
    for dr in p.get_drawings():
        for it in dr['items']:
            if it[0]=='l':
                a,b=it[1],it[2]
                if abs(a.y-b.y)<1.2 and abs(a.x-b.x)>1000: hl.append(round(a.y,1))
                if abs(a.x-b.x)<1.5 and 300<abs(a.y-b.y)<400:
                    vl.append((round(a.x,1),round(min(a.y,b.y),1),round(max(a.y,b.y),1)))
    hs=sorted(set(hl))
    systems=[]; i=0
    while i<len(hs):
        run=[hs[i]]; j=i+1
        while j<len(hs) and abs(hs[j]-run[-1]-82.7)<2.5: run.append(hs[j]); j+=1
        if len(run)>=5:
            systems.append({'top':run[0],'bot':run[-1],'spc':82.7})
            i=j
        else: i+=1
    for s in systems:
        s['bars']=sorted(set(x for x,y0,y1 in vl
                             if abs(y0-s['top'])<8 and 324<y1-y0<346))
    heads=[]
    for st in p.get_texttrace():
        if 'Leland' not in st['font']: continue
        for c in st['chars']:
            if c[0] in HEADS: heads.append((round(c[2][0],1),round(c[2][1],1),HEADS[c[0]]))
    nums=[]
    for b in p.get_text('dict')['blocks']:
        for l in b.get('lines',[]):
            for sp in l['spans']:
                if sp['font']=='Edwin-Italic' and sp['text'].strip().isdigit():
                    nums.append((int(sp['text'].strip()),round(sp['origin'][0],1),round(sp['origin'][1],1)))
    return systems,heads,nums

recs=[]
for pno,p in enumerate(DOC):
    systems,heads,nums=page(p)
    for s in systems:
        s['mid']=(s['top']+s['bot'])/2
        s['anch']=[]
    for n,nx,ny in nums:
        cand=[s for s in systems if s['top']-140<ny<s['bot']+140]
        if not cand: continue
        s=min(cand,key=lambda s:abs(s['mid']-ny))
        if not s['bars']: continue
        s['anch'].append((n,min(s['bars'],key=lambda b:abs(b-nx))))
    for s in systems:
        a=sorted(s['anch'])
        for k,(n,x0) in enumerate(a):
            x1=a[k+1][1] if k+1<len(a) else s['bars'][-1]
            if x1-x0<40: continue
            for x,y,g in heads:
                if x0-25<=x<=x1+25 and s['top']-210<y<s['bot']+210:
                    recs.append({'m':n,'x':x,'x0':x0,'w':x1-x0,
                                 'u':round((y-s['mid'])/s['spc']*2),'g':g})

print('recs',len(recs))
cov=sorted(set(r['m'] for r in recs))
print('covered',len(cov),'range',cov[0],cov[-1])
print('missing',[i for i in range(1,219) if i not in cov])
c=collections.Counter((r['u'],r['g']) for r in recs)
for k,v in sorted(c.items()): print(k,v)
print('dup n', [n for n,cc in collections.Counter(r['m'] for r in recs).items() if False])
json.dump(recs,open('midi_work/recs3.json','w'))
