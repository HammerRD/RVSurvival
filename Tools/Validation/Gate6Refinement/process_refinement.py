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
def aim(a):own.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p.get_actor_location()+unreal.Vector(0,0,p.get_editor_property('BaseEyeHeight')),a.get_actor_location()))
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
def walking(rear):
 if not isdriver:own.set_control_rotation(unreal.Rotator(yaw=v.get_actor_rotation().yaw+(180 if rear else 0)));key('W',True)
at(20,lambda:walking(True));at(21.7,lambda:key('W',False) if not isdriver else None);at(22.5,lambda:check('moving_walk_to_rear',local(wp)[0]<-150 and standing() and own_frame(),local(wp)))
at(23,lambda:walking(False));at(24.7,lambda:key('W',False) if not isdriver else None);at(25.5,lambda:check('moving_walk_back_to_front',local(wp)[0]>60 and standing() and own_frame(),local(wp)))
at(26,lambda:(key('W',False),key('S',True)) if isdriver else None);at(31,lambda:key('S',False) if isdriver else None)
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
def tick(dt):
 global idx,nextsample
 if not active:return
 t=time.time()-start
 if t<0:return
 try:
  while idx<len(events) and t>=events[idx][0]:events[idx][1]();idx+=1
  if not active:return
  if t>=nextsample:
   nextsample=t+.2;samples.append({'t':t,'passenger':local(wp),'driver_occupant':str(driver.get_editor_property('Occupant')),'passenger_occupant':str(passenger.get_editor_property('Occupant')),'door':door.get_editor_property('bOpen'),'speed':v.get_velocity().length()})
 except Exception as e:check('exception',False,repr(e));finish()
h=unreal.register_slate_post_tick_callback(tick)
