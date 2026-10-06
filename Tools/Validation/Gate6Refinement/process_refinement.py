import unreal,json,time,os
B='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate6Refinement/'
session=json.load(open(B+'session.json'));config=session['config'];start=session['start']
w=next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='Gate6FuelElectricalTest' and unreal.GameplayStatics.get_player_controller(w,0) and unreal.GameplayStatics.get_player_controller(w,0).get_controlled_pawn())
authority=unreal.GameplayStatics.get_game_mode(w) is not None;own=unreal.GameplayStatics.get_player_controller(w,0);p=own.get_controlled_pawn();other=next(c for c in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSurvivorCharacter) if c!=p)
hp=p if authority else other;cp=other if authority else p
v=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSystemsMotorhome)[0];door=v.get_editor_property('HouseDoor')
driver=next(s for s in v.get_seats() if s.get_editor_property('bDriverSeat'));passenger=next(s for s in v.get_seats() if not s.get_editor_property('bDriverSeat'))
isdriver=(authority==(config['driver']=='host'));dp=hp if config['driver']=='host' else cp;wp=cp if config['driver']=='host' else hp
entries=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVVehicleEntryPoint)
de=next(a for a in entries if a.get_editor_property('Seat')==driver and abs(v.get_actor_transform().inverse_transform_location(a.get_actor_location()).y)>100)
pe=next(a for a in entries if a.get_editor_property('Seat')==passenger and abs(v.get_actor_transform().inverse_transform_location(a.get_actor_location()).y)>100)
insidepass=next(a for a in entries if a.get_editor_property('Seat')==passenger and abs(v.get_actor_transform().inverse_transform_location(a.get_actor_location()).y)<100)
insidedriver=next(a for a in entries if a.get_editor_property('Seat')==driver and abs(v.get_actor_transform().inverse_transform_location(a.get_actor_location()).y)<100)
bed=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVRestPoint) if str(a.get_editor_property('DisplayName'))=='Rear bed')
stations=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVInteriorStation);power=next(a for a in stations if str(a.get_editor_property('StationName'))=='Power')
needs=p.get_editor_property('PlayerState').get_component_by_class(unreal.RVNeedsComponent);pose=p.get_component_by_class(unreal.RVRestPoseComponent)
results=[];samples=[];events=[];idx=0;nextsample=0;active=True;target=None
def at(s,fn):events.append((s,fn))
def check(n,ok,d=''):results.append({'case':n,'pass':bool(ok),'detail':str(d)});unreal.log('REFINE_NET '+json.dumps(results[-1]))
def cmd(s):unreal.SystemLibrary.execute_console_command(own,s,own)
def key(k,on):
 if k=='E' and on and target:aim(target)
 cmd('Input.'+('+' if on else '-')+'key '+k)
def local(c):q=v.get_actor_transform().inverse_transform_location(c.get_actor_location());return [q.x,q.y,q.z]
def aim(a):
 point=a.get_editor_property('DoorCollision').get_world_location() if isinstance(a,unreal.RVInteractiveDoor) else a.get_actor_location()
 own.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p.get_actor_location()+unreal.Vector(0,0,p.get_editor_property('BaseEyeHeight')),point))
def focus(a):
 global target
 target=a;aim(a)
def place(c,q):
 if authority:c.set_actor_location(v.get_actor_transform().transform_location(unreal.Vector(*q)),False,True)
def occupied():return driver.get_editor_property('Occupant')==dp and passenger.get_editor_property('Occupant')==wp
def standing():
 q=local(wp);return passenger.get_editor_property('Occupant') is None and wp.get_editor_property('SeatedVehicle') is None and abs(q[1])<35 and 140<q[2]<240
def own_frame():return isdriver or p.get_component_by_class(unreal.RVPassengerReferenceFrameComponent).get_editor_property('ReferenceFrame')==v
def setup():
 cmd('t.MaxFPS 60');cmd('t.IdleWhenNotForeground 0')
 if authority:
  for c,a,sgn in [(dp,de,-1),(wp,pe,1)]:
   q=v.get_actor_transform().inverse_transform_location(a.get_actor_location());place(c,(q.x,q.y+sgn*125,100))
 check('house_door_starts_closed',door is not None and not door.get_editor_property('bOpen'))
at(0,setup);at(1,lambda:focus(de if isdriver else pe));at(1.3,lambda:key('E',True));at(2.2,lambda:key('E',False));at(3.5,lambda:check('both_seats_reserved',occupied()))
at(4,lambda:own.request_switch_seat('PassengerSeat' if isdriver else 'DriverSeat'));at(5.5,lambda:check('occupied_seat_rejected_before_release',occupied()))
at(6,lambda:own.request_living_area() if not isdriver else None);at(7.5,lambda:check('passenger_to_rear_no_exterior_exit',standing() and own_frame(),local(wp)))
at(8,lambda:focus(insidepass) if not isdriver else None);at(8.3,lambda:key('E',True) if not isdriver else None);at(9.2,lambda:key('E',False) if not isdriver else None);at(10.5,lambda:check('rear_back_to_passenger',occupied()))
at(11,lambda:key('W',True) if isdriver else None);at(16,lambda:own.request_living_area() if not isdriver else None)
at(18,lambda:check('moving_passenger_to_living_area',standing() and own_frame() and v.get_velocity().length()>150,{'pos':local(wp),'speed':v.get_velocity().length()}))
at(18.3,lambda:own.request_living_area() if isdriver else None);at(19.5,lambda:check('moving_driver_retains_control',driver.get_editor_property('Occupant')==dp and (not isdriver or own.get_controlled_pawn()==v)))
at(18.5,lambda:focus(door) if not isdriver else None);at(18.8,lambda:key('E',True) if not isdriver else None);at(19.7,lambda:key('E',False) if not isdriver else None)
at(19.9,lambda:check('moving_door_open_replicates',door.get_editor_property('bOpen')))
def walking(rear):
 if not isdriver:own.set_control_rotation(unreal.Rotator(yaw=v.get_actor_rotation().yaw+(180 if rear else 0)));key('W',True)
at(20,lambda:walking(True));at(21.7,lambda:key('W',False) if not isdriver else None);at(22.5,lambda:check('moving_walk_to_rear',local(wp)[0]<-150 and standing() and own_frame(),local(wp)))
at(23,lambda:walking(False));at(24.7,lambda:key('W',False) if not isdriver else None);at(25.5,lambda:check('moving_walk_back_to_front',local(wp)[0]>60 and standing() and own_frame(),local(wp)))
at(25.6,lambda:focus(door) if not isdriver else None);at(25.8,lambda:key('E',True) if not isdriver else None);at(26.7,lambda:key('E',False) if not isdriver else None)
at(27.5,lambda:check('moving_door_close_replicates',not door.get_editor_property('bOpen')))
at(28,lambda:focus(insidepass) if not isdriver else None);at(28.3,lambda:key('E',True) if not isdriver else None);at(29.2,lambda:key('E',False) if not isdriver else None)
at(30,lambda:check('moving_rear_to_available_passenger',occupied() and v.get_velocity().length()>150,v.get_velocity().length()))
at(30.3,lambda:own.request_living_area() if not isdriver else None);at(31.5,lambda:check('moving_passenger_rear_repeat',standing() and own_frame(),local(wp)))
at(32,lambda:(key('W',False),key('SpaceBar',True)) if isdriver else None);at(51,lambda:key('SpaceBar',False) if isdriver else None)
at(33,lambda:check('parked_after_drive',v.get_velocity().length()<50,v.get_velocity().length()))
at(34,lambda:place(wp,(-180,0,195)));at(35,lambda:focus(bed) if not isdriver else None);at(35.3,lambda:key('E',True) if not isdriver else None);at(36.2,lambda:key('E',False) if not isdriver else None)
at(37.5,lambda:check('bed_pose_and_occupancy_replicate',bed.get_editor_property('Occupant')==wp.get_editor_property('PlayerState') and wp.get_component_by_class(unreal.RVRestPoseComponent).get_editor_property('RestPoint')==bed,local(wp)))
at(38,lambda:key('Z',True) if not isdriver else None);at(38.3,lambda:key('Z',False) if not isdriver else None)
at(39.5,lambda:check('sleep_state_replicates',wp.get_editor_property('PlayerState').get_component_by_class(unreal.RVNeedsComponent).get_editor_property('State').rest_mode==unreal.RVRestMode.SLEEPING))
at(40,lambda:key('R',True) if not isdriver else None);at(40.3,lambda:key('R',False) if not isdriver else None);at(41.5,lambda:check('stand_up_replicates_safe_aisle',bed.get_editor_property('Occupant') is None and standing() and own_frame(),local(wp)))
at(42,lambda:walking(False));at(43,lambda:key('W',False) if not isdriver else None);at(44,lambda:check('bed_walk_away',local(wp)[0]>-40 and standing() and own_frame(),local(wp)))
# Door changes are made by the standing passenger, observed by both processes.
at(45,lambda:place(wp,(92.4,275,100)));at(46,lambda:focus(door) if not isdriver else None);at(46.3,lambda:key('E',True) if not isdriver else None);at(47.2,lambda:key('E',False) if not isdriver else None);at(48.5,lambda:check('door_open_replicates',door.get_editor_property('bOpen')))
at(49,lambda:focus(door) if not isdriver else None);at(49.3,lambda:key('E',True) if not isdriver else None);at(50.2,lambda:key('E',False) if not isdriver else None);at(51.5,lambda:check('door_close_replicates',not door.get_editor_property('bOpen')))
def finish():
 global active
 active=False;unreal.unregister_slate_post_tick_callback(h)
 json.dump({'pid':os.getpid(),'authority':authority,'config':config,'results':results,'samples':samples},open(B+config['name']+('_server.json' if authority else '_client.json'),'w'),indent=2)
at(53,finish)
events=[(s+20 if s>=33 and s!=51 else s,fn) for s,fn in events]
if config.get('transition_only',False):
 events=[(s,fn) for s,fn in events if fn!=finish]
 transition_start=len(events)
 at(64,lambda:own.request_living_area() if isdriver else None)
 at(65.5,lambda:check('parked_driver_to_rear_replicates',driver.get_editor_property('Occupant') is None and dp.get_editor_property('SeatedVehicle') is None and abs(local(dp)[1])<5 and 45<local(dp)[0]<215,local(dp)))
 at(66,lambda:place(wp,(-95,0,195)))
 at(67,lambda:focus(insidedriver) if not isdriver else None);at(67.3,lambda:key('E',True) if not isdriver else None);at(68.2,lambda:key('E',False) if not isdriver else None)
 at(69.5,lambda:check('rear_to_available_driver_network',driver.get_editor_property('Occupant')==wp and (own.get_controlled_pawn()==v if not isdriver else own.get_controlled_pawn()==p),{'wp':str(wp),'occupant':str(driver.get_editor_property('Occupant')),'pawn':str(own.get_controlled_pawn()),'actors':[str(a) for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSurvivorCharacter)]}))
 at(70,lambda:own.request_living_area() if not isdriver else None)
 at(71.5,lambda:check('new_driver_to_rear_and_safe_fallback',driver.get_editor_property('Occupant') is None and wp.get_editor_property('SeatedVehicle') is None and abs(local(wp)[1])<5 and 45<local(wp)[0]<215,local(wp)))
 at(72,lambda:focus(insidedriver) if isdriver else None);at(72.3,lambda:key('E',True) if isdriver else None);at(73.2,lambda:key('E',False) if isdriver else None)
 at(74.5,lambda:check('original_driver_restored_from_interior',driver.get_editor_property('Occupant')==dp))
 at(75,lambda:focus(insidepass) if not isdriver else None);at(75.3,lambda:key('E',True) if not isdriver else None);at(76.2,lambda:key('E',False) if not isdriver else None)
 at(77.5,lambda:check('both_seats_restored_after_interior_exchange',occupied()))
 at(79,finish)
 events=events[:transition_start]+[(s+25,fn) for s,fn in events[transition_start:]]
if config.get('disconnect',False):
 events=[(s,fn) for s,fn in events if fn!=finish]
 at(65,lambda:own.request_living_area() if not authority and isdriver else None)
 at(67,lambda:place(cp,(-180,0,195)))
 at(68,lambda:focus(bed) if not authority else None);at(68.3,lambda:key('E',True) if not authority else None);at(69.2,lambda:key('E',False) if not authority else None)
 at(70.5,lambda:check('client_bed_reserved_before_disconnect',bed.get_editor_property('Occupant')==cp.get_editor_property('PlayerState')))
 at(71,lambda:key('Z',True) if not authority else None);at(71.3,lambda:key('Z',False) if not authority else None)
 at(72.5,lambda:check('client_sleep_before_disconnect',cp.get_editor_property('PlayerState').get_component_by_class(unreal.RVNeedsComponent).get_editor_property('State').rest_mode==unreal.RVRestMode.SLEEPING))
 def disconnect_client():
  if authority:return
  finish();controller=own;execute=unreal.SystemLibrary.execute_console_command
  from runner_runtime import release_runners
  release_runners();execute(controller,'disconnect',controller)
 at(74,disconnect_client)
 def cleaned():
  if not authority:return
  check('disconnect_frees_bed_and_survivor',bed.get_editor_property('Occupant') is None and len(unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSurvivorCharacter))==1)
  check('disconnect_keeps_RV_other_needs_and_seats',len(unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSystemsMotorhome))==1 and own.get_editor_property('PlayerState').get_component_by_class(unreal.RVNeedsComponent).get_editor_property('State').rest_mode==unreal.RVRestMode.AWAKE and (driver.get_editor_property('Occupant')==hp if config['driver']=='host' else driver.get_editor_property('Occupant') is None))
 at(80,cleaned);at(82,finish)
events.sort(key=lambda entry:entry[0])
def tick(dt):
 global idx,nextsample,hp,cp,dp,wp
 if not active:return
 if not authority:
  # Remote pawns can be recreated after normal net relevancy changes; never retain the destroyed wrapper.
  remote=next((a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSurvivorCharacter) if a!=p),None)
  if remote:
   hp=remote;cp=p;dp=hp if config['driver']=='host' else cp;wp=cp if config['driver']=='host' else hp
 t=time.time()-start
 if t<0:return
 try:
  while idx<len(events) and t>=events[idx][0]:
   fn=events[idx][1];idx+=1;terminating=fn.__name__=='disconnect_client' and not authority;fn()
   if terminating:return # Runner namespace was released before disconnect; use the captured local guard.
   if not active:return
  if not active:return
  if t>=nextsample:
   nextsample=t+.2;samples.append({'t':t,'passenger':local(wp),'driver_occupant':str(driver.get_editor_property('Occupant')),'passenger_occupant':str(passenger.get_editor_property('Occupant')),'door':door.get_editor_property('bOpen'),'speed':v.get_velocity().length()})
 except Exception as e:check('exception',False,repr(e));finish()
h=unreal.register_slate_post_tick_callback(tick)


