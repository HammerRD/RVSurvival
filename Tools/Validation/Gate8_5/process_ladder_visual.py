"""Held-key diagnostics, NOT manual acceptance. Initial fixture only; subsequent
routes walk through native input/CMC. Never call seat/rest/door completion RPCs.
Scoped cleanup releases all world wrappers before Stop PIE.
"""
import unreal,json,time,os,math
from pathlib import Path
B=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate8_5Validation')
session=json.loads((B/'session.json').read_text());config=session['config'];start=session['start']
w=next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='Gate8_5CharacterTest' and unreal.GameplayStatics.get_player_controller(w,0) and unreal.GameplayStatics.get_player_controller(w,0).get_controlled_pawn())
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
def aim_eye(point):
 origin=p.get_actor_eyes_view_point()[0]
 if p.get_editor_property('bUseControllerRotationYaw'):
  profile=p.get_component_by_class(unreal.RVCharacterPresentationComponent).get_editor_property('Profile');offset=profile.get_editor_property('OwnerCameraOffset');position=p.get_actor_location();angle=math.atan2(point.y-position.y,point.x-position.x)
  origin=position+unreal.Vector(math.cos(angle)*offset.x-math.sin(angle)*offset.y,math.sin(angle)*offset.x+math.cos(angle)*offset.y,p.get_editor_property('BaseEyeHeight')+offset.z)
 return origin

def aim(a,role='walker'):
 global route
 if not own(role):return
 if route:key('W',False);route=None
 point=a.get_actor_location()
 if a==door:point=door.get_editor_property('DoorCollision').get_world_location()
 if a==ladder and local(p)[2]>320:point=ladder.get_editor_property('RoofInteraction').get_world_location()
 pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(aim_eye(point),point))
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
camera=None
hud_hidden=False
visual_rows=[]
def inspect_remote(name,c,kind='seat'):
 global camera,hud_hidden
 if c==p:return
 component=c.get_component_by_class(unreal.RVCharacterPresentationComponent)
 skeletal=c.get_editor_property('Mesh');anim=skeletal.get_anim_instance()
 check('remote_skeletal_'+name,component.has_configured_visuals() and isinstance(anim,unreal.RVHumanoidAnimInstance),component.get_editor_property('VisualState'))
 target=skeletal.get_socket_location('pelvis')+unreal.Vector(0,0,10);q=v.get_actor_transform().inverse_transform_location(target)
 if kind=='bed':delta=unreal.Vector(100,-q.y,100)
 elif kind=='ladder':delta=unreal.Vector(-200,100,30)
 else:delta=unreal.Vector(65 if name=='dinette_rear' else -65,-65 if q.y>0 else 65,35)
 location=target+v.get_actor_transform().transform_location(delta)-v.get_actor_location()
 rotation=unreal.MathLibrary.find_look_at_rotation(location,target)
 if camera is None:camera=unreal.RVCharacterContentLibrary.spawn_observation_camera(v,location,rotation)
 else:camera.set_actor_location_and_rotation(location,rotation,False,True)
 camera.get_component_by_class(unreal.CameraComponent).set_field_of_view(120);cmd('showhud');hud_hidden=True;pc.set_view_target_with_blend(camera,0)
 visual_rows.append({'name':name,'remote':True,'pose_index':anim.get_editor_property('PoseIndex'),'local_position':local(c),'foot_bones':{bone:str(v.get_actor_transform().inverse_transform_location(skeletal.get_socket_location(bone))) for bone in ['foot_l','foot_r']},'camera':str(location)})
def capture(name):cmd('shot showui filename='+str(B/(config['name']+('_server_' if authority else '_client_')+name+'.png')).replace('\\','/')+' -nosuffix')
def restore_view():
 global hud_hidden
 pc.set_view_target_with_blend(pc.get_controlled_pawn(),0)
 if hud_hidden:cmd('showhud');hud_hidden=False

visual_rows=[]
def setup_ladder():
 cmd('t.MaxFPS 60')
 if authority:
  wp.set_actor_location(v.get_actor_transform().transform_location(unreal.Vector(-520,75,95)),False,True)
  dp.set_actor_location(v.get_actor_transform().transform_location(unreal.Vector(650,-300,95)),False,True)
at(0,setup_ladder);interact(1,ladder)
at(3,lambda:check('normal_E_ladder',ladder.get_editor_property('Occupant')==wp))
hold(3.2,'W',2.4)
at(4.5,lambda:inspect_remote('ladder',wp,'ladder'));at(4.7,lambda:capture('ladder') if isdriver else None);at(4.9,restore_view)
hold(6.5,'S',2.5);tap(9.5,'E')
at(11,lambda:check('normal_down_and_ground_return',walking(wp) and not frame(wp) and ladder.get_editor_property('Occupant') is None))
def finish():
 global active
 active=False
 for name in list(held):key(name,False)
 unreal.unregister_slate_post_tick_callback(h)
 (B/(config['name']+('_server.json' if authority else '_client.json'))).write_text(json.dumps({'pid':os.getpid(),'results':results,'visuals':visual_rows},indent=2))
at(12,finish);events.sort(key=lambda e:e[0])
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
