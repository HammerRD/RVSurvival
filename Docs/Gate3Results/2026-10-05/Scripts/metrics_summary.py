import json,ast,pathlib
P=pathlib.Path('D:/GitHub/RVSurvival/RVSurvival/Docs/Gate3Results/2026-10-05')
rows=[]
for n in ['final_material_host','final_material_client','process_host_driver_client','process_client_driver_server','network_host_driver_client','network_client_driver_server','final_material_network_client_server','soak_host','soak_client']:
 p=P/(n+'.json')
 if not p.exists():continue
 d=json.load(open(p));stats=[]
 for r in d['results']:
  try:
   v=ast.literal_eval(r['detail'])
   if isinstance(v,dict) and 'drift_cm' in v:stats.append(v)
  except Exception:pass
 rows.append({'run':n,'checks':len(d['results']),'failed':sum(not r['pass'] for r in d['results']),'max_standing_drift_cm':max((s['drift_cm'] for s in stats),default=None),'max_measured_correction_cm':max((s['max_correction_cm'] for s in stats),default=None),'max_phase_correction_count':max((s['corrections'] for s in stats),default=None)})
json.dump(rows,open(P/'measurement_summary.json','w'),indent=2)
