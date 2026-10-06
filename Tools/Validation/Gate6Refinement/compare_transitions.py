import json,math,sys
from pathlib import Path
root=next(p for p in Path(__file__).resolve().parents if (p/'RVSurvival.uproject').exists())
name=sys.argv[1]
a=json.loads((root/'Saved/Gate6Refinement'/f'{name}_server.json').read_text())
b=json.loads((root/'Saved/Gate6Refinement'/f'{name}_client.json').read_text())
assert a['pid']!=b['pid']
rows=[s for s in a['samples'] if 18<s['t']<27]
errors=[math.dist(s['passenger'],min(b['samples'],key=lambda r:abs(r['t']-s['t']))['passenger']) for s in rows]
limit=75 if a['config'].get('network') else 30
checks=[{'case':'distinct_processes','pass':a['pid']!=b['pid']},
 {'case':'live_server_checks','pass':all(r['pass'] for r in a['results'])},
 {'case':'live_client_checks','pass':all(r['pass'] for r in b['results'])},
 {'case':'paired_moving_transition_and_walking','pass':bool(errors) and max(errors)<limit,'maximum_cm':max(errors),'limit_cm':limit}]
result={'name':name,'checks':checks,'pass':all(c['pass'] for c in checks)}
(root/'Docs/Gate6Refinement'/f'{name}_paired.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result));assert result['pass']
