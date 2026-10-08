"""Focused native-input passenger locomotion and repeat V paths; controlled speed fixture."""
import unreal,json,time,os,math
from pathlib import Path
B=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate9Validation');session=json.loads((B/'session.json').read_text());config=session['config'];start=session['start']
w=next(a for a in unreal.ObjectIterator(unreal.World) if a.get_name()=='Gate9CombatInfectedTest' and unreal.GameplayStatics.get_player_controller(a,0) and unreal.GameplayStatics.get_player_controller(a,0).get_controlled_pawn())
authority=unreal.GameplayStatics.get_game_mode(w) is not None;pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn();other=next(c for c in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSurvivorCharacter) if c!=p)
isdriver=authority==(config['driver']=='host');dp=p if isdriver else other;wp=other if isdriver else p
v=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSystemsMotorhome)[0];seats=v.get_seats();driver=next(s for s in seats if s.get_editor_property('bDriverSeat'));passenger=next(s for s in seats if not s.get_editor_property('bDriverSeat') and not s.get_editor_property('bInteriorOnly'))
entries=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVVehicleEntryPoint)
def entry(s):return next(a for a in entries if a.get_editor_property('Seat')==s and abs(v.get_actor_transform().inverse_transform_location(a.get_actor_location()).y)>100)
de=entry(driver);pe=entry(passenger);results=[];samples=[];events=[];held=set();route=None;speed_target=None;phase='setup';camera=None;nextsample=0;active=True;anchors={};braking=False
def check(n,b,d=''):results.append({'case':n,'pass':bool(b),'detail':str(d)});unreal.log('CHARACTER_MOVING '+json.dumps(results[-1]))
def key(k,on):
 unreal.RVInteriorMotorhome.dispatch_development_key(pc,k,on)
 if on:held.add(k)
 else:held.discard(k)
def at(t,fn):events.append((t,fn))
def local(c):q=v.get_actor_transform().inverse_transform_location(c.get_actor_location());return [q.x,q.y,q.z]
def own(role):return isdriver==(role=='driver')
def tap(t,k,role='driver'):
 at(t,lambda:key(k,True) if own(role) else None);at(t+.15,lambda:key(k,False) if own(role) else None)
def hold(t,k,seconds,role='driver'):
 at(t,lambda:key(k,True) if own(role) else None);at(t+seconds,lambda:key(k,False) if own(role) else None)
def aim(a):pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p.get_actor_eyes_view_point()[0],a.get_actor_location()))
def walk(target):
 global route
 if not isdriver:route=target;key('W',True)
def stopwalk():
 global route
 if not isdriver:key('W',False);route=None
def speed(value):
 global speed_target,phase
 speed_target=value;phase=str(value)
def mark(name):anchors[name]=local(wp)
def stable(name):
 q=local(wp);f=wp.get_component_by_class(unreal.RVPassengerReferenceFrameComponent)
 check(name,f.get_editor_property('ReferenceFrame')==v and 145<q[2]<235 and abs(q[1])<65 and math.dist(q,anchors[name])<12,{'before':anchors[name],'after':q,'speed':v.get_velocity().length(),'corrections':f.get_editor_property('CorrectionCount'),'max_cm':f.get_editor_property('MaxCorrectionCm')})
def state(name):
 q=local(wp);f=wp.get_component_by_class(unreal.RVPassengerReferenceFrameComponent);anim=wp.get_editor_property('Mesh').get_anim_instance()
 reached=(q[0]>80 if name.endswith('front') else q[0]<-100 if name.endswith('rear') else q[1]>15 if name.endswith('sideways') else True)
 check(name,reached and f.get_editor_property('ReferenceFrame')==v and 145<q[2]<235 and abs(q[1])<65,{'position':q,'animation_speed':anim.get_editor_property('GroundSpeed'),'pose':anim.get_editor_property('PoseIndex'),'vehicle_speed':v.get_velocity().length()})
def observe(name):
 global camera
 if not isdriver:return
 target=wp.get_editor_property('Mesh').get_socket_location('pelvis')+unreal.Vector(0,0,10);q=v.get_actor_transform().inverse_transform_location(target)
 location=target+v.get_actor_transform().transform_location(unreal.Vector(175,0,15))-v.get_actor_location();rotation=unreal.MathLibrary.find_look_at_rotation(location,target)
 if camera is None:camera=unreal.RVCharacterContentLibrary.spawn_observation_camera(v,location,rotation)
 else:camera.set_actor_location_and_rotation(location,rotation,False,True)
 camera.get_component_by_class(unreal.CameraComponent).set_field_of_view(110);pc.set_view_target_with_blend(camera,0)
def shot(name):
 if isdriver:unreal.SystemLibrary.execute_console_command(pc,'shot showui filename='+str(B/(config['name']+('_server_' if authority else '_client_')+name+'.png')).replace('\\','/')+' -nosuffix',pc)
def resetview():
 if isdriver:pc.set_view_target_with_blend(pc.get_controlled_pawn(),0)
def capture(t,name):at(t,lambda:observe(name));at(t+.2,lambda:shot(name));at(t+.4,resetview)
def setup():
 unreal.SystemLibrary.execute_console_command(pc,'t.MaxFPS 60',pc)
 if authority:
  for name in ['DA_9mmHandgun','DA_9mmMagazine']:
   item=unreal.RVItemInstance();item.set_editor_property('Id',unreal.GuidLibrary.new_guid());item.set_editor_property('Definition',unreal.load_asset('/Game/Combat/Items/'+name));assert not wp.get_component_by_class(unreal.RVInventoryComponent).add_authority(item)
  for c,a in [(dp,de),(wp,pe)]:q=v.get_actor_transform().inverse_transform_location(a.get_actor_location());c.set_actor_location(v.get_actor_transform().transform_location(unreal.Vector(q.x,q.y+(-125 if q.y<0 else 125),100)),False,True)
 if config.get('network'):
  for k,val in [('PktLagMin',100),('PktLagMax',100),('PktLoss',2)]:unreal.SystemLibrary.execute_console_command(pc,'NetEmulation.'+k+' '+str(val),pc)
def stopvehicle():
 global speed_target,braking
 speed_target=None;braking=True
 if isdriver:key('SpaceBar',False);key('W',False);key('S',True)
def parked():
 if isdriver:key('S',False);key('SpaceBar',True)
 check('parked_after_braking',v.get_velocity().length()<15,v.get_velocity().length())
def check_seat(i,expected):
 seat=passenger if expected=='passenger' else driver
 check('native_V_'+str(i)+'_'+expected,seat.get_editor_property('Occupant')==dp and dp.get_editor_property('SeatedVehicle')==v and local(dp)[2]>120 and dp.get_component_by_class(unreal.CapsuleComponent).get_collision_enabled()==unreal.CollisionEnabled.NO_COLLISION,local(dp))
def finish():
 global active
 active=False
 for k in list(held):key(k,False)
 unreal.unregister_slate_post_tick_callback(handle)
 (B/(config['name']+('_server.json' if authority else '_client.json'))).write_text(json.dumps({'pid':os.getpid(),'config':config,'evidence_kind':'native control paths; server physics speed fixture for road/highway phases','results':results,'samples':samples},indent=2))
 events.clear()
at(0,setup);at(1,lambda:aim(de if isdriver else pe));hold(1.2,'E',.8,'driver');hold(1.2,'E',.8,'walker');at(3.5,lambda:check('normal_E_seats',driver.get_editor_property('Occupant')==dp and passenger.get_editor_property('Occupant')==wp));tap(4,'Three','walker');at(5.5,lambda:state('3_rear_walkable'));at(5.6,lambda:wp.get_component_by_class(unreal.RVPassengerReferenceFrameComponent).reset_diagnostics());hold(6,'W',38)
at(8,lambda:speed(500));at(9,lambda:mark('low_stand'));at(11,lambda:stable('low_stand'));capture(10,'low_standing')
at(12,lambda:walk((120,0)));at(15,lambda:state('low_front'));at(15.2,lambda:walk((-130,0)));at(18,lambda:state('low_rear'));at(18.1,stopwalk)
at(19,lambda:speed(1800));at(20,lambda:mark('road_stand'));at(22,lambda:stable('road_stand'));capture(21,'road_standing')
at(23,lambda:walk((100,0)));capture(24,'road_walking');at(26,lambda:state('road_front'));at(26.1,stopwalk);at(27,lambda:speed(2700));at(28,lambda:mark('highway_stand'));at(30,lambda:stable('highway_stand'));at(30.1,lambda:check('approximately_60mph',v.get_velocity().length()>2500,v.get_velocity().length()));capture(29,'highway_standing')
at(31,lambda:walk((-130,0)));capture(32,'highway_walking');at(34,lambda:state('highway_rear'));at(34.1,stopwalk);at(35,lambda:walk((-130,25)));at(36,lambda:state('highway_sideways'));at(36.1,stopwalk)
at(37,lambda:mark('gentle_turn'));hold(37.1,'A',.2);at(39,lambda:stable('gentle_turn'));at(39.5,lambda:speed(1800));at(40,lambda:mark('strong_turn'));hold(40.1,'D',.6);at(42,lambda:stable('strong_turn'));at(43,lambda:mark('braking'));at(44,stopvehicle);at(53,parked);at(54,lambda:state('braking_keeps_frame'));at(54.9,lambda:key('SpaceBar',False) if isdriver else None);hold(55,'W',2);at(58,lambda:(state('resume_keeps_frame'),check('resume_actually_driving',v.get_velocity().length()>150,v.get_velocity().length())));at(58.1,stopvehicle);at(67,parked)
for i in range(20):
 t=69+i*1.6;tap(t,'V');at(t+.6,lambda i=i:check_seat(i,'passenger'));tap(t+.8,'One');at(t+1.4,lambda i=i:check_seat(i,'driver'))
tap(6.2,'Four','walker');tap(6.5,'R','walker')
at(8.9,lambda:pc.set_control_rotation(unreal.Rotator(yaw=v.get_actor_rotation().yaw+90,pitch=30)) if not isdriver else None)
tap(9.2,'LeftMouseButton','walker');at(9.5,lambda:pc.set_control_rotation(unreal.Rotator(yaw=v.get_actor_rotation().yaw)) if not isdriver else None)
at(10.7,lambda:check('standing moving passenger reloads and fires authoritatively',wp.get_component_by_class(unreal.RVCombatComponent).shot_sequence==1 and wp.get_component_by_class(unreal.RVCombatComponent).get_loaded_rounds()==14))
at(102,finish);events.sort(key=lambda e:e[0])
def tick(dt):
 global nextsample,route,braking
 if not active:return
 try:
  now=time.time();elapsed=now-start
  while events and elapsed>=events[0][0]:_,fn=events.pop(0);fn()
  if not active:return
  if authority and speed_target is not None:
   v.get_editor_property('Mesh').set_physics_linear_velocity(v.get_actor_forward_vector()*speed_target,False)
  if braking and v.get_velocity().length()<40:
   if isdriver:key('S',False);key('SpaceBar',True)
   braking=False
  if route and not isdriver:
   q=local(p);x,y=route
   if math.hypot(x-q[0],y-q[1])<9:stopwalk()
   else:pc.set_control_rotation(unreal.Rotator(yaw=v.get_actor_rotation().yaw+math.degrees(math.atan2(y-q[1],x-q[0]))))
  if now>=nextsample:
   nextsample=now+.1;f=wp.get_component_by_class(unreal.RVPassengerReferenceFrameComponent);anim=wp.get_editor_property('Mesh').get_anim_instance()
   samples.append({'t':round(elapsed,2),'phase':phase,'passenger':local(wp),'speed':v.get_velocity().length(),'animation_speed':anim.get_editor_property('GroundSpeed'),'pose':anim.get_editor_property('PoseIndex'),'corrections':f.get_editor_property('CorrectionCount'),'max_cm':f.get_editor_property('MaxCorrectionCm')})
 except Exception as e:check('harness_exception',False,repr(e));events.clear();finish()
handle=unreal.register_slate_post_tick_callback(tick)




