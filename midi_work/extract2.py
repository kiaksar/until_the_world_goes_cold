import pymupdf, json, collections
P='/Users/kiamt01/Desktop/music_projects/until_the_world_goes_cold/Trivium - Until The World Goes Cold - Pro - Drums.pdf'
DOC=pymupdf.open(P)
HEADS={0xE0A4:'black',0xE0A9:'x',0xE0B3:'circlex'}

def page_data(p):
    hl=[]
    for dr in p.get_drawings():
        for it in dr['items']:
            if it[0]=='l':
                a,b=it[1],it[2]
                if abs(a.y-b.y)<1.2 and abs(a.x-b.x)>1000: hl.append(round(a.y,1))
    hs=sorted(set(hl)); systems=[]
    for i in range(len(hs)-4):
        r=hs[i:i+5]
        if all(abs(r[j+1]-r[j]-82.7)<2.5 for j in range(4)) and not any(abs(r[0]-o[0])<5 for o in systems):
            systems.append(r)
    heads=[]
    for s in p.get_texttrace():
        if 'Leland' not in s['font']: continue
        for c in s['chars']:
            if c[0] in HEADS: heads.append((round(c[2][0],1),round(c[2][1],1),HEADS[c[0]]))
    vlines=[]
    for dr in p.get_drawings():
        for it in dr['items']:
            if it[0]=='l':
                a,b=it[1],it[2]
                if abs(a.x-b.x)<1.5 and 250<abs(a.y-b.y)<400: vlines.append((round(a.x,1),round(min(a.y,b.y),1)))
    # measure numbers
    nums=[]
    for b in p.get_text('dict')['blocks']:
        for l in b.get('lines',[]):
            for sp in l['spans']:
                if sp['font']=='Edwin-Italic' and sp['text'].strip().isdigit():
                    nums.append((int(sp['text'].strip()), round(sp['origin'][0],1), round(sp['origin'][1],1)))
    return systems, heads, vlines, nums

allp=[]
for pno,p in enumerate(DOC):
    allp.append((pno,)+page_data(p))
json.dump(allp,open('/tmp/utwgc/pages.json','w'))
print('pages',len(allp))
for pno,sysh,heads,vl,nums in allp:
    print('page',pno,'sys',len(sysh),'heads',len(heads),'vlines',len(vl),'nums',len(nums), 'numrange', (min(n for n,_,_ in nums), max(n for n,_,_ in nums)) if nums else None)
