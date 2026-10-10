"""Resume saved PCG patches with all authored cells loaded through native editor adapters."""
import unreal,json,time,gc,traceback
from pathlib import Path
out=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate10Validation');started=time.time();phase=0;handle=None

def prepare():
 levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert levels.load_level('/Game/Maps/WNY_PrototypeRegion')
 world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
 assert unreal.RVWorldContentLibrary.set_region_authoring_loaded(world,True)
 before=dict(unreal.RVWorldContentLibrary.inspect_region(world))
 (out/'pcg-before-full-load.json').write_text(json.dumps(before,indent=2))
 actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
 count=0
 for a in actors:
  if isinstance(a,unreal.RVBiomePatch):a.get_editor_property('dressing').generate(True);count+=1
 (out/'pcg-request.json').write_text(json.dumps({'parents':count,'full_authoring_bounds_loaded':True}))

def save():
 levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
 world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
 record={'stats':dict(unreal.RVWorldContentLibrary.get_dressing_stats(world)),'components':dict(unreal.RVWorldContentLibrary.inspect_region(world))}
 assert unreal.EditorLoadingAndSavingUtils.save_map(world,'/Game/Maps/WNY_PrototypeRegion')
 assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
 (out/'pcg-full-load.json').write_text(json.dumps(record,indent=2))
 assert unreal.RVWorldContentLibrary.set_region_authoring_loaded(world,False)

def tick(delta):
 global phase,handle
 try:
  if phase==0 and time.time()-started>5:
   phase=10;prepare();phase=1
  elif phase==1 and time.time()-started>35:
   world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
   pending=dict(unreal.RVWorldContentLibrary.get_dressing_stats(world))['Pending'];world=None
   if pending==0:phase=10;save();phase=2
   elif time.time()-started>240:raise RuntimeError('PCG timeout')
  elif phase==2:
   unreal.unregister_slate_post_tick_callback(handle);handle=None;phase=3;gc.collect();unreal.SystemLibrary.quit_editor()
 except Exception:
  (out/'pcg-full-load-error.txt').write_text(traceback.format_exc());phase=2
handle=unreal.register_slate_post_tick_callback(tick)
