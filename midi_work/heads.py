import pymupdf, json, collections
DOC=pymupdf.open('/Users/kiamt01/Desktop/music_projects/until_the_world_goes_cold/Trivium - Until The World Goes Cold - Pro - Drums.pdf')
HEADS={0xE0A4:'black',0xE0A9:'x',0xE0B3:'circlex'}
out=[]
for pno,p in enumerate(DOC):
    for b in p.get_text('rawdict')['blocks']:
        for l in b.get('lines',[]):
            for sp in l['spans']:
                if 'Leland' not in sp['font']: continue
                for c in sp['chars']:
                    u=ord(c['c'])
                    if u in HEADS:
                        bb=c['bbox']
                        out.append({'page':pno,'x':round(bb[0],1),'y':round(bb[1],1),'g':HEADS[u]})
print(len(out))
c=collections.Counter((o['page'],o['g']) for o in out)
print(c)
json.dump(out,open('/tmp/utwgc/heads.json','w'))
