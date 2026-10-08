import unreal,time,json,gc,traceback
from pathlib import Path
out=Path('D:/GitHub/RVSurvival/RVSurvival/Docs/Gate9Results');levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert levels.load_level('/Game/Maps/Gate9CombatInfectedTest');assert levels.save_current_level()
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
 if isinstance(a,unreal.StaticMeshActor) and a.get_actor_label()=='Gate3_10km_TestGround':
  a.modify();a.static_mesh_component.modify();a.static_mesh_component.set_mobility(unreal.ComponentMobility.STATIC);a.static_mesh_component.set_collision_profile_name('BlockAll')
a=None
info={'navigation_system':str(unreal.NavigationSystemV1.get_navigation_system(world)),'config':str(world.get_world_settings().get_editor_property('NavigationSystemConfig')),'console_api':str(getattr(unreal.EditorLevelLibrary,'editor_console_command',None))}
try:info['build_deferred_until_load_unlocked']=True
except Exception:info['error']=traceback.format_exc()
start=time.time();requested=False;request_time=0
def tick(dt):
 global world,requested,request_time
 if not requested:
  if time.time()-start<3 or unreal.NavigationSystemV1.is_navigation_being_built_or_locked(world):return
  requested=unreal.RVCombatContentLibrary.build_navigation_editor(world);request_time=time.time();return
 if time.time()-request_time<8 or unreal.NavigationSystemV1.is_navigation_being_built(world):return
 try:
  info['diagnostics']=dict(unreal.RVCombatContentLibrary.inspect_navigation(world))
  info['built']=not unreal.NavigationSystemV1.is_navigation_being_built(world)
  info['nav_actors']=[a.get_name() for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors() if isinstance(a,unreal.RecastNavMesh)]
  path=unreal.NavigationSystemV1.find_path_to_location_synchronously(world,unreal.Vector(0,-2500,0),unreal.Vector(900,-2500,0))
  info['path_valid']=bool(path and path.is_valid());info['path_points']=len(path.path_points) if path else 0
  info['floor_actors']=[{'label':a.get_actor_label(),'position':str(a.get_actor_location()),'scale':str(a.get_actor_scale3d()),'mesh':str(a.static_mesh_component.get_editor_property('StaticMesh'))} for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors() if isinstance(a,unreal.StaticMeshActor) and ('Floor' in a.get_actor_label() or 'Ground' in a.get_actor_label())]
  info['saved']=levels.save_current_level();path=None
 except Exception:info['result_error']=traceback.format_exc()
 (out/'navigation-build.json').write_text(json.dumps(info,indent=2));unreal.unregister_slate_post_tick_callback(handle);world=None;gc.collect();unreal.SystemLibrary.quit_editor()
handle=unreal.register_slate_post_tick_callback(tick)
