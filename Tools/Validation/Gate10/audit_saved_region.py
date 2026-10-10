"""Audit saved region and enable native streaming after editor startup completes."""
import unreal,json,time,gc,traceback
from pathlib import Path
out=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate10Validation')
started=time.time();phase=0;handle=None

def audit():
 levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
 assert levels.load_level('/Game/Maps/WNY_PrototypeRegion')
 world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
 assert unreal.RVWorldContentLibrary.configure_region_streaming(world)
 actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
 record={'region':dict(unreal.RVWorldContentLibrary.inspect_region(world)),
 'actors':[{'label':a.get_actor_label(),'class':a.get_class().get_name(),'position':[a.get_actor_location().x,a.get_actor_location().y,a.get_actor_location().z]} for a in actors],
 'stats':dict(unreal.RVWorldContentLibrary.get_dressing_stats(world))}
 assert levels.save_current_level()
 assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
 (out/'saved-region-audit.json').write_text(json.dumps(record,indent=2))

def tick(delta):
 global phase,handle
 if phase==0 and time.time()-started>5:
  phase=1
  try:audit()
  except Exception:(out/'saved-region-audit-error.txt').write_text(traceback.format_exc())
  gc.collect()
 elif phase==1 and time.time()-started>20:
  unreal.unregister_slate_post_tick_callback(handle);handle=None;phase=2
  gc.collect();unreal.SystemLibrary.quit_editor()
handle=unreal.register_slate_post_tick_callback(tick)
