"""Quantify native correction reports; do not classify transition bursts as passes."""
from pathlib import Path
import json,re,datetime,math
root=Path('D:/GitHub/RVSurvival/RVSurvival');saved=root/'Saved/Gate6PhysicalRefinement'
phases=[('initial fixture / physical entry',0,13.6),('moving cab seated',13.6,17.5),
 ('moving cab release',17.5,19),('moving standing aisle',19,20.6),
 ('moving front Dinette entry',20.6,22.6),('moving front Dinette release',22.6,24),
 ('rear Dinette entry',26,28.2),('rear Dinette release',28.2,29.5),
 ('bed placement/rest',51,54.5),('bed wake placement',54.5,57),
 ('cab release after bed',63.5,65),('physical exit steps',66.2,69),
 ('ladder entry',74,76),('ladder ascent',76,80.4),('roof dismount',80.4,82),
 ('roof walking',82,85),('upper ladder return',88,90),('ladder descent',90,94.4),
 ('ladder ground dismount',94.4,96),('ground walk from ladder',96,99),
 ('closed-door approach',103,106.2),('back away from door',106.2,109.4),
 ('physical re-entry steps',111.3,114.3),('re-entry interior walking',114.3,118.7),
 ('repeat physical exit',118.7,121.3),('final driver release/exit',121.3,129.3)]
stamp=re.compile(r'^\[(\d{4}\.\d\d\.\d\d-\d\d\.\d\d\.\d\d:\d+)\]')
def timestamp(line):
 m=stamp.match(line)
 return datetime.datetime.strptime(m[1],'%Y.%m.%d-%H.%M.%S:%f') if m else None
out=[]
for name in ('physical_host_100ms_2loss','physical_client_100ms_2loss'):
 lines=(saved/(name+'_child.log')).read_text(encoding='utf-8-sig',errors='replace').splitlines()
 anchor=next(timestamp(s) for s in lines if 't.MaxFPS = "60"' in s)
 reports=[]
 for line in lines:
  m=re.search(r'RVPassenger (\S+) correction=([\d.]+)cm frame=(\S+)',line)
  if m:reports.append({'t':round((timestamp(line)-anchor).total_seconds(),3),'actor':m[1],'cm':float(m[2]),'frame':m[3]})
 raw=json.loads((saved/(name+'_client.json')).read_text(encoding='utf-8-sig'))
 rows=[]
 for label,begin,end in phases:
  events=[e for e in reports if begin<=e['t']<end]
  actual=[]
  for who in ('driver','walker'):
   points=[s for s in raw['samples'] if s['who']==who and begin<=s['t']<end]
   deltas=[math.dist(a['pos'],b['pos']) for a,b in zip(points,points[1:])]
   actual.append({'who':who,'samples':len(points),'max_adjacent_local_displacement_cm':max(deltas) if deltas else None})
  rows.append({'phase':label,'begin_s':begin,'end_s':end,'native_correction_events':len(events),'max_native_report_cm':max((e['cm'] for e in events),default=0),'first_event_s':events[0]['t'] if events else None,'last_event_s':events[-1]['t'] if events else None,'sampled_local_displacements':actual})
 out.append({'suite':name,'phase_time_anchor_utc':str(anchor),'phases':rows,'native_reports':reports})
result={'status':'transition smoothness unresolved pending visual sustained-key validation',
 'unchanged_existing_check':{'network_cm':75,'baseline_cm':30,'scope':'Gate6LayoutRework process_refinement reset then steady highway/turn walking; process_stations reset then moving workstation uses; not authoritative seat/bed/ladder placement transitions'},
 'interpretation':'Native metric compares acknowledged saved-move position to correction target, using relative coordinates only when movement bases agree. It is not measured visual mesh displacement. Intentional safe placements and stale acknowledgements may contribute, but unsolicited visual displacement cannot be excluded by these logs. Large transition reports exceed75cm if that steady-phase bound were applied; no new permissive transition bound is introduced. Passing occupancy/floor checks does not certify smoothness.',
 'runs':out}
(root/'Docs/Gate6PhysicalRefinement/transition-correction-assessment.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
for run in out:
 print(run['suite'],[(r['phase'],r['native_correction_events'],r['max_native_report_cm']) for r in run['phases'] if r['native_correction_events'] and r['begin_s']>=13.6])
