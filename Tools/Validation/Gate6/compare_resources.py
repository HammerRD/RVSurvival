import json,sys
from pathlib import Path
name=sys.argv[1];b=Path('Saved/Gate6Validation')
a=json.loads((b/(name+'_server.json')).read_text());c=json.loads((b/(name+'_client.json')).read_text());results=[]
assert a['pid']!=c['pid']
for t in [6.7,7.6,22.8,28.9,30,35.7]:
 x=min(a['samples'],key=lambda s:abs(s['t']-t));y=min(c['samples'],key=lambda s:abs(s['t']-t))
 ok=(abs(x['fuel']-y['fuel'])<.02 and abs(x['house']-y['house'])<2 and x['generator']==y['generator'] and x['lights']==y['lights'] and x['can']==y['can'])
 results.append({'case':'stable_convergence_'+str(t),'pass':ok,'server':x,'client':y})
out={'name':name,'different_processes':True,'results':results}
Path('Docs/Gate6Results/'+name+'_paired.json').write_text(json.dumps(out,indent=2))
print(name,'paired',sum(r['pass'] for r in results),'/',len(results))
sys.exit(0 if all(r['pass'] for r in results) else 1)
