"""Read saved native terrain without modifying or replaying gameplay."""
import unreal,time,json,gc,sys,traceback,importlib
sys.path.insert(0,'D:/GitHub/RVSurvival/RVSurvival/Tools/Validation/Gate10');import terrain_audit_common;importlib.reload(terrain_audit_common)
from pathlib import Path
out=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate10Validation');docs=Path('D:/GitHub/RVSurvival/RVSurvival/Docs/Gate10Results');start=time.time();phase=0;handle=None;loaded_at=0
def audit():
 w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
 (out/'saved-terrain-audit.json').write_text(json.dumps(dict(unreal.RVWorldContentLibrary.audit_region_terrain(w)),indent=2))
 summary,rows=terrain_audit_common.collect(w);w=None
 failures=terrain_audit_common.passes(summary,rows);summary['pass']=not failures;summary['failures']=len(failures);summary['first_failures']=failures[:20]
 (out/'saved-terrain-full-samples.json').write_text(json.dumps(rows,indent=1))
 docs.joinpath('saved-terrain-full-audit.json').write_text(json.dumps(summary,indent=2))
def tick(dt):
 global phase,handle,loaded_at
 if phase==0 and time.time()-start>5:
  phase=10
  try:
   assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level('/Game/Maps/WNY_PrototypeRegion')
   assert unreal.RVWorldContentLibrary.set_region_authoring_loaded(unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world(),True);loaded_at=time.time();phase=3
  except Exception:(out/'saved-terrain-audit-error.txt').write_text(traceback.format_exc());phase=4
 elif phase==3 and time.time()-loaded_at>10:
  # A few frames after loading, so registered proxies have collision before sampling.
  phase=10
  try:audit()
  except Exception:(out/'saved-terrain-audit-error.txt').write_text(traceback.format_exc())
  phase=4
 elif phase==4:
  phase=10
  try:assert unreal.RVWorldContentLibrary.set_region_authoring_loaded(unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world(),False)
  except Exception:(out/'saved-terrain-audit-release-error.txt').write_text(traceback.format_exc())
  for k in ['last_traceback','last_value','last_type','last_exc']:
   if hasattr(sys,k):setattr(sys,k,None)
  gc.collect();phase=1
 elif phase==1:
  unreal.unregister_slate_post_tick_callback(handle);handle=None;phase=2;unreal.SystemLibrary.quit_editor()
handle=unreal.register_slate_post_tick_callback(tick)
