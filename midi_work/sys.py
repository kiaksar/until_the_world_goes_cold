import pymupdf, collections, json
DOC=pymupdf.open('/Users/kiamt01/Desktop/music_projects/until_the_world_goes_cold/Trivium - Until The World Goes Cold - Pro - Drums.pdf')
HEADS={0xE0A4:'black',0xE0A9:'x',0xE0B3:'circlex'}
def systems(p):
    vl=[]
    for dr in p.get_drawings():
        for it in dr['items']:
            if it[0]=='l':
                a,b=it[1],it[2]
                if abs(a.x-b.x)<1.2 and 330<abs(a.y-b.y)<345:
                    vl.append((round(a.x,1),round(min(a.y,b.y),1)))
    vl=sorted(set(vl))
    out=[]
    for x,y in vl:
        for s in out:
            if abs(s['y']-y)<3: s['xs'].append(x); break
        else: out.append({'y':y,'xs':[x]})
    return sorted(out,key=lambda s:s['y'])
for pno,p in enumerate(DOC[:1]):
    for i,s in enumerate(systems(p)):
        print('sys',i,'y=%.1f'%s['y'],'bars',len(s['xs']))
        print('   ', [round(x) for x in sorted(set(s['xs']))])
