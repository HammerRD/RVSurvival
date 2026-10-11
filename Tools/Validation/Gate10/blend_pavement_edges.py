"""Blend graded terrain to road and parking-slab surfaces through the Landscape edit layer; save only after an in-session strict edge audit passes."""
import unreal,time,json,gc,sys,traceback,importlib
sys.path.insert(0,'D:/GitHub/RVSurvival/RVSurvival/Tools/Validation/Gate10');import terrain_audit_common;importlib.reload(terrain_audit_common)
from pathlib import Path
out=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate10Validation');docs=Path('D:/GitHub/RVSurvival/RVSurvival/Docs/Gate10Results');started=time.time();phase=0;handle=None;graded_at=0;receipt={}
def world():return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
def grade():
 assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level('/Game/Maps/WNY_PrototypeRegion')
 assert unreal.RVWorldContentLibrary.set_region_authoring_loaded(world(),True)
 # Rural loop 4-5 used to end 20 cm above the divided highway; bring it down to highway height before it reaches the highway edge.
 for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
  if isinstance(a,unreal.RVRegionRoad) and a.get_actor_label()=='Rural loop 4-5':
   spline=a.get_editor_property('Route');n=spline.get_number_of_spline_points()
   before=[[round(c,1) for c in (v.x,v.y,v.z)] for v in [spline.get_location_at_spline_point(i,unreal.SplineCoordinateSpace.WORLD) for i in range(n)]]
   assert n==6 and abs(before[5][2]-12)<0.5 and abs(before[4][1]-3273)<2,before
   a.modify();spline.modify()
   p4=spline.get_location_at_spline_point(4,unreal.SplineCoordinateSpace.WORLD);p5=spline.get_location_at_spline_point(5,unreal.SplineCoordinateSpace.WORLD);t=(p4.y-2600)/(p4.y-p5.y)
   spline.add_spline_point_at_index(unreal.Vector(p4.x+(p5.x-p4.x)*t,2600,12),5,unreal.SplineCoordinateSpace.WORLD,False)
   spline.update_spline();a.rebuild_road()
   receipt['rural_loop_4_5']={'before':before,'after':[[round(c,1) for c in (v.x,v.y,v.z)] for v in [spline.get_location_at_spline_point(i,unreal.SplineCoordinateSpace.WORLD) for i in range(spline.get_number_of_spline_points())]]}
   spline=None
  a=None
 assert 'rural_loop_4_5' in receipt
 receipt['native']=dict(unreal.RVWorldContentLibrary.blend_region_terrain_to_pavement(world()))
 assert receipt['native'].get('ParkingSlabs')==5 and receipt['native'].get('ChangedVertices',0)>0,receipt
def verify_and_save():
 summary,rows=terrain_audit_common.collect(world())
 failures=terrain_audit_common.passes(summary,rows);summary['pass']=not failures;summary['failures']=len(failures);summary['first_failures']=failures[:20]
 (out/'paved-edges-presave-edge-steps.json').write_text(json.dumps(summary.pop('_edge_rows'),indent=1))
 (out/'paved-edges-presave-samples.json').write_text(json.dumps(rows,indent=1));docs.joinpath('paved-edges-presave-audit.json').write_text(json.dumps(summary,indent=2))
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
  (out/'paved-edges.json').write_text(json.dumps(receipt,indent=2))
  for k in ['last_traceback','last_value','last_type','last_exc']:
   if hasattr(sys,k):setattr(sys,k,None)
  gc.collect();phase=1
 elif phase==1:
  unreal.unregister_slate_post_tick_callback(handle);handle=None;phase=2;unreal.SystemLibrary.quit_editor()
handle=unreal.register_slate_post_tick_callback(tick)
