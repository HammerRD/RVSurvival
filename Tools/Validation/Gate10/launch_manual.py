"""Save the new mobile base/start streaming policy, then open normal one-player PIE."""
import unreal,time,json,traceback,gc
from pathlib import Path
out=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate10Validation');started=time.time();phase=0;handle=None

def launch():
 levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert levels.load_level('/Game/Maps/WNY_PrototypeRegion')
 world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert unreal.RVWorldContentLibrary.set_region_authoring_loaded(world,True)
 changed=[]
 for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
  if a.get_actor_label() in ['WNY mobile survival base','WNY Player Start']:
   a.modify();a.set_editor_property('bIsSpatiallyLoaded',False);changed.append(a.get_actor_label())
 assert len(changed)==2,changed
 assert levels.save_current_level();assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
 assert unreal.RVWorldContentLibrary.set_region_authoring_loaded(world,False)
 settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.LevelEditorPlaySettings'));settings.set_editor_property('RunUnderOneProcess',True);settings.set_editor_property('PlayNumberOfClients',1);settings.set_editor_property('AdditionalLaunchParameters','')
 network=settings.get_editor_property('NetworkEmulationSettings');network.set_editor_property('bIsNetworkEmulationEnabled',False);settings.set_editor_property('NetworkEmulationSettings',network)
 unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings')).set_editor_property('bThrottleCPUWhenNotForeground',False)
 (out/'manual-launch.json').write_text(json.dumps({'saved':True,'always_loaded_mobile_base_and_start':changed,'manual_result':'pending'},indent=2))
 levels.editor_request_begin_play()

def tick(delta):
 global phase,handle
 if phase==0 and time.time()-started>5:
  phase=1
  try:launch()
  except Exception:(out/'manual-launch-error.txt').write_text(traceback.format_exc())
  unreal.unregister_slate_post_tick_callback(handle);handle=None;gc.collect()
handle=unreal.register_slate_post_tick_callback(tick)
