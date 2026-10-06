"""Compare independent Gate 5 process receipts; never accesses live Unreal objects."""
import json,math,sys
from pathlib import Path
root=Path(__file__).resolve().parents[2]
name=sys.argv[1]
a=json.loads((root/'Saved/Gate5Validation'/f'{name}_server.json').read_text())
b=json.loads((root/'Saved/Gate5Validation'/f'{name}_client.json').read_text())
assert a['process_id']!=b['process_id'], 'Separate process PIDs required'
def nearest(rows,t):return min(rows,key=lambda r:abs(r['t']-t))
checks=[]
for t in [135.6,136.7,142.4,143.5,150.7,151.8,158.7,159.8,166.7,167.8,175]:
 s=nearest(a['samples'],t);c=nearest(b['samples'],t)
 checks.append({'case':f'inventory_at_{t}','pass':s['inventory']==c['inventory']})
 for key in s['containers']:
  checks.append({'case':f'{key}_at_{t}','pass':s['containers'][key]==c['containers'].get(key)})
for t in [36,55,153.5,159.5,176]:
 s=nearest(a['samples'],t);c=nearest(b['samples'],t)
 for player in ['host','client']:
  for key in ['nutrition','hydration','fatigue','reserve']:
   error=abs(s['needs'][player][key]-c['needs'][player][key])
   checks.append({'case':f'{player}_{key}_at_{t}','pass':error<.2,'error':error})
checks.append({'case':'workstation_counts_converge','pass':a['station_counts']==b['station_counts']})
rows=[s for s in a['samples'] if 37<s['t']<116 or 130<s['t']<176]
errors=[math.dist(s['local'],nearest(b['samples'],s['t'])['local']) for s in rows]
limit=75 if a['config'].get('network') else 30
checks.append({'case':'paired_passenger_local_position','pass':max(errors)<limit,'max_error_cm':max(errors),'limit_cm':limit})
for side in [a,b]:
 checks.append({'case':f"live_assertions_{side['process_id']}",'pass':all(r['pass'] for r in side['results']),'checks':len(side['results'])})
result={'config':a['config'],'server_pid':a['process_id'],'client_pid':b['process_id'],'checks':checks,'pass':all(x['pass'] for x in checks)}
out=root/'Docs/Gate5Results'/f'{name}_paired.json';out.write_text(json.dumps(result,indent=2))
print(json.dumps({'name':name,'checks':len(checks),'pass':result['pass'],'max_local_error_cm':max(errors),'failures':[x for x in checks if not x['pass']]}))
