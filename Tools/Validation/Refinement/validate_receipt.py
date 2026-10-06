import json,sys
from pathlib import Path
d=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8-sig'))
rows=d if isinstance(d,list) else d.get('results',d.get('checks',[]))
if isinstance(rows,int):
 assert d.get('pass') is True and rows>0,d
 print('checks='+str(rows)+' failures=0')
else:
 assert isinstance(rows,list) and rows, 'Missing assertion rows'
 bad=[r for r in rows if not isinstance(r,dict) or r.get('pass') is not True]
 print(json.dumps({'checks':len(rows),'failures':bad}))
 assert not bad,'Assertion failed'
