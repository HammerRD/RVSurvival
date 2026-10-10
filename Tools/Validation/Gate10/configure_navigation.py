import unreal,time,gc,traceback,json
from pathlib import Path
out=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate10Validation');started=time.time();phase=0;handle=None

def configure():
 levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert levels.load_level('/Game/Maps/WNY_PrototypeRegion')
 world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert unreal.RVWorldContentLibrary.set_region_authoring_loaded(world,True)
 navs=[a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors() if isinstance(a,unreal.RecastNavMesh)];assert navs
 for nav in navs:
  nav.modify();nav.set_editor_property('bIsWorldPartitioned',True);nav.set_editor_property('RuntimeGeneration',unreal.RuntimeGenerationType.STATIC);nav.set_editor_property('AgentRadius',42);nav.set_editor_property('AgentHeight',192)
 assert levels.save_current_level();assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
 (out/'navigation-configuration.json').write_text(json.dumps({'saved':True,'mode':'native static partitioned navmesh; build via WorldPartitionNavigationDataBuilder','agent_radius_cm':42,'agent_height_cm':192,'build_and_runtime_projection':'pending'},indent=2))
 assert unreal.RVWorldContentLibrary.set_region_authoring_loaded(world,False)

def tick(delta):
 global phase,handle
 if phase==0 and time.time()-started>5:
  phase=1
  try:configure()
  except Exception:(out/'navigation-configuration-error.txt').write_text(traceback.format_exc())
  gc.collect()
 elif phase==1 and time.time()-started>20:
  unreal.unregister_slate_post_tick_callback(handle);handle=None;phase=2;gc.collect();unreal.SystemLibrary.quit_editor()
handle=unreal.register_slate_post_tick_callback(tick)
