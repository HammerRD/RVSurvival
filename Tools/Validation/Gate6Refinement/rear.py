import unreal,json
B='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate6Refinement/'
w=next(w for w in unreal.ObjectIterator(unreal.World) if 'UEDPIE_' in w.get_path_name() and w.get_name()=='Gate6FuelElectricalTest')
pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn();v=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVInteriorMotorhome)[0]
f=p.get_component_by_class(unreal.RVPassengerReferenceFrameComponent);m=p.get_component_by_class(unreal.CharacterMovementComponent)
seats=v.get_seats();driver=next(s for s in seats if s.get_editor_property('bDriverSeat'));passenger=next(s for s in seats if not s.get_editor_property('bDriverSeat'))
points=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVVehicleInteriorSeatPoint)
dp=next(a for a in points if a.get_editor_property('Seat')==driver);pp=next(a for a in points if a.get_editor_property('Seat')==passenger)
t=0;idx=0;events=[];checks=[];start=None
def at(s,fn):events.append((s,fn))
def check(n,ok,d=''):r={'case':n,'pass':bool(ok),'detail':str(d)};checks.append(r);unreal.log('REFINE '+json.dumps(r))
def key(k,on):unreal.SystemLibrary.execute_console_command(pc,'Input.'+('+' if on else '-')+'key '+k,pc)
def aim(a):pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p.get_actor_location()+unreal.Vector(0,0,64),a.get_actor_location()))
def local():return v.get_actor_transform().inverse_transform_location(p.get_actor_location())
def clear():return pc.get_controlled_pawn()==p and pc.get_editor_property('SeatedVehicle') is None and f.get_editor_property('ReferenceFrame')==v and m.get_editor_property('MovementMode')==unreal.MovementMode.MOVE_WALKING
at(0,lambda:p.set_actor_location(v.get_actor_transform().transform_location(unreal.Vector(130,0,180)),False,True))
at(1,lambda:aim(dp));at(1.2,lambda:key('E',True));at(2,lambda:key('E',False));at(3,lambda:check('standing_to_driver',pc.get_controlled_pawn()==v))
at(3.5,lambda:pc.request_living_area());at(4.5,lambda:check('driver_to_validated_living_area',clear() and abs(local().y)<5 and 45<local().x<215,local()))
at(5,lambda:aim(pp));at(5.2,lambda:key('E',True));at(6,lambda:key('E',False));at(7,lambda:check('rear_to_passenger',passenger.get_editor_property('Occupant')==p and pc.get_controlled_pawn()==p))
at(7.5,lambda:key('Three',True));at(7.7,lambda:key('Three',False));at(8.5,lambda:check('native_3_passenger_to_living_area',clear(),local()))
def walk_start():
 global start
 start=local().x;pc.set_control_rotation(unreal.Rotator(yaw=v.get_actor_rotation().yaw+180));key('W',True)
at(9,walk_start);at(10,lambda:key('W',False));at(10.5,lambda:check('walking_restored_after_rear_transition',clear() and local().x<start-70,local()))
at(11,lambda:p.set_actor_location(v.get_actor_transform().transform_location(unreal.Vector(130,0,180)),False,True));at(12,lambda:aim(dp));at(12.2,lambda:key('E',True));at(13,lambda:key('E',False));at(14,lambda:check('living_area_reenter_driver',pc.get_controlled_pawn()==v))
at(14.5,lambda:pc.request_switch_seat('PassengerSeat'));at(15.5,lambda:check('seat_to_seat_preserved',passenger.get_editor_property('Occupant')==p and driver.get_editor_property('Occupant') is None))
at(16,lambda:pc.request_switch_seat('DriverSeat'));at(17,lambda:check('passenger_to_driver_preserved',driver.get_editor_property('Occupant')==p and pc.get_controlled_pawn()==v))
at(17.5,lambda:pc.request_living_area());at(18.5,lambda:check('repeated_safe_rear_release',clear() and all(s.get_editor_property('Occupant') is None for s in seats),local()))
def tick(dt):
 global t,idx
 t+=dt
 try:
  while idx<len(events) and t>=events[idx][0]:events[idx][1]();idx+=1
  if t>20:unreal.unregister_slate_post_tick_callback(h);json.dump({'results':checks},open(B+'rear.json','w'),indent=2)
 except Exception as e:
  check('exception',False,repr(e));unreal.unregister_slate_post_tick_callback(h);json.dump({'results':checks},open(B+'rear.json','w'),indent=2)
h=unreal.register_slate_post_tick_callback(tick)

