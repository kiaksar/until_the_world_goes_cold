import pymupdf, json, collections, statistics
P='/Users/kiamt01/Desktop/music_projects/until_the_world_goes_cold/Trivium - Until The World Goes Cold - Pro - Drums.pdf'
DOC=pymupdf.open(P)
HEADS={0xE0A4:'black',0xE0A9:'x',0xE0B3:'circlex'}
SP=82.7

def page(p):
    hl=[]
    for dr in p.get_drawings():
        for it in dr['items']:
            if it[0]=='l':
                a,b=it[1],it[2]
                if abs(a.y-b.y)<1.2 and abs(a.x-b.x)>1000: hl.append(round(a.y,1))
    hs=sorted(set(hl))
    # full runs with SP spacing (5 or 6 lines)
    systems=[]
    i=0
    while i<len(hs):
        run=[hs[i]]; j=i+1
        while j<len(hs) and abs(hs[j]-run[-1]-SP)<2.5: run.append(hs[j]); j+=1
        if len(run)>=5:
            systems.append({'top':run[0],'bot':run[-1],'mid':(run[0]+run[-1])/2,'spc':SP})
            i=j
        else: i+=1
    heads=[]
    for s in p.get_texttrace():
        if 'Leland' not in s['font']: continue
        for c in s['chars']:
            if c[0] in HEADS: heads.append((round(c[2][0],1),round(c[2][1],1),HEADS[c[0]]))
    vl=[]
    for dr in p.get_drawings():
        for it in dr['items']:
            if it[0]=='l':
                a,b=it[1],it[2]
                if abs(a.x-b.x)<1.5 and 250<abs(a.y-b.y)<400: vl.append((round(a.x,1),round(min(a.y,b.y),1)))
    nums=[]
    for b in p.get_text('dict')['blocks']:
        for l in b.get('lines',[]):
            for sp in l['spans']:
                if sp['font']=='Edwin-Italic' and sp['text'].strip().isdigit():
                    nums.append((int(sp['text'].strip()),round(sp['origin'][0],1),round(sp['origin'][1],1)))
    return systems,heads,vl,nums

recs=[]
for pno,p in enumerate(DOC):
    systems,heads,vl,nums=page(p)
    for s in systems:
        s['bars']=sorted(set(x for x,y in vl if abs(y-s['top'])<8))
    for n,nx,ny in nums:
        cand=[s for s in systems if s['top']-140<ny<s['bot']+140]
        if not cand: continue
        s=min(cand,key=lambda s:abs((s['top']+s['bot'])/2-ny))
        if not s['bars']: continue
        bx=min(s['bars'],key=lambda b:abs(b-nx))
        s.setdefault('anch',[]).append((n,bx))
    for s in systems:
        a=sorted(s.get('anch',[]),key=lambda t:t[1])
        for k,(n,x0) in enumerate(a):
            x1=a[k+1][1] if k+1<len(a) else s['bars'][-1]
            for x,y,g in heads:
                if x0-30<=x<=x1+30 and s['top']-210<y<s['bot']+210:
                    recs.append({'m':n,'x':x,'x0':x0,'w':x1-x0,
                                 'u':round((y-s['mid'])/SP*2),'g':g})
print('recs',len(recs),'cov',len(set(r['m'] for r in recs)))
c=collections.Counter((r['u'],r['g']) for r in recs)
for k,v in sorted(c.items()): print(k,v)
json.dump(recs,open('/tmp/utwgc/recs2.json','w'))
