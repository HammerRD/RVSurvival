"""Open the actual saved map; prepare an approach, then await real window V input.
No direct seat RPCs. Holds E through the engine input system for entry only.
PIE remains open for visual inspection; Stop PIE before releasing this runner.
"""
import unreal, time, json
from pathlib import Path
from collections import deque
B=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate6LayoutRework')
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level('/Game/Maps/Gate6FuelElectricalTest')
assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
s=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.LevelEditorPlaySettings'))
s.set_editor_property('PlayNumberOfClients',1);s.set_editor_property('RunUnderOneProcess',True);s.set_editor_property('AdditionalLaunchParameters','')
n=s.get_editor_property('NetworkEmulationSettings');n.set_editor_property('bIsNetworkEmulationEnabled',False);s.set_editor_property('NetworkEmulationSettings',n)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
start=time.time();phase=0;ready_time=0;nextsample=0;samples=deque(maxlen=6000)
def tick(dt):
 global phase,ready_time,nextsample
 if time.time()-start<6:return
 try:
  w=next(a for a in unreal.ObjectIterator(unreal.World) if a.get_name()=='Gate6FuelElectricalTest' and 'UEDPIE_' in a.get_path_name())
  pc=unreal.GameplayStatics.get_player_controller(w,0)
  v=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSystemsMotorhome)[0]
  p=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSurvivorCharacter)[0]
  if phase==0:
   e=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVVehicleEntryPoint) if a.get_editor_property('Seat').get_editor_property('bDriverSeat') and abs(v.get_actor_transform().inverse_transform_location(a.get_actor_location()).y)>100)
   loc=e.get_actor_location()-v.get_actor_right_vector()*125;loc.z=v.get_actor_location().z+100
   p.set_actor_location(loc,False,True);pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(loc+unreal.Vector(0,0,64),e.get_actor_location()))
   ready_time=time.time()+1;phase=1
  if phase==1 and time.time()>ready_time:
   unreal.SystemLibrary.execute_console_command(pc,'Input.+key E',pc);ready_time=time.time()+.85;phase=2
  if phase==2 and time.time()>ready_time:
   unreal.SystemLibrary.execute_console_command(pc,'Input.-key E',pc);phase=3
  if time.time()>nextsample:
   nextsample=time.time()+.1;q=v.get_actor_transform().inverse_transform_location(p.get_actor_location());m=p.get_component_by_class(unreal.CharacterMovementComponent)
   samples.append({'t':time.time()-start,'local':[q.x,q.y,q.z],'mode':str(m.get_editor_property('MovementMode')),'capsule':str(p.get_component_by_class(unreal.CapsuleComponent).get_collision_enabled()),'pawn':pc.get_controlled_pawn().get_name() if pc.get_controlled_pawn() else None,'parent':str(p.get_attach_parent_actor())})
   meshes=[{'name':a.get_name(),'mesh':a.get_editor_property('StaticMesh').get_name(),'visible':a.is_visible(),'hidden':a.get_editor_property('bHiddenInGame')} for a in v.get_components_by_class(unreal.StaticMeshComponent) if a.get_editor_property('StaticMesh') and 'Door_Back' in a.get_editor_property('StaticMesh').get_name()]
   with open(B/'manual-baseline.json','w') as snapshot:
    json.dump({'samples':list(samples),'original_door_parts':meshes},snapshot,indent=2)
 except (StopIteration,IndexError):return
 except Exception as e:
  unreal.log_error("MANUAL_PROBE "+repr(e));unreal.unregister_slate_post_tick_callback(h)
h=unreal.register_slate_post_tick_callback(tick)

