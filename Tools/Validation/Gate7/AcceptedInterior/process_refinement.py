"""Held-key diagnostics, NOT manual acceptance. Initial fixture only; subsequent
routes walk through native input/CMC. Never call seat/rest/door completion RPCs.
Scoped cleanup releases all world wrappers before Stop PIE.
"""
import unreal,json,time,os,math
from pathlib import Path
B=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate7AcceptedInterior')
session=json.loads((B/'session.json').read_text());config=session['config'];start=session['start']
w=next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='Gate7MechanicalTest' and unreal.GameplayStatics.get_player_controller(w,0) and unreal.GameplayStatics.get_player_controller(w,0).get_controlled_pawn())
authority=unreal.GameplayStatics.get_game_mode(w) is not None
pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn()
other=next(c for c in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSurvivorCharacter) if c!=p)
hp=p if authority else other;cp=other if authority else p
isdriver=authority==(config['driver']=='host');dp=hp if config['driver']=='host' else cp;wp=cp if config['driver']=='host' else hp
v=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSystemsMotorhome)[0]
door=v.get_editor_property('HouseDoor');seats=v.get_seats()
driver=next(s for s in seats if s.get_editor_property('bDriverSeat'))
passenger=next(s for s in seats if not s.get_editor_property('bDriverSeat') and not s.get_editor_property('bInteriorOnly'))
front=next(s for s in seats if s.get_name()=='DinetteFrontSeat');rear=next(s for s in seats if s.get_name()=='DinetteRearSeat')
entries=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVVehicleEntryPoint)
def entry(s):return next(a for a in entries if a.get_editor_property('Seat')==s and abs(v.get_actor_transform().inverse_transform_location(a.get_actor_location()).y)<100)
de=entry(driver);pe=entry(passenger);fe=entry(front);re=entry(rear)
bed=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVRestPoint) if str(a.get_editor_property('DisplayName'))=='Rear bed')
ladder=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVLadder)[0]
results=[];samples=[];events=[];idx=0;nextsample=0;route=None;held=set();active=True;braking=False
def at(s,fn):events.append((s,fn))
def check(name,ok,detail=''):
 row={'case':name,'pass':bool(ok),'detail':str(detail)};results.append(row);unreal.log('PHYSICAL_NET '+json.dumps(row))
def cmd(text):unreal.SystemLibrary.execute_console_command(pc,text,pc)
def key(name,on):
 unreal.RVInteriorMotorhome.dispatch_development_key(pc,name,on)
 if on:held.add(name)
 else:held.discard(name)
def own(role):return role=='both' or (role=='driver')==isdriver
def tap(t,name,role='walker'):
 at(t,lambda:key(name,True) if own(role) else None);at(t+.15,lambda:key(name,False) if own(role) else None)
def hold(t,name,duration,role='walker'):
 at(t,lambda:key(name,True) if own(role) else None);at(t+duration,lambda:key(name,False) if own(role) else None)
def local(c):q=v.get_actor_transform().inverse_transform_location(c.get_actor_location());return [q.x,q.y,q.z]
def walk(target,role='walker',timeout=5):
 global route
 if own(role):route={'target':target,'until':time.time()+timeout};key('W',True)
def aim(a,role='walker'):
 global route
 if not own(role):return
 if route:key('W',False);route=None
 point=a.get_actor_location()
 if a==door:point=door.get_editor_property('DoorCollision').get_world_location()
 if a==ladder and local(p)[2]>320:point=ladder.get_editor_property('RoofInteraction').get_world_location()
 pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p.get_actor_location()+unreal.Vector(0,0,p.get_editor_property('BaseEyeHeight')),point))
def interact(t,a,role='walker'):
 at(t,lambda:aim(a,role));hold(t+.2,'E',.8,role)
def walking(c):return c.get_editor_property('SeatedVehicle') is None and c.get_component_by_class(unreal.CharacterMovementComponent).get_editor_property('MovementMode')==unreal.MovementMode.MOVE_WALKING
def frame(c):return c.get_component_by_class(unreal.RVPassengerReferenceFrameComponent).get_editor_property('ReferenceFrame')==v
def seat_offset(c):return c.get_component_by_class(unreal.CapsuleComponent).get_editor_property('RelativeLocation').length()
def awake(c):
 state=c.get_editor_property('PlayerState')
 # Driver PlayerState belongs to the possessed vehicle; survivor is unpossessed.
 if state is None and driver.get_editor_property('Occupant')==c:state=v.get_editor_property('PlayerState')
 return state is not None and state.get_component_by_class(unreal.RVNeedsComponent).get_editor_property('State').rest_mode==unreal.RVRestMode.AWAKE
def safe_inside(c):q=local(c);return walking(c) and frame(c) and abs(q[1])<45 and 140<q[2]<240
def brake():
 global braking
 if isdriver:braking=True;key('S',True)
def setup():
 cmd('t.MaxFPS 60');cmd('t.IdleWhenNotForeground 0');cmd('rv.Passenger.Debug 1')
 if config.get('network'):
  for setting,value in [('PktLagMin',100),('PktLagMax',100),('PktLoss',2)]:cmd('NetEmulation.'+setting+' '+str(value))
 if authority:
  for c,y in [(dp,240),(wp,370)]:c.set_actor_location(v.get_actor_transform().transform_location(unreal.Vector(92.4,y,100)),False,True)
 check('saved_map_physical_entry_no_teleport_markers',v.get_editor_property('bPhysicalDoorEntry') and len(unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVInteriorAccessPoint))==0)
 check('only_rear_bed_is_rest_point',len(unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVRestPoint))==1)
at(0,setup)
interact(1,door,'driver');at(3,lambda:check('door_open_converges',door.get_editor_property('bOpen')))
at(3.1,lambda:walk((92.4,0),'driver'));at(6,lambda:check('driver_physical_step_door_entry',safe_inside(dp),local(dp)))
interact(6.2,de,'driver');at(8,lambda:check('physical_entry_then_E_driver',driver.get_editor_property('Occupant')==dp))
at(8.2,lambda:walk((92.4,0)));at(11.5,lambda:check('walker_physical_step_door_entry',safe_inside(wp),local(wp)))
interact(11.7,pe);at(13.5,lambda:check('physical_entry_then_E_passenger',passenger.get_editor_property('Occupant')==wp and seat_offset(wp)<1,seat_offset(wp)))
at(13.6,lambda:[c.get_component_by_class(unreal.RVPassengerReferenceFrameComponent).reset_diagnostics() for c in [dp,wp]])
tap(14,'One');at(15,lambda:check('occupied_driver_rejects_keeps_passenger',driver.get_editor_property('Occupant')==dp and passenger.get_editor_property('Occupant')==wp))
hold(15.2,'W',8,'driver');tap(17.5,'Three');at(19,lambda:check('moving_passenger_3_rear',safe_inside(wp) and v.get_velocity().length()>150,local(wp)))
tap(19.2,'Three','driver');at(20.5,lambda:check('moving_driver_3_rejected_before_release',driver.get_editor_property('Occupant')==dp and v.get_velocity().length()>150))
interact(20.6,fe);at(22.3,lambda:check('moving_dinette_front_seated_awake',front.get_editor_property('Occupant')==wp and awake(wp) and seat_offset(wp)<1,seat_offset(wp)))
tap(22.5,'E');at(23.6,lambda:check('dinette_front_stand_no_sleep',safe_inside(wp) and awake(wp)))
at(23.3,brake);at(31.3,lambda:key('SpaceBar',False) if isdriver else None);at(29,lambda:check('stopped_before_driver_departure',v.get_velocity().length()<10,v.get_velocity().length()))
at(24,lambda:walk((-40,0)));interact(26,re);at(28,lambda:check('dinette_rear_seated_awake',rear.get_editor_property('Occupant')==wp and awake(wp) and seat_offset(wp)<1,seat_offset(wp)))
tap(28.2,'E');at(29.3,lambda:check('dinette_rear_stand_no_sleep',safe_inside(wp) and awake(wp)))
at(29.5,lambda:walk((-115,0)));interact(31,bed);at(33,lambda:check('bed_pose_and_rest_replicate',bed.get_editor_property('Occupant')==wp.get_editor_property('PlayerState') and wp.get_component_by_class(unreal.RVRestPoseComponent).get_editor_property('RestPoint')==bed and not awake(wp)))
tap(33.2,'Z');at(34.3,lambda:check('bed_sleep_player_specific',wp.get_editor_property('PlayerState').get_component_by_class(unreal.RVNeedsComponent).get_editor_property('State').rest_mode==unreal.RVRestMode.SLEEPING and awake(dp)))
tap(34.5,'R');at(35.7,lambda:check('bed_wake_safe_aisle',safe_inside(wp) and awake(wp)))
tap(36,'Three','driver');at(37.3,lambda:check('stopped_driver_3_rear',safe_inside(dp) and driver.get_editor_property('Occupant') is None,local(dp)))
at(37.4,lambda:walk((155,-20),'driver'))
at(37.5,lambda:walk((85,0)));interact(39.5,pe);at(41.3,lambda:check('rear_back_to_passenger',passenger.get_editor_property('Occupant')==wp))
interact(41.5,de,'driver');at(43.3,lambda:check('rear_back_to_driver',driver.get_editor_property('Occupant')==dp))
tap(43.5,'Three');at(45,lambda:walk((92.4,0)));at(46.2,lambda:walk((92.4,240)));at(49,lambda:check('walker_physical_step_door_exit',walking(wp) and not frame(wp) and local(wp)[1]>200,local(wp)))
at(49.2,lambda:walk((-455,240)));at(52,lambda:walk((-455,75)));interact(54,ladder);at(56,lambda:check('ladder_reserved_replicates',ladder.get_editor_property('Occupant')==wp))
hold(56.2,'W',3.7);tap(60.4,'E');at(61.8,lambda:check('roof_dismount_supported_walking',walking(wp) and frame(wp) and ladder.get_editor_property('Occupant') is None and 405<local(wp)[2]<420,local(wp)))
hold(62,'W',1.5,'driver');at(64,lambda:check('roof_presence_locks_propulsion',v.get_velocity().length()<10,v.get_velocity().length()))
at(62.1,lambda:walk((110,75)));at(65,lambda:check('roof_walk_past_fixtures',walking(wp) and frame(wp) and local(wp)[0]>80 and local(wp)[2]>405,local(wp)))
at(65.2,lambda:walk((-315,75)));interact(68,ladder);at(70,lambda:check('roof_return_ladder_reserved',ladder.get_editor_property('Occupant')==wp))
hold(70.2,'S',3.7);tap(74.4,'E');at(75.8,lambda:check('roof_ladder_ground_return',walking(wp) and not frame(wp) and local(wp)[2]<110 and ladder.get_editor_property('Occupant') is None,local(wp)))
at(76,lambda:walk((-455,240)));at(78,lambda:walk((92.4,240)));interact(81,door);at(83,lambda:check('door_closed_converges_after_physical_exit',not door.get_editor_property('bOpen')))
at(83.1,lambda:walk((92.4,0),timeout=2));at(86,lambda:check('closed_door_physically_blocks_entry',local(wp)[1]>130 and local(wp)[2]<130,local(wp)))
at(86.1,lambda:walk((92.4,240)))
interact(86.2,door);at(88.1,lambda:walk((92.4,0)));at(91,lambda:check('physical_reentry_restores_frame',safe_inside(wp),local(wp)))
at(91.2,lambda:walk((-140,0)));at(93,lambda:check('physical_front_to_rear_walk',safe_inside(wp) and local(wp)[0]<-110,local(wp)))
at(93.2,lambda:walk((92.4,0)));at(95.5,lambda:walk((92.4,240)));at(98,lambda:check('repeat_physical_exit_no_locked_state',walking(wp) and not frame(wp) and awake(wp),local(wp)))
at(98.1,lambda:walk((200,240)))
tap(98.2,'Three','driver');at(100,lambda:walk((92.4,0),'driver'));at(101.5,lambda:walk((92.4,240),'driver'));at(104,lambda:check('driver_physical_exit_after_cab_release',walking(dp) and not frame(dp) and local(dp)[1]>200,local(dp)))
def finish():
 global active
 active=False
 for name in list(held):key(name,False)
 unreal.unregister_slate_post_tick_callback(h)
 (B/(config['name']+('_server.json' if authority else '_client.json'))).write_text(json.dumps({'pid':os.getpid(),'authority':authority,'config':config,'evidence_kind':'native-held-input diagnostics; manual hold routes pending','results':results,'samples':samples},indent=2))
 # Clear wrappers and event closures before the parent launcher stops PIE.
 for name in ['w','pc','p','other','hp','cp','dp','wp','v','door','seats','driver','passenger','front','rear','entries','de','pe','fe','re','bed','ladder']:globals()[name]=None
 events.clear()
at(106,finish)
# Brake to a real stop before parked-only bed/driver operations; do not fake speed.
# Reopen only after physically backing clear of the door's safety swing.
events=[(s+(20 if s>=29 else 0)+(3.2 if s>=86.2 else 0),fn) for s,fn in events]
if config.get('disconnect'):
 endpoint=(61.8 if config['disconnect']=='Roof' else 56)+20
 events=[(s,fn) for s,fn in events if s<=endpoint]
 def disconnect_client():
  if authority:return
  check('client_disconnect_requested_from_'+config['disconnect'].lower(),True)
  controller=pc;execute=unreal.SystemLibrary.execute_console_command
  finish()
  from runner_runtime import release_runners
  release_runners();execute(controller,'disconnect',controller)
 def cleanup_check():
  if not authority:return
  check('disconnect_releases_ladder_and_seats',len(unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSurvivorCharacter))==1 and ladder.get_editor_property('Occupant') is None and passenger.get_editor_property('Occupant') is None)
  check('remaining_player_needs_unchanged_awake',awake(dp))
 at(endpoint+.3,disconnect_client);at(endpoint+3,cleanup_check)
 hold(endpoint+3.2,'W',1.5,'driver')
 at(endpoint+5.2,lambda:check('disconnect_releases_roof_or_climb_drive_lock',v.get_velocity().length()>10,v.get_velocity().length()) if authority else None)
 at(endpoint+6,finish)
events.sort(key=lambda pair:pair[0])
def tick(dt):
 global idx,nextsample,route,braking,hp,cp,dp,wp
 if not active:return
 try:
  now=time.time();elapsed=now-start
  if not authority:
   remote=next((c for c in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSurvivorCharacter) if c!=p),None)
   if remote:hp=remote;cp=p;dp=p if isdriver else remote;wp=remote if isdriver else p
  while idx<len(events) and elapsed>=events[idx][0]:
   fn=events[idx][1];idx+=1
   terminating=fn.__name__=='finish' or (fn.__name__=='disconnect_client' and not authority)
   fn()
   if terminating:return # Managed module globals were released by disconnect.
  if not active:return
  if braking and v.get_velocity().length()<10:
   key('S',False);key('SpaceBar',True);braking=False
  if route:
   q=local(p);x,y=route['target'];distance=math.hypot(x-q[0],y-q[1])
   if distance<9 or now>route['until']:
    key('W',False);route=None
   else:pc.set_control_rotation(unreal.Rotator(yaw=v.get_actor_rotation().yaw+math.degrees(math.atan2(y-q[1],x-q[0]))))
  if now<nextsample:return
  nextsample=now+.1
  for label,c in [('driver',dp),('walker',wp)]:
   if not unreal.SystemLibrary.is_valid(c):continue
   movement=c.get_component_by_class(unreal.CharacterMovementComponent);capsule=c.get_component_by_class(unreal.CapsuleComponent);f=c.get_component_by_class(unreal.RVPassengerReferenceFrameComponent)
   samples.append({'t':round(elapsed,2),'who':label,'pos':local(c),'seat':str(c.get_editor_property('SeatedVehicle')),'seat_offset_cm':seat_offset(c) if c.get_editor_property('SeatedVehicle') else None,'cmc_active':movement.is_active(),'cmc_tick':movement.is_component_tick_enabled(),'mode':str(movement.get_editor_property('MovementMode')),'collision':str(capsule.get_collision_enabled()),'frame':str(f.get_editor_property('ReferenceFrame')),'corrections':f.get_editor_property('CorrectionCount'),'max_correction':f.get_editor_property('MaxCorrectionCm'),'speed':v.get_velocity().length()})
 except Exception as error:
  check('harness_exception',False,repr(error));finish()
h=unreal.register_slate_post_tick_callback(tick)
