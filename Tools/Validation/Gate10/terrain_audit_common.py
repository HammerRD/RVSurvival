"""Shared read-only terrain sampling for the WNY region audits; registers no callbacks."""
import unreal,json,math
# Mirrors RVWorldContentLibrary.cpp CreateRegionLandscape/GradeRegionSitePads; used only as the intended target.
def original(x,y):return (1800*math.sin(x/65000)*math.cos(y/72000)+650*math.sin(y/25000))*max(0,min(1,(abs(y)-3000)/12000))
pads=[('Pine Creek Fuel',-130000,4900,2500,2900,0),('Erie Road Service',-60000,-5500,3000,4100,0),('Hawthorne Farm',0,46000,2800,3500,original(0,45000)),
 ('Maple Run Campground',75000,46000,2800,3500,original(75000,45000)),('Rowland Crossroads',140000,5000,2500,3900,0)]
garage=('Erie garage approach V2',-60000,-7000,4000,6600,0)
def smooth(a):a=max(0,min(1,a));return a*a*(3-2*a)
def intended(x,y):
 h=original(x,y)
 for sites,falloff in [(pads,1400),([garage],9000)]:
  for _,cx,cy,hx,hy,height in sites:
   margin=400 if sites is pads else 0 # Grading flattens one Landscape quad beyond each authored pad.
   h=h+(height-h)*smooth(1-max(0,max(abs(x-cx)-hx-margin,abs(y-cy)-hy-margin))/falloff)
 return h
def stats(values):
 values=[v for v in values if v is not None]
 return {'n':len(values),'min':round(min(values),3),'max':round(max(values),3),'mean':round(sum(values)/len(values),3),'mean_abs':round(sum(abs(v) for v in values)/len(values),3)} if values else {'n':0}
def delta(s,key,ref):return None if key not in s or ref is None else s[key]-ref
def worst(rows,key,count=5):
 rows=[r for r in rows if r.get(key) is not None];rows.sort(key=lambda r:-abs(r[key]));return rows[:count]
def collect(w):
 requests=[]
 for name,cx,cy,hx,hy,height in pads+[garage]:
  nx,ny=int(2*hx/250),int(2*hy/250)
  for i in range(nx+1):
   for j in range(ny+1):requests.append(('pad',name,cx-hx+i*2*hx/nx,cy-hy+j*2*hy/ny,{'pad_target':height}))
 roads={}
 for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
  if isinstance(a,unreal.RVRegionRoad):
   label=a.get_actor_label();spline=a.get_editor_property('Route');roads[label]=spline.get_number_of_spline_points();length=spline.get_spline_length()
   for i in range(roads[label]):
    v=spline.get_location_at_spline_point(i,unreal.SplineCoordinateSpace.WORLD);requests.append(('road_point',label,v.x,v.y,{'index':i,'spline_z':v.z}))
   d=0.0
   while d<=length:
    v=spline.get_location_at_distance_along_spline(d,unreal.SplineCoordinateSpace.WORLD);requests.append(('road_dense',label,v.x,v.y,{'distance_cm':round(d),'spline_z':v.z}));d+=1000
   spline=None
  a=None
 raw=json.loads(unreal.RVWorldContentLibrary.audit_region_terrain_samples(w,[unreal.Vector2D(r[2],r[3]) for r in requests]))
 assert len(raw['Samples'])==len(requests),'sample count mismatch'
 layer_keys=[l['Name']+'Z' for l in raw['EditLayers']]
 rows=[]
 for (kind,name,x,y,extra),s in zip(requests,raw['Samples']):
  r={'kind':kind,'site':name,'x':round(x,1),'y':round(y,1),**extra,**{k:v for k,v in s.items() if k not in ('X','Y')},'intended_z':round(intended(x,y),3),'original_z':round(original(x,y),3)}
  if kind=='pad':
   for key in ['FinalZ','CollisionZ','FirstHitZ']+layer_keys:r['d_'+key]=delta(s,key,extra['pad_target'])
  else:
   road=s.get('MeshZ') if s.get('MeshClass')=='RVRegionRoad' else None;r['road_surface_z']=road
   for key in ['FinalZ','CollisionZ']+layer_keys:r['road_minus_'+key]=None if road is None else road-s[key] if key in s else None
   r['landscape_over_road']=None if road is None or 'CollisionZ' not in s else s['CollisionZ']-road
  rows.append(r)
 summary={'landscape':{k:v for k,v in raw.items() if k!='Samples'},'roads':roads,'pads':{},'road_results':{}}
 for name,*_ in pads+[garage]:
  p=[r for r in rows if r['kind']=='pad' and r['site']==name]
  summary['pads'][name]={'target_z':p[0]['pad_target'],'samples':len(p),**{k:stats([r.get(k) for r in p]) for k in ['d_FinalZ','d_CollisionZ','d_FirstHitZ']+['d_'+k for k in layer_keys]},
   'collision_minus_final':stats([r['CollisionZ']-r['FinalZ'] for r in p if 'CollisionZ' in r and 'FinalZ' in r]),
   'collision_minus_original':stats([r['CollisionZ']-r['original_z'] for r in p if 'CollisionZ' in r]),
   'worst_collision':[{k:r.get(k) for k in ('x','y','FinalZ','CollisionZ','FirstHitZ','FirstHitActor','original_z','d_CollisionZ')} for r in worst(p,'d_CollisionZ')],
   'worst_final':[{k:r.get(k) for k in ('x','y','FinalZ','CollisionZ','original_z','d_FinalZ')} for r in worst(p,'d_FinalZ')]}
 for label in roads:
  for kind in ['road_point','road_dense']:
   p=[r for r in rows if r['kind']==kind and r['site']==label]
   summary['road_results'].setdefault(label,{})[kind]={'samples':len(p),'road_mesh_hits':sum(r['road_surface_z'] is not None for r in p),
    **{k:stats([r.get(k) for r in p]) for k in ['road_minus_FinalZ','road_minus_CollisionZ']+['road_minus_'+k for k in layer_keys]},
    'spline_minus_collision':stats([r['spline_z']-r['CollisionZ'] for r in p if 'CollisionZ' in r]),
    'collision_minus_intended':stats([r['CollisionZ']-r['intended_z'] for r in p if 'CollisionZ' in r]),
    'worst':[{k:r.get(k) for k in ('index','distance_cm','x','y','spline_z','road_surface_z','FinalZ','CollisionZ','FirstHitActor','road_minus_CollisionZ')} for r in worst(p,'road_minus_CollisionZ')]}
 roads_hit=[r for r in rows if r['kind']=='road_point' and r['road_surface_z'] is not None]
 summary['all_road_points']={'road_surface_minus_intended':stats([r['road_surface_z']-r['intended_z'] for r in roads_hit]),'road_surface_minus_collision':stats([r['road_surface_z']-r['CollisionZ'] for r in roads_hit if 'CollisionZ' in r]),
  'off_by_more_than_30cm':sum(abs(r['road_surface_z']-r.get('CollisionZ',r['road_surface_z']))>30 for r in roads_hit),'no_road_mesh_hit':sum(r['kind']=='road_point' and r['road_surface_z'] is None for r in rows)}
 summary['all_samples_collision_minus_original']=stats([r['CollisionZ']-r['original_z'] for r in rows if 'CollisionZ' in r])
 return summary,rows
def passes(summary,rows,tolerance=3.0,road_tolerance=10.0):
 """Graded pads must be at target in final heightmap, edit layer and collision; roads ~18 cm above terrain."""
 failures=[]
 for r in rows:
  if r['kind']=='pad':
   for k in [k for k in r if k.startswith('d_') and k!='d_FirstHitZ']:
    if r[k] is None or abs(r[k])>tolerance:failures.append((r['site'],r['x'],r['y'],k,r[k]))
  elif r['kind']=='road_point' and r.get('road_surface_z') is not None and r.get('road_minus_CollisionZ') is not None and abs(r['road_minus_CollisionZ']-18)>road_tolerance:
   failures.append((r['site'],r.get('index'),r['x'],r['y'],'road_minus_CollisionZ',r['road_minus_CollisionZ']))
 return failures
