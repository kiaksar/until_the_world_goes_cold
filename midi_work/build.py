import json, collections
pages=json.load(open('/tmp/utwgc/pages.json'))
for pno,sysh,heads,vl,nums in pages:
    # barline xs per system
    for s in sysh:
        top=s[0]
        xs=sorted(set(x for x,y in vl if abs(y-top)<6))
        print('p%d top=%.0f'%(pno,top), len(xs), [round(x) for x in xs])
