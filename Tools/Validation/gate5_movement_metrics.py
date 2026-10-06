from pathlib import Path
import json,math
b=Path('Saved/Gate5Validation');report=[]
for name in ['moving_host_baseline','moving_client_baseline','moving_host_emulated','moving_client_emulated']:
 for role in ['server','client']:
  r=json.loads((b/(name+'_'+role+'.json')).read_text())
  stable=[x for x in r['results'] if x['case'].endswith('_stable') or x['case']=='storage_floor_and_corrections']
  relevant=[s for s in r['samples'] if 37<s['t']<116 or 138<s['t']<184]
  report.append({'case':name,'role':role,'stable_checks':stable,'max_correction_cm':max(s['maxcorr'] for s in relevant),'floor_lost_samples':sum(not s['frame'] for s in relevant),'max_speed_cm_s':max(s['speed'] for s in r['samples'])})
Path('Docs/Gate5Results/movement-telemetry.json').write_text(json.dumps(report,indent=2))
for r in report:print(r['case'],r['role'],'correction_cm',r['max_correction_cm'],'floor_lost',r['floor_lost_samples'],'max_speed',r['max_speed_cm_s'])
