"""Preserve accepted pawn defaults; reparent only new region mode and safe starts."""
import unreal,time,json,gc,traceback,sys
from pathlib import Path
out=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate10Validation');started=time.time();phase=0;handle=None
def configure():
 assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level('/Game/Maps/WNY_PrototypeRegion')
 world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert unreal.RVWorldContentLibrary.set_region_authoring_loaded(world,True)
 actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);labels={a.get_actor_label():a for a in actors.get_all_level_actors()}
 vehicle=labels['WNY mobile survival base'];tags=list(vehicle.tags)
 if 'PlayerMobileBase' not in [str(t) for t in tags]:tags.append('PlayerMobileBase')
 vehicle.modify();vehicle.tags=tags
 r=vehicle.get_actor_location()
 for name,offset in [('WNY Player Start',unreal.Vector(0,750,-40)),('WNY Second Player Start',unreal.Vector(-220,750,-40))]:
  a=labels[name];a.modify();a.set_actor_location(r+offset,False,False);a.set_editor_property('bIsSpatiallyLoaded',False)
 bp=unreal.load_asset('/Game/World/WNY/Gameplay/BP_WNYGameMode');assert bp
 old_pawn=unreal.get_default_object(bp.generated_class()).get_editor_property('DefaultPawnClass');assert old_pawn
 parent=unreal.load_class(None,'/Script/RVSurvival.RVRegionGameMode');assert parent
 unreal.BlueprintEditorLibrary.reparent_blueprint(bp,parent);unreal.BlueprintEditorLibrary.compile_blueprint(bp)
 mode=unreal.get_default_object(bp.generated_class())
 mode.set_editor_property('DefaultPawnClass',old_pawn)
 mode.set_editor_property('GameStateClass',unreal.EditorAssetLibrary.load_blueprint_class('/Game/World/WNY/Gameplay/BP_WNYGameState'))
 assert mode.get_editor_property('DefaultPawnClass')==old_pawn
 assert unreal.EditorAssetLibrary.save_loaded_asset(bp)
 assert unreal.EditorLoadingAndSavingUtils.save_map(world,'/Game/Maps/WNY_PrototypeRegion');assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
 assert unreal.RVWorldContentLibrary.set_region_authoring_loaded(world,False)
 (out/'region-arrival-configuration.json').write_text(json.dumps({'saved':True,'parent':'ARVRegionGameMode','pawn':'accepted BP_Gate9_5Survivor','native_fallback':'two clear ground PlayerStarts','arrival':'single server-validated current mobile-base aisle placement and accepted native moving-base registration','runtime_join_and_moving_validation':'pending'},indent=2))
def tick(dt):
 global phase,handle
 if phase==0 and time.time()-started>5:
  phase=10
  try:configure()
  except Exception:
   (out/'region-arrival-error.txt').write_text(traceback.format_exc())
   for k in ['last_traceback','last_value','last_type','last_exc']:
    if hasattr(sys,k):setattr(sys,k,None)
  gc.collect();phase=1
 elif phase==1:
  phase=2;unreal.unregister_slate_post_tick_callback(handle);handle=None;gc.collect();unreal.SystemLibrary.quit_editor()
handle=unreal.register_slate_post_tick_callback(tick)



