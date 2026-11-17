import pymupdf, collections, itertools
DOC = pymupdf.open('/Users/kiamt01/Desktop/music_projects/until_the_world_goes_cold/Trivium - Until The World Goes Cold - Pro - Drums.pdf')
NOTEHEADS = {0xE0A4:'black', 0xE0A9:'x', 0xE0B3:'circlex'}
def page_geom(p):
    hl=[];vl=[]
    for dr in p.get_drawings():
        for it in dr['items']:
            if it[0]=='l':
                a,b=it[1],it[2]
                if abs(a.y-b.y)<1.2 and abs(a.x-b.x)>150: hl.append(round(a.y,1))
                if abs(a.x-b.x)<1.2 and abs(a.y-b.y)>150: vl.append((round(a.x,1),round(min(a.y,b.y),1),round(max(a.y,b.y),1)))
    return sorted(set(hl)), vl
def staves(hl):
    out=[]
    hs=sorted(hl)
    for i,y in enumerate(hs):
        run=[y]
        cur=y
        for z in hs[i+1:]:
            if abs(z-cur-82.7)<2.5: run.append(z); cur=z
            elif abs(z-cur)<2.5: pass
            elif z-cur<60: continue
            else: break
            if len(run)==5: break
        if len(run)==5 and run not in out: out.append(run)
    # dedupe overlaps
    ded=[]
    for r in out:
        if not any(abs(r[0]-d[0])<5 for d in ded): ded.append(r)
    return sorted(ded)
res={}
for pno,p in enumerate(DOC):
    hl,vl=page_geom(p)
    st=staves(hl)
    heads=[]
    for sp in [s for b in p.get_text('dict')['blocks'] for l in b.get('lines',[]) for s in l['spans'] if 'Leland' in s['font']]:
        for i,ch in enumerate(sp['text']):
            if ord(ch) in NOTEHEADS:
                heads.append((sp['origin'][0]+i*41.35, sp['origin'][1], NOTEHEADS[ord(ch)]))
    for s in st:
        top=s[0]
        sub=[h for h in heads if top-120<h[1]<s[-1]+120]
        res[(pno,round(top,1))]=sorted(sub)
print(len(res),'staves')
for k,v in sorted(res.items()):
    print(k,len(v),v[:4])
