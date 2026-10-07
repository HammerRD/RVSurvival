"""Reacquired control-path diagnostics and read-only manual observer; no completion RPCs."""
import unreal,json,time
from pathlib import Path
B=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate6PhysicalRefinement')
started=time.time();initialized=False;held=None;last=0;next_sample=0
def tick(dt):
 global initialized,held,last,next_sample
 if time.time()-started<6:return
 try:
  world=next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='Gate6FuelElectricalTest' and 'UEDPIE_' in w.get_path_name())
  pc=unreal.GameplayStatics.get_player_controller(world,0);pawn=pc.get_controlled_pawn()
  rv=unreal.GameplayStatics.get_all_actors_of_class(world,unreal.RVSystemsMotorhome)[0]
  if not initialized:
   pawn.set_actor_location(rv.get_actor_transform().transform_location(unreal.Vector(92.4,240,100)),False,True)
   pc.set_control_rotation(unreal.Rotator(yaw=rv.get_actor_rotation().yaw-90));initialized=True
  if held and time.time()>=held[1]:unreal.RVInteriorMotorhome.dispatch_development_key(pc,held[0],False);held=None
  try:command=json.loads((B/'command.json').read_text())
  except (OSError,ValueError):command={}
  if command.get('id',0)>last:
   last=command['id'];op=command.get('op')
   if op=='look':pc.set_control_rotation(unreal.Rotator(pitch=command.get('pitch',0),yaw=rv.get_actor_rotation().yaw+command['yaw']))
   elif op=='aim':
    kind=command['kind'];name=command.get('name','')
    cls={'door':unreal.RVInteractiveDoor,'seat':unreal.RVVehicleEntryPoint,'rest':unreal.RVRestPoint,'ladder':unreal.RVLadder}[kind]
    targets=unreal.GameplayStatics.get_all_actors_of_class(world,cls)
    if kind=='seat':targets=[a for a in targets if a.get_editor_property('Seat').get_name()==name and abs(rv.get_actor_transform().inverse_transform_location(a.get_actor_location()).y)<100]
    if kind=='rest':targets=[a for a in targets if str(a.get_editor_property('DisplayName'))==name]
    target=targets[0]
    point=target.get_actor_location()
    if kind=='door':point=target.get_editor_property('DoorCollision').get_world_location()
    if kind=='ladder' and rv.get_actor_transform().inverse_transform_location(pawn.get_actor_location()).z>320:point=target.get_editor_property('RoofInteraction').get_world_location()
    pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(pawn.get_actor_location()+unreal.Vector(0,0,pawn.get_editor_property('BaseEyeHeight')),point))
   elif op=='hold':
    if held:unreal.RVInteriorMotorhome.dispatch_development_key(pc,held[0],False)
    unreal.RVInteriorMotorhome.dispatch_development_key(pc,command['key'],True);held=(command['key'],time.time()+command['seconds'])
   elif op=='finish':
    if held:unreal.RVInteriorMotorhome.dispatch_development_key(pc,held[0],False);held=None
    unreal.unregister_slate_post_tick_callback(h)
    from runner_runtime import release_runners
    release_runners()
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
    return
  if time.time()<next_sample:return
  next_sample=time.time()+.05
  q=rv.get_actor_transform().inverse_transform_location(pawn.get_actor_location())
  row={'time':time.time(),'command':last,'local':[q.x,q.y,q.z],'pawn':pawn.get_name(),'speed':rv.get_velocity().length(),'look':str(pc.get_control_rotation()),'seat_feedback':pc.get_editor_property('SeatFeedback')}
  if isinstance(pawn,unreal.RVSurvivorCharacter):
   movement=pawn.get_component_by_class(unreal.CharacterMovementComponent);capsule=pawn.get_component_by_class(unreal.CapsuleComponent)
   frame=pawn.get_component_by_class(unreal.RVPassengerReferenceFrameComponent)
   row.update(mode=str(movement.get_editor_property('MovementMode')),radius=capsule.get_unscaled_capsule_radius(),half=capsule.get_unscaled_capsule_half_height(),collision=str(capsule.get_collision_enabled()),frame=str(frame.get_editor_property('ReferenceFrame')),prompt=str(pawn.get_component_by_class(unreal.RVInteractionComponent).get_prompt()),rest=str(pc.player_state.get_component_by_class(unreal.RVNeedsComponent).get_editor_property('State').rest_mode),ladder=str(pawn.get_component_by_class(unreal.RVLadderClimbComponent).get_editor_property('Ladder')))
  door=unreal.GameplayStatics.get_all_actors_of_class(world,unreal.RVInteractiveDoor)[0]
  row['door_open']=door.get_editor_property('bOpen')
  (B/'current.json').write_text(json.dumps(row,indent=2))
  with open(B/'samples.jsonl','a') as stream:stream.write(json.dumps(row)+'\n')
 except (StopIteration,IndexError):return
 except Exception as error:
  unreal.log_error('PHYSICAL_REFINEMENT '+repr(error));unreal.unregister_slate_post_tick_callback(h)
h=unreal.register_slate_post_tick_callback(tick)
