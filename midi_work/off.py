import pymupdf, collections
DOC=pymupdf.open('/Users/kiamt01/Desktop/music_projects/until_the_world_goes_cold/Trivium - Until The World Goes Cold - Pro - Drums.pdf')
HEADS={0xE0A4:'black',0xE0A9:'x',0xE0B3:'circlex'}
p=DOC[0]
# staff lines for sys0: find 5 lines with 82.7 spacing, longest span group
hl=[]
for dr in p.get_drawings():
    for it in dr['items']:
        if it[0]=='l':
            a,b=it[1],it[2]
            if abs(a.y-b.y)<1.2 and abs(a.x-b.x)>1000: hl.append(round(a.y,1))
hl=sorted(set(hl))
print(hl)
c=collections.Counter()
for b in p.get_text('dict')['blocks']:
  for l in b.get('lines',[]):
    for sp in l['spans']:
      if 'Leland' not in sp['font']: continue
      for i,ch in enumerate(sp['text']):
        if ord(ch) in HEADS and 2050<sp['origin'][1]<2490:
          c[(round(sp['origin'][1],1),HEADS[ord(ch)])]+=1
for k,v in sorted(c.items()): print(k,v)
