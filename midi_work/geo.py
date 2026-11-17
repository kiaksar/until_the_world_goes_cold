import pymupdf, collections
DOC=pymupdf.open('/Users/kiamt01/Desktop/music_projects/until_the_world_goes_cold/Trivium - Until The World Goes Cold - Pro - Drums.pdf')
HEADS={0xE0A4:'black',0xE0A9:'x',0xE0B3:'circlex'}
for pno,p in enumerate(DOC):
    vl=[]
    for dr in p.get_drawings():
        for it in dr['items']:
            if it[0]=='l':
                a,b=it[1],it[2]
                if abs(a.x-b.x)<1.2 and 300<abs(a.y-b.y)<360:
                    vl.append((a.x,min(a.y,b.y),max(a.y,b.y)))
    vl=sorted(set(vl))
    print('page',pno,'staff-span vlines',len(vl))
    syss=[]
    for x,y0,y1 in vl:
        for s in syss:
            if abs(s['y0']-y0)<3: s['xs'].append(x); break
        else: syss.append({'y0':y0,'y1':y1,'xs':[x]})
    for s in syss: print('  y',round(s['y0'],1),round(s['y1'],1),'span',round(s['y1']-s['y0'],1),'bars',len(s['xs']))
