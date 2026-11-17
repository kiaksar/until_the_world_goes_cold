import pymupdf
DOC=pymupdf.open('/Users/kiamt01/Desktop/music_projects/until_the_world_goes_cold/Trivium - Until The World Goes Cold - Pro - Drums.pdf')
p=DOC[0]
for b in p.get_text('dict')['blocks']:
    for l in b.get('lines',[]):
        for sp in l['spans']:
            if sp['font'].startswith('Edwin'):
                t=sp['text'].strip()
                if t and sp['origin'][1]<2500:
                    print(repr(t), sp['font'], round(sp['size'],1), 'x=%.0f y=%.0f'%(sp['origin'][0],sp['origin'][1]))
