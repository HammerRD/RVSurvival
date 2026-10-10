"""Authored bound clearance review; Unreal PCG still generates all foliage."""
import unreal,time,json,gc,traceback,math,random,sys
from pathlib import Path
out=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate10Validation');started=time.time();phase=0;handle=None
def intersects_segment(p,q,lo,hi):
 # Liang-Barsky tests authored rectangles, not a runtime foliage generator.
 t0,t1=0.,1.
 for axis in range(2):
  d=q[axis]-p[axis]
  if abs(d)<1e-6:
   if not lo[axis]<=p[axis]<=hi[axis]:return False
  else:
   a,b=(lo[axis]-p[axis])/d,(hi[axis]-p[axis])/d
   if a>b:a,b=b,a
   t0=max(t0,a);t1=min(t1,b)
   if t0>t1:return False
 return True
def run():
 levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert levels.load_level('/Game/Maps/WNY_PrototypeRegion')
 world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert unreal.RVWorldContentLibrary.set_region_authoring_loaded(world,True)
 actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);loaded=actors.get_all_level_actors();labels={a.get_actor_label():a for a in loaded}
 roads=[]
 for a in loaded:
  if isinstance(a,unreal.RVRegionRoad):
   route=a.get_editor_property('route')
   for i in range(route.get_number_of_spline_points()-1):
    p=route.get_location_at_spline_point(i,unreal.SplineCoordinateSpace.WORLD);q=route.get_location_at_spline_point(i+1,unreal.SplineCoordinateSpace.WORLD)
    roads.append(([p.x,p.y],[q.x,q.y],a.get_editor_property('width_cm')/2+500))
 # Broad highway section, sharing the existing main carriageway and a gently merged parallel lane.
 asphalt=unreal.load_asset('/Game/World/WNY/Materials/M_Asphalt');white=unreal.load_asset('/Game/World/WNY/Materials/M_CreamTrim')
 for index,x in enumerate(range(90000,170000,10000)):
  name='WNY divided highway north '+str(index);a=labels.get(name) or actors.spawn_actor_from_class(unreal.RVRegionRoad,unreal.Vector(x,0 if x==90000 else 1800,12))
  a.set_actor_label(name);a.tags=['WNYHighwayMilestone','RoadExclusion'];a.set_editor_property('asphalt',asphalt);a.set_editor_property('center_paint',white);a.set_editor_property('width_cm',1100)
  spline=a.get_editor_property('route');spline.clear_spline_points(False)
  for j in range(6):
   sx=x+j*2000;sy=1800*min(1,max(0,(sx-90000)/10000))
   spline.add_spline_point(unreal.Vector(sx-x,sy-(0 if x==90000 else 1800),0),unreal.SplineCoordinateSpace.LOCAL,False)
  spline.update_spline();a.rebuild_road()
  roads.append(([x,0 if x==90000 else 1800],[x+10000,1800],1050))
 removed=[]
 for a in loaded:
  if not isinstance(a,unreal.RVBiomePatch):continue
  if not any(a.actor_has_tag(tag) for tag in ['WNYRoadsideDressing','WNYVergeMilestone']):continue
  c=a.get_actor_location();b=a.get_editor_property('bounds').get_unscaled_box_extent()
  if any(intersects_segment(p,q,[c.x-b.x-margin,c.y-b.y-margin],[c.x+b.x+margin,c.y+b.y+margin]) for p,q,margin in roads):
   removed.append(a.get_actor_label());assert actors.destroy_actor(a)
 # Rural-loop tree groups leave authored approaches and the clear aisle of each road untouched.
 graph=unreal.load_asset('/Game/World/WNY/PCG/PCG_Deciduous');rng=random.Random(197712);added=0
 for index,x in enumerate(range(-50000,105001,15000)):
  for side in [-1,1]:
   y=45000+side*12000;px=x+rng.uniform(-1000,1000);bx,by=5000,2500
   if any(intersects_segment(p,q,[px-bx-margin,y-by-margin],[px+bx+margin,y+by+margin]) for p,q,margin in roads):continue
   name='WNY rural-loop grove %02d %d'%(index,side);a=labels.get(name) or actors.spawn_actor_from_class(unreal.RVBiomePatch,unreal.Vector(px,y,0));a.set_actor_label(name);a.tags=['WNYClearGroves']
   a.get_editor_property('bounds').set_box_extent(unreal.Vector(bx,by,20000));c=a.get_editor_property('dressing');c.set_graph(graph);c.set_editor_property('seed',5300+index*31+side);added+=1
 assert unreal.EditorLoadingAndSavingUtils.save_map(world,'/Game/Maps/WNY_PrototypeRegion');assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
 assert unreal.RVWorldContentLibrary.set_region_authoring_loaded(world,False)
 (out/'dressing-clearance.json').write_text(json.dumps({'saved':True,'removed_overlapping_authored_bounds':removed,'rural_groves':added,'highway_parallel_carriageway_m':800,'generation':'next saved-state session','actual_route_validation':'pending'},indent=2))
def tick(dt):
 global phase,handle
 if phase==0 and time.time()-started>5:
  phase=10
  try:run()
  except Exception:
   (out/'dressing-clearance-error.txt').write_text(traceback.format_exc())
   for k in ['last_traceback','last_value','last_type','last_exc']:
    if hasattr(sys,k):setattr(sys,k,None)
  gc.collect();phase=1
 elif phase==1:
  phase=2;unreal.unregister_slate_post_tick_callback(handle);handle=None;gc.collect();unreal.SystemLibrary.quit_editor()
handle=unreal.register_slate_post_tick_callback(tick)
