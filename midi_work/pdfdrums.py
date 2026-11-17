import pymupdf, collections, json

DOC = pymupdf.open('/Users/kiamt01/Desktop/music_projects/until_the_world_goes_cold/Trivium - Until The World Goes Cold - Pro - Drums.pdf')

NOTEHEADS = {0xE0A4:'black', 0xE0A9:'x', 0xE0B3:'circlex', 0xE0A3:'half'}

def page_geometry(p):
    hl=[]; vl=[]
    for dr in p.get_drawings():
        for it in dr['items']:
            if it[0]=='l':
                a,b=it[1],it[2]
                if abs(a.y-b.y)<1.2 and abs(a.x-b.x)>150: hl.append((a.y,a.x,b.x))
                if abs(a.x-b.x)<1.2 and abs(a.y-b.y)>150: vl.append((a.x,min(a.y,b.y),max(a.y,b.y)))
    return hl, vl

def staves(hl):
    ys=sorted(set(round(y,1) for y,_,_ in hl))
    groups=[]
    for y in ys:
        placed=False
        for g in groups:
            if abs(y-g[-1])<100: g.append(y); placed=True; break
        if not placed: groups.append([y])
    out=[]
    for g in groups:
        if len(g)>=5:
            diffs=[round(g[i+1]-g[i],1) for i in range(len(g)-1)]
            out.append({'top':g[0],'lines':g,'diffs':diffs})
    return out

p=DOC[0]
hl,vl=page_geometry(p)
for s in staves(hl): print(s['lines'], s['diffs'])
