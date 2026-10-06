from pathlib import Path
import json
import sys
name=sys.argv[1]
b=Path('Saved/Gate5Validation')
a=json.loads((b/(name+'_server.json')).read_text());c=json.loads((b/(name+'_client.json')).read_text());assert a['pid']!=c['pid']
checks=[]
for t in [2.5,4.5,6.5,8.5,10.5,12.5,17.5,19.5,24.5,29.5]:
 s=min(a['samples'],key=lambda r:abs(r['t']-t));r=min(c['samples'],key=lambda r:abs(r['t']-t))
 checks.append({'case':f'items_at_{t}','pass':all(s[k]==r[k] for k in ['host','client','container'])})
 checks.append({'case':f'needs_at_{t}','pass':all(abs(s['needs'][p][v]-r['needs'][p][v])<.01 for p in ['host','client'] for v in ['nutrition','hydration','fatigue']) and all(s['needs'][p]['rest']==r['needs'][p]['rest'] for p in ['host','client'])})
 checks.append({'case':f'rest_reservation_at_{t}','pass':s['rest_occupied']==r['rest_occupied']})
for r in [a,c]:checks.append({'case':str(r['pid'])+'_live','pass':all(x['pass'] for x in r['results'])})
print({'checks':len(checks),'pass':all(x['pass'] for x in checks),'failures':[x for x in checks if not x['pass']]})
Path('Docs/Gate5Results/'+name+'_paired.json').write_text(json.dumps({'server_pid':a['pid'],'client_pid':c['pid'],'checks':checks},indent=2))
for role,r in [('server',a),('client',c)]:
 r.pop('samples');Path('Docs/Gate5Results/'+name+'_'+role+'.json').write_text(json.dumps(r,indent=2))

assert all(x["pass"] for x in checks), checks
