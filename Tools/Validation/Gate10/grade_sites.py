"""Bounded native grading and saved geometry alignment; only the new WNY map."""
import unreal,time,json,math,traceback,gc,sys
from pathlib import Path
out=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate10Validation');started=time.time();phase=0;handle=None
sites=[(-130000,4900,2500,2900,0),(-60000,-5500,3000,4100,0),(0,46000,2800,3500,None),(75000,46000,2800,3500,None),(140000,5000,2500,3900,0)]
def terrain(x,y):return (1800*math.sin(x/65000)*math.cos(y/72000)+650*math.sin(y/25000))*max(0,min(1,(abs(y)-3000)/12000))
def graded(x,y):
 h=terrain(x,y)
 for cx,cy,hx,hy,value in sites:
  height=terrain(cx,45000) if value is None else value;outside=max(abs(x-cx)-hx,abs(y-cy)-hy);alpha=max(0,min(1,1-max(0,outside)/1400));alpha=alpha*alpha*(3-2*alpha);h=h*(1-alpha)+height*alpha
 return h

def apply():
 assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level('/Game/Maps/WNY_PrototypeRegion')
 world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert unreal.RVWorldContentLibrary.set_region_authoring_loaded(world,True)
 actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);loaded=actors.get_all_level_actors();land=next(a for a in loaded if isinstance(a,unreal.Landscape))
 assert not land.actor_has_tag('WNYGeometryGradedV1'),'already aligned; inspect saved state'
 receipt={'native':dict(unreal.RVWorldContentLibrary.grade_region_site_pads(world)),'moved':[],'road_points':0}
 assert receipt['native'].get('GradedSites')==5,receipt
 groups=[(['PINE CREEK FUEL','Sign PINE CREEK','Pine Creek','Fuel canopy','Inactive pump'],-130000,6500),(['ERIE ROAD SERVICE','Sign ERIE','Erie Service'],-60000,-8500),(['HAWTHORNE FARM','Sign HAWTHORNE','Hawthorne','Farm dining'],0,47000),(['MAPLE RUN CAMPGROUND','Sign MAPLE','Maple Run','Camp picnic','Camp fire'],75000,47000),(['ROWLAND CROSSROADS','Sign ROWLAND','Rowland'],140000,8000)]
 for a in loaded:
  label=a.get_actor_label();q=a.get_actor_location()
  for prefixes,x,y in groups:
   if any(label.startswith(prefix) for prefix in prefixes):
    # Parking was authored at its own ground height, unlike each building's shell.
    delta=graded(q.x,q.y)-terrain(q.x,q.y) if label.endswith('RV parking') else graded(x,y)-terrain(x,y)
    a.modify();a.set_actor_location(q+unreal.Vector(0,0,delta),False,False);receipt['moved'].append(label);break
  else:
   if label.startswith(('Abandoned trail vehicle','Abandoned vehicle body collision','Trail vehicle cargo')):
    # These are separate actors, consistently shifted with their vehicle site's ground.
    number=int(label.rsplit(' ',1)[1]);positions=[(-129000,3400),(-61600,-11000),(73500,49200),(35000,-150),(35350,100)];x,y=positions[number];delta=graded(x,y)-terrain(x,y)
    if abs(delta)>0.01:a.modify();a.set_actor_location(q+unreal.Vector(0,0,delta),False,False);receipt['moved'].append(label)
  if isinstance(a,unreal.RVRegionEncounterZone):
   a.modify();a.set_actor_location(unreal.Vector(q.x,q.y,graded(q.x,q.y)),False,False)
  if isinstance(a,unreal.RVRegionRoad):
   a.modify();spline=a.get_editor_property('Route');spline.modify()
   for i in range(spline.get_number_of_spline_points()):
    v=spline.get_location_at_spline_point(i,unreal.SplineCoordinateSpace.WORLD);spline.set_location_at_spline_point(i,unreal.Vector(v.x,v.y,graded(v.x,v.y)+12),unreal.SplineCoordinateSpace.WORLD,False);receipt['road_points']+=1
   spline.update_spline();a.rebuild_road()
 land.modify();tags=list(land.tags);tags.append('WNYGeometryGradedV1');land.tags=tags
 assert unreal.EditorLoadingAndSavingUtils.save_map(world,'/Game/Maps/WNY_PrototypeRegion');assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
 assert unreal.RVWorldContentLibrary.set_region_authoring_loaded(world,False);receipt['saved']=True;receipt['manual_validation']='pending';(out/'site-grading.json').write_text(json.dumps(receipt,indent=2))
def tick(dt):
 global phase,handle
 if phase==0 and time.time()-started>5:
  phase=10
  try:apply()
  except Exception:(out/'site-grading-error.txt').write_text(traceback.format_exc())
  for key in ['last_traceback','last_value','last_type','last_exc']:
   if hasattr(sys,key):setattr(sys,key,None)
  gc.collect();phase=1
 elif phase==1:
  phase=2;unreal.unregister_slate_post_tick_callback(handle);handle=None;gc.collect();unreal.SystemLibrary.quit_editor()
handle=unreal.register_slate_post_tick_callback(tick)
