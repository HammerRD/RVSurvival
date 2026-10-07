"""Compare stable seated/moving windows, retaining setup/transition corrections."""
import json
from pathlib import Path
B=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate6PhysicalRefinement')
def summarize(path):
 d=json.loads(path.read_text(encoding='utf-8-sig'));samples=d.get('samples',[]);rows=[]
 for label,begin,end in [('moving_cab_seat',15.6,17.2),('moving_standing_aisle',19,20.3),('moving_dinette_front',21.4,22.4),('dinette_rear',27.0,28.1),('roof_walk',82.4,84.8)]:
  s=[r for r in samples if r.get('who')=='walker' and begin<=r['t']<=end]
  if not s:continue
  offsets=[r['seat_offset_cm'] for r in s if r.get('seat_offset_cm') is not None]
  rows.append({'window':label,'begin_s':begin,'end_s':end,'samples':len(s),'correction_count_change':s[-1]['corrections']-s[0]['corrections'],'local_x_span_cm':max(r['pos'][0] for r in s)-min(r['pos'][0] for r in s),'max_seat_relative_offset_cm':max(offsets) if offsets else None,'first_position':s[0]['pos'],'last_position':s[-1]['pos'],'raw_cumulative_max_cm':s[-1]['max_correction']})
 return {'source':str(path),'windows':rows}
history=sorted(B.glob('History/physical_host_100ms_2loss_*/*_client.json'),key=lambda p:p.stat().st_mtime)
out={'retained_prior_attempts':[summarize(p) for p in history],'final_source_host_driver':summarize(B/'physical_host_100ms_2loss_client.json'),'final_source_client_driver':summarize(B/'physical_client_100ms_2loss_server.json')}
(B.parent.parent/'Docs/Gate6PhysicalRefinement/correction-comparison.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
for name,data in out.items():
 if isinstance(data,dict):print(name,[(r['window'],r['correction_count_change'],round(r['local_x_span_cm'],3)) for r in data['windows']])
