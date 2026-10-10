"""Extend only the garage pad/driveway; preserve all saved site identities."""
import unreal,time,json,gc,traceback,sys
from pathlib import Path
out=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate10Validation');start=time.time();phase=0;handle=None
def apply():
 levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert levels.load_level('/Game/Maps/WNY_PrototypeRegion')
 w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert unreal.RVWorldContentLibrary.set_region_authoring_loaded(w,True)
 assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
 result=dict(unreal.RVWorldContentLibrary.grade_region_site_pads(w,True));assert result.get('GradedSites')==1,result
 actors={a.get_actor_label():a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()}
 parking=actors['ERIE ROAD SERVICE RV parking'];p=parking.get_actor_location();parking.modify();parking.set_actor_location(unreal.Vector(p.x,p.y,10),False,False)
 road=actors['Garage approach'];road.modify();spline=road.get_editor_property('Route');spline.modify();spline.clear_spline_points(False)
 points=[(-60000,0),(-60000,-3500),(-62500,-6500),(-62500,-11000),(-60000,-11000)]
 for x,y in points:spline.add_spline_point(unreal.Vector(x,y,12),unreal.SplineCoordinateSpace.WORLD,False)
 spline.update_spline();road.rebuild_road()
 assert levels.save_current_level() and unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
 assert unreal.RVWorldContentLibrary.set_region_authoring_loaded(w,False)
 (out/'garage-approach-extension.json').write_text(json.dumps({'saved':True,'native':result,'driveway_points':points,'parking_position':[p.x,p.y,10],'falloff_m':90,'visual_driving_and_derived_data':'pending'},indent=2))
def tick(dt):
 global phase,handle
 if phase==0 and time.time()-start>5:
  phase=10
  try:apply()
  except Exception:(out/'garage-approach-extension-error.txt').write_text(traceback.format_exc())
  for k in ['last_traceback','last_value','last_type','last_exc']:
   if hasattr(sys,k):setattr(sys,k,None)
  gc.collect();phase=1
 elif phase==1:
  unreal.unregister_slate_post_tick_callback(handle);handle=None;phase=2;unreal.SystemLibrary.quit_editor()
handle=unreal.register_slate_post_tick_callback(tick)
