"""Grade the five sites and garage extension through the Landscape edit layer; save only after an in-session audit passes."""
import unreal,time,json,gc,sys,traceback,importlib
sys.path.insert(0,'D:/GitHub/RVSurvival/RVSurvival/Tools/Validation/Gate10');import terrain_audit_common;importlib.reload(terrain_audit_common)
from pathlib import Path
out=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate10Validation');docs=Path('D:/GitHub/RVSurvival/RVSurvival/Docs/Gate10Results');started=time.time();phase=0;handle=None;graded_at=0;receipt={}
def world():return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
def grade():
 assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level('/Game/Maps/WNY_PrototypeRegion')
 assert unreal.RVWorldContentLibrary.set_region_authoring_loaded(world(),True)
 receipt['native']=dict(unreal.RVWorldContentLibrary.grade_region_site_pads(world()))
 assert receipt['native'].get('GradedSites')==6,receipt
 # Widened pads move their falloff ring outward; re-seat only the roads crossing it, at graded height + 12 cm as grade_sites.py did.
 reseat=['Rural loop 1-30','Rural loop 2-0','Rural loop 2-35','Rural loop 3-0'];receipt['reseated']={}
 for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
  if isinstance(a,unreal.RVRegionRoad) and a.get_actor_label() in reseat:
   a.modify();spline=a.get_editor_property('Route');spline.modify();points=[]
   for i in range(spline.get_number_of_spline_points()):
    v=spline.get_location_at_spline_point(i,unreal.SplineCoordinateSpace.WORLD);z=terrain_audit_common.intended(v.x,v.y)+12
    spline.set_location_at_spline_point(i,unreal.Vector(v.x,v.y,z),unreal.SplineCoordinateSpace.WORLD,False);points.append([round(v.x,1),round(v.y,1),round(v.z,3),round(z,3)])
   spline.update_spline();a.rebuild_road();receipt['reseated'][a.get_actor_label()]=points;spline=None
  a=None
 assert sorted(receipt['reseated'])==sorted(reseat),receipt['reseated'].keys()
def verify_and_save():
 summary,rows=terrain_audit_common.collect(world())
 failures=terrain_audit_common.passes(summary,rows);summary['pass']=not failures;summary['failures']=len(failures);summary['first_failures']=failures[:20]
 (out/'grading-v3-presave-samples.json').write_text(json.dumps(rows,indent=1));docs.joinpath('grading-v3-presave-audit.json').write_text(json.dumps(summary,indent=2))
 receipt['presave_pass']=not failures;receipt['presave_failures']=len(failures)
 if failures:receipt['saved']=False;return
 assert unreal.EditorLoadingAndSavingUtils.save_map(world(),'/Game/Maps/WNY_PrototypeRegion');assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
 receipt['saved']=True
def tick(dt):
 global phase,handle,graded_at
 if phase==0 and time.time()-started>5:
  phase=10
  try:grade();graded_at=time.time();phase=3
  except Exception:receipt['error']=traceback.format_exc();phase=4
 elif phase==3 and time.time()-graded_at>10:
  # Some frames after the merge, so collision and proxies are settled before sampling.
  phase=10
  try:verify_and_save()
  except Exception:receipt['error']=traceback.format_exc()
  phase=4
 elif phase==4:
  phase=10
  try:receipt['released']=unreal.RVWorldContentLibrary.set_region_authoring_loaded(world(),False)
  except Exception:receipt['release_error']=traceback.format_exc()
  (out/'grading-v3.json').write_text(json.dumps(receipt,indent=2))
  for k in ['last_traceback','last_value','last_type','last_exc']:
   if hasattr(sys,k):setattr(sys,k,None)
  gc.collect();phase=1
 elif phase==1:
  unreal.unregister_slate_post_tick_callback(handle);handle=None;phase=2;unreal.SystemLibrary.quit_editor()
handle=unreal.register_slate_post_tick_callback(tick)
