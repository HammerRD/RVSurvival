"""Development-only manual view/input aid. No seat/rest/door RPC shortcuts.
Every tick reacquires the current player; only primitives survive between ticks.
Commands perform mouse-look setup or native key holds and export visible PIE shots.
"""
import unreal,json,time
from pathlib import Path
B=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate6LayoutRework')
last=0;held=None;nexttick=0
def tick(dt):
 global last,held,nexttick
 if time.time()<nexttick:return
 nexttick=time.time()+.05
 try:
  w=next(a for a in unreal.ObjectIterator(unreal.World) if a.get_name()=='Gate6FuelElectricalTest' and 'UEDPIE_' in a.get_path_name())
  pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn()
  if not p:return
  v=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSystemsMotorhome)[0]
  if held and time.time()>held[1]:unreal.RVInteriorMotorhome.dispatch_development_key(pc,held[0],False);held=None
  try:r=json.load(open(B/'manual-command.json'))
  except (OSError,ValueError):r={}
  if r.get('id',0)>last:
   last=r['id'];op=r.get('op')
   if op=='look':pc.set_control_rotation(unreal.Rotator(pitch=r.get('pitch',0),yaw=v.get_actor_rotation().yaw+r['yaw']))
   elif op=='aim':
    kind=r['kind'];name=r['name']
    classes={'station':unreal.RVInteriorStation,'container':unreal.RVStoragePoint,'rest':unreal.RVRestPoint,'seat':unreal.RVVehicleEntryPoint,'door':unreal.RVInteractiveDoor,'ladder':unreal.RVLadder}
    actors=unreal.GameplayStatics.get_all_actors_of_class(w,classes[kind])
    def matches(a):
     if kind=='station':return str(a.get_editor_property('StationName'))==name
     if kind=='container':return str(a.get_editor_property('Container').get_editor_property('DisplayName'))==name
     if kind=='rest':return str(a.get_editor_property('DisplayName'))==name
     if kind=='seat':return a.get_editor_property('Seat').get_name()==name and abs(v.get_actor_transform().inverse_transform_location(a.get_actor_location()).y)<100
     return True
    target=next(a for a in actors if matches(a))
    point=target.get_editor_property('DoorCollision').get_world_location() if kind=='door' else target.get_actor_location()
    pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p.get_actor_location()+unreal.Vector(0,0,p.get_editor_property('BaseEyeHeight')),point))
   elif op=='hold':
    if held:unreal.RVInteriorMotorhome.dispatch_development_key(pc,held[0],False)
    unreal.RVInteriorMotorhome.dispatch_development_key(pc,r['key'],True);held=(r['key'],time.time()+r['seconds'])
   elif op=='photo':unreal.SystemLibrary.execute_console_command(pc,'shot filename='+str(B/r['name']).replace('\\','/')+' -nosuffix'+(' showui' if r.get('ui') else ''),pc)
  q=v.get_actor_transform().inverse_transform_location(p.get_actor_location())
  row={'time':time.time(),'local':[q.x,q.y,q.z],'look':str(pc.get_control_rotation()),'pawn':p.get_name()}
  if isinstance(p,unreal.RVSurvivorCharacter):
   row['prompt']=str(p.get_component_by_class(unreal.RVInteractionComponent).get_prompt())
   row['movement']=str(p.get_component_by_class(unreal.CharacterMovementComponent).get_editor_property('MovementMode'))
   row['capsule']=str(p.get_component_by_class(unreal.CapsuleComponent).get_collision_enabled())
   row['rest']=str(pc.player_state.get_component_by_class(unreal.RVNeedsComponent).get_editor_property('State').rest_mode)
   row['pose']=str(p.get_component_by_class(unreal.RVRestPoseComponent).get_editor_property('RestPoint'))
   inventory=p.get_component_by_class(unreal.RVInventoryComponent)
   row['inventory_feedback']=inventory.get_editor_property('Feedback')
   opened=inventory.get_editor_property('OpenContainer')
   row['container']=str(opened.get_editor_property('DisplayName')) if opened else None
  json.dump(row,open(B/'manual-current.json','w'),indent=2)
 except (StopIteration,IndexError):return
 except Exception as e:unreal.log_error('MANUAL_CONTROL '+repr(e));unreal.unregister_slate_post_tick_callback(h)
h=unreal.register_slate_post_tick_callback(tick)
