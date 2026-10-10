"""Read saved native terrain without modifying or replaying gameplay."""
import unreal,time,json,gc,sys,traceback
from pathlib import Path
out=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate10Validation');start=time.time();phase=0;handle=None
def audit():
 levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert levels.load_level('/Game/Maps/WNY_PrototypeRegion')
 w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert unreal.RVWorldContentLibrary.set_region_authoring_loaded(w,True)
 try:(out/'saved-terrain-audit.json').write_text(json.dumps(dict(unreal.RVWorldContentLibrary.audit_region_terrain(w)),indent=2))
 finally:assert unreal.RVWorldContentLibrary.set_region_authoring_loaded(w,False)
def tick(dt):
 global phase,handle
 if phase==0 and time.time()-start>5:
  phase=10
  try:audit()
  except Exception:(out/'saved-terrain-audit-error.txt').write_text(traceback.format_exc())
  for k in ['last_traceback','last_value','last_type','last_exc']:
   if hasattr(sys,k):setattr(sys,k,None)
  gc.collect();phase=1
 elif phase==1:
  unreal.unregister_slate_post_tick_callback(handle);handle=None;phase=2;unreal.SystemLibrary.quit_editor()
handle=unreal.register_slate_post_tick_callback(tick)
