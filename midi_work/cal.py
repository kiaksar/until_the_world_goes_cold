import pymupdf, json, collections
DOC=pymupdf.open('/Users/kiamt01/Desktop/music_projects/until_the_world_goes_cold/Trivium - Until The World Goes Cold - Pro - Drums.pdf')
HEADS={0xE0A4:'black',0xE0A9:'x',0xE0B3:'circlex'}
def systems(p):
    hl=[]
    for dr in p.get_drawings():
        for it in dr['items']:
            if it[0]=='l':
                a,b=it[1],it[2]
                if abs(a.y-b.y)<1.2 and abs(a.x-b.x)>1000: hl.append(round(a.y,1))
    hs=sorted(set(hl)); out=[]
    for i in range(len(hs)-4):
        run=hs[i:i+5]
        d=[round(run[j+1]-run[j],1) for j in range(4)]
        if all(abs(x-82.7)<2.5 for x in d) and not any(abs(run[0]-o[0])<5 for o in out):
            out.append(run)
    return out
tot=collections.Counter(); sysn=0
for pno,p in enumerate(DOC):
    syss=systems(p); sysn+=len(syss)
    heads=[]
    for b in p.get_text('rawdict')['blocks']:
        for l in b.get('lines',[]):
            for sp in l['spans']:
                if 'Leland' not in sp['font']: continue
                for c in sp['chars']:
                    if ord(c['c']) in HEADS: heads.append((c['bbox'][1],HEADS[ord(c['c'])]))
    for g in syss:
        mid=g[2]; spc=g[1]-g[0]
        for y,gl in heads:
            if g[0]-200<y<g[-1]+200:
                tot[(round((y-mid)/spc*2),gl)]+=1
print('systems',sysn)
for k,v in sorted(tot.items()): print(k,v)
