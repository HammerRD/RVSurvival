import unreal,json,math,time,os
B='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate3Validation/'
session=json.load(open(B+'process_session.json'));config=session['config'];role=config['driver']
VC=unreal.load_class(None,'/Script/RVSurvival.RVInteriorMotorhome');CC=unreal.load_class(None,'/Script/RVSurvival.RVSurvivorCharacter');FC=unreal.load_class(None,'/Script/RVSurvival.RVPassengerReferenceFrameComponent');EC=unreal.load_class(None,'/Script/RVSurvival.RVVehicleEntryPoint');SC=unreal.load_class(None,'/Script/RVSurvival.RVInteriorStation')
world=next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='Gate3MovingInteriorTest' and unreal.GameplayStatics.get_player_controller(w,0) and unreal.GameplayStatics.get_player_controller(w,0).get_controlled_pawn())
isServer=unreal.GameplayStatics.get_game_mode(world) is not None;own=unreal.GameplayStatics.get_player_controller(world,0);chars=unreal.GameplayStatics.get_all_actors_of_class(world,CC);ownpawn=own.get_controlled_pawn();other=next(a for a in chars if a!=ownpawn)
sw=cw=world;sv=cv=v=unreal.GameplayStatics.get_all_actors_of_class(world,VC)[0]
host=own if isServer else None;client=None if isServer else own;hp=ownpawn if isServer else other;cp=other if isServer else ownpawn;sp=cp;chp=hp
out=config['name']+('_server' if isServer else '_client')
driver=host if role=='host' else client;walker=client if role=='host' else host;wp=cp if role=='host' else hp;swp=wp;observer=wp;wv=v
ss=cs=st={str(a.get_editor_property('StationName')):a for a in unreal.GameplayStatics.get_all_actors_of_class(world,SC)}
rows=[];results=[];events=[];idx=0;elapsed=0;sample_acc=0;phase='setup';target=None;held=set();anchors={};counts={};station_initial={};active=True;yaws={};speed_target=None;drive_held=set();default_radius=wp.get_component_by_class(unreal.CapsuleComponent).get_unscaled_capsule_radius();default_speed=wp.get_component_by_class(unreal.CharacterMovementComponent).get_editor_property('MaxWalkSpeed')

def cmd(pc,s):
 if pc:unreal.SystemLibrary.execute_console_command(pc,s,pc)
def look(pc,r):
 if pc:pc.set_control_rotation(r)
def key(pc,k,on):cmd(pc,'Input.'+('+' if on else '-')+'key '+k)
def drive_key(k,on):
 if (k in drive_held)==on:return
 key(driver,k,on)
 if on:drive_held.add(k)
 else:drive_held.discard(k)
def set_speed(s):
 global speed_target
 speed_target=s
 for k in list(drive_held):drive_key(k,False)
def walk_key(k,on):
 if (k in held)==on:return
 key(walker,k,on)
 if on:held.add(k)
 else:held.discard(k)
def local(v,p):q=v.get_actor_transform().inverse_transform_location(p.get_actor_location());return [q.x,q.y,q.z]
def visual(v,c):
 q=v.get_actor_transform().inverse_transform_location(c.get_editor_property('mesh').get_world_location());return [q.x,q.y,q.z]
def check(n,ok,d=''):r={'case':n,'pass':bool(ok),'detail':str(d)};results.append(r);unreal.log('GATE3_SUITE '+json.dumps(r))
def at(t,f):events.append((t,f))
def stop_walk():
 global target
 target=None
 for k in list(held):walk_key(k,False)
def move(x):
 global target
 stop_walk();target=(0,x);look(walker,unreal.Rotator(yaw=wv.get_actor_rotation().yaw))
def move_y(y):
 global target
 stop_walk();target=(1,y);look(walker,unreal.Rotator(yaw=wv.get_actor_rotation().yaw-90))
def mark(p):
 global phase
 phase=p;anchors[p]=local(wv,wp);yaws[p]=sv.get_actor_rotation().yaw;wp.get_component_by_class(FC).reset_diagnostics()
def setup():
 # Only fixture placement is teleported, before any driving. All interior traversal uses accepted input.
 if isServer:swp.set_actor_location(sv.get_actor_transform().transform_location(unreal.Vector(122,300,110)),False,True);look(walker,unreal.Rotator(yaw=sv.get_actor_rotation().yaw-90))
 e=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(sw,EC) if a.get_editor_property('Seat').get_editor_property('bDriverSeat'));p=hp if role=='host' else sp
 pos=e.get_actor_location()-sv.get_actor_right_vector()*180;pos.z=92
 if isServer:p.set_actor_location(pos,False,True)
 look(driver,unreal.MathLibrary.find_look_at_rotation(pos+unreal.Vector(0,0,64),e.get_actor_location()))
def frame_ok():return wp.get_component_by_class(FC).get_editor_property('ReferenceFrame')==wv and swp.get_component_by_class(FC).get_editor_property('ReferenceFrame')==sv
def aim_station(n):
 stop_walk();a=st[n];look(walker,unreal.MathLibrary.find_look_at_rotation(wp.get_actor_location()+unreal.Vector(0,0,64),a.get_actor_location()));station_initial[n]=ss[n].get_editor_property('InteractionCount')
def observer_camera():
 if not driver:return
 v=driver.get_controlled_pawn()
 if not isinstance(v,unreal.WheeledVehiclePawn):return
 arm=v.get_component_by_class(unreal.SpringArmComponent)
 arm.set_editor_property('TargetArmLength',0);arm.set_editor_property('SocketOffset',unreal.Vector());arm.set_editor_property('bDoCollisionTest',False);arm.set_editor_property('bInheritPitch',True);arm.set_editor_property('bInheritRoll',True)
 arm.set_relative_location(unreal.Vector(160,0,235),False,False);arm.set_relative_rotation(unreal.Rotator(yaw=180,pitch=-8),False,False)
def station_check(n,prefix):
 a=ss[n].get_editor_property('InteractionCount');b=cs[n].get_editor_property('InteractionCount');check(prefix+'_'+n,a==station_initial[n]+1 and a==b and (not prefix.startswith(('moving','turning')) or sv.get_velocity().length()>1000) and frame_ok() and 165<local(wv,wp)[2]<210,{'before':station_initial[n],'server':a,'client':b,'passenger':local(wv,wp),'speed':sv.get_velocity().length()})
def snap():
 f=wp.get_component_by_class(FC);m=wp.get_component_by_class(unreal.CharacterMovementComponent);sl=local(sv,swp);cl=local(cv,cp if role=='host' else chp)
 rows.append({'t':round(elapsed,3),'phase':phase,'speed':sv.get_velocity().length(),'server':sl,'client':cl,'local':local(wv,wp),'frame':bool(f.get_editor_property('ReferenceFrame')),'mode':str(m.get_editor_property('movement_mode')),'corr':f.get_editor_property('CorrectionCount'),'maxcorr':f.get_editor_property('MaxCorrectionCm'),'step':f.get_editor_property('MaxLocalStepCm'),'base':str(f.get_editor_property('CurrentBase')),'base_changes':f.get_editor_property('BaseChanges'),'frame_changes':f.get_editor_property('FrameChanges'),'visual':visual(cv,chp) if role=='client' else visual(sv,sp),'observer_mesh_world':str((chp if role=='client' else sp).get_editor_property('mesh').get_world_location()),'yaw':sv.get_actor_rotation().yaw,'vehicle':list((sv.get_actor_location().x,sv.get_actor_location().y,sv.get_actor_location().z))})
for pc in [host,client]:cmd(pc,'t.MaxFPS 60');cmd(pc,'t.IdleWhenNotForeground 0');cmd(pc,'Slate.bAllowThrottling 0');cmd(pc,'rv.Passenger.Debug 1')
at(0,setup);at(.6,lambda:move_y(10));at(2.9,stop_walk);at(3,lambda:check('natural_entry',frame_ok() and abs(local(wv,wp)[1])<115,local(wv,wp)))
at(1,lambda:key(driver,'E',True));at(2,lambda:key(driver,'E',False));at(3.2,lambda:check('driver_possession',(driver.get_controlled_pawn()==v if driver else any(s.get_editor_property('bDriverSeat') and s.get_editor_property('Occupant')==(hp if role=='host' else cp) for s in v.get_seats()))))
at(3.5,observer_camera)
# Natural entry should leave the pawn near the side doorway. Move down the aisle using actual inputs.
route=[('Workbench',-190),('Medical',-145),('Kitchen',-40),('Storage',-195),('Power',60),('Navigation',130)]
for i,(n,x) in enumerate(route):
 t=4+i*5
 at(t,lambda x=x,n=n:(mark('station_'+n),move(x)));at(t+2.7,lambda n=n:aim_station(n));at(t+2.9,lambda:key(walker,'E',True));at(t+3.7,lambda:key(walker,'E',False));at(t+4.3,lambda n=n:station_check(n,'stationary_station'))
at(34,lambda:(move(-190),mark('stationary_return')));at(37,lambda:(stop_walk(),mark('low_speed_stand'),set_speed(500)))
at(40,lambda:check('low_speed',250<sv.get_velocity().length()<800 and abs(sv.get_velocity().z)<30,sv.get_velocity()))
at(44,lambda:(check('moderate_speed',sv.get_velocity().length()>1000 and abs(sv.get_velocity().z)<30,sv.get_velocity()),mark('moving_walk_front'),move(130)))
at(47,lambda:(check('moving_front',local(wv,wp)[0]>100 and frame_ok(),local(wv,wp)),stop_walk(),mark('moving_walk_rear'),move(-190)))
at(50,lambda:(check('moving_rear',local(wv,wp)[0]<-160 and frame_ok(),local(wv,wp)),stop_walk(),mark('highway_stand')))
at(52,lambda:check('highway_speed',sv.get_velocity().length()>2500 and abs(sv.get_velocity().z)<30,sv.get_velocity()))
for i,(n,x) in enumerate(route):
 t=53+i*5
 at(t,lambda x=x,n=n:(mark('station_'+n),move(x)));at(t+2.7,lambda n=n:aim_station(n));at(t+2.9,lambda:key(walker,'E',True));at(t+3.7,lambda:key(walker,'E',False));at(t+4.3,lambda n=n:station_check(n,'moving_station'))
at(83,lambda:(move(-145),mark('moving_return')));at(86,lambda:(stop_walk(),mark('sideways'),look(walker,unreal.Rotator(yaw=wv.get_actor_rotation().yaw)),key(walker,'D',True)));at(86.13,lambda:key(walker,'D',False));at(87,lambda:check('sideways_walk',local(wv,wp)[1]>anchors['sideways'][1]+10,local(wv,wp)))
at(87.2,lambda:key(walker,'A',True));at(87.33,lambda:key(walker,'A',False))
mouse_before={}
def begin_mouse(k):
 if not walker:return
 mouse_before[k]=walker.get_control_rotation();key(walker,k+' 1',True)
def end_mouse(k):
 if not walker:return
 key(walker,k,False);a=mouse_before[k];b=walker.get_control_rotation()
 delta=unreal.MathLibrary.normalized_delta_rotator(b,a)
 check('moving_mouse_'+k,abs(delta.yaw if k=='MouseX' else delta.pitch)>1 and frame_ok(),str(delta))
at(87.4,lambda:begin_mouse('MouseX'));at(87.6,lambda:end_mouse('MouseX'))
at(87.65,lambda:begin_mouse('MouseY'));at(87.85,lambda:end_mouse('MouseY'))
at(88,lambda:(mark('gentle_turn'),key(driver,'D',True)));at(88.15,lambda:key(driver,'D',False));at(89.9,lambda:check('gentle_turn_occurred',abs(sv.get_actor_rotation().yaw-yaws['gentle_turn'])>1,sv.get_actor_rotation()))
at(93.9,lambda:check('strong_turn_occurred',abs(sv.get_actor_rotation().yaw-yaws['strong_turn'])>5,sv.get_actor_rotation()))
at(90,lambda:(mark('strong_turn'),key(driver,'A',True)));at(90.6,lambda:key(driver,'A',False))
at(85.3,lambda:aim_station('Medical'));at(85.4,lambda:key(walker,'E',True));at(85.6,lambda:key(walker,'E',False));at(85.85,lambda:check('moving_early_release_cancel',ss['Medical'].get_editor_property('InteractionCount')==station_initial['Medical'],ss['Medical'].get_editor_property('InteractionCount')))
at(89.7,lambda:aim_station('Medical'));at(90.02,lambda:key(walker,'E',True));at(90.85,lambda:key(walker,'E',False));at(91.3,lambda:station_check('Medical','turning_station'))
at(91.5,lambda:(aim_station('Medical'),key(walker,'E',True)));at(91.7,lambda:look(walker,unreal.Rotator(yaw=wv.get_actor_rotation().yaw+180)));at(92.2,lambda:key(walker,'E',False));at(92.5,lambda:check('moving_look_away_cancel',ss['Medical'].get_editor_property('InteractionCount')==station_initial['Medical'],ss['Medical'].get_editor_property('InteractionCount')))
at(94,lambda:(mark('braking_stand'),set_speed(None),key(driver,'W',False),key(driver,'S',True)));at(97,lambda:(key(driver,'S',False),key(driver,'SpaceBar',True)));at(100,lambda:check('vehicle_stopped',sv.get_velocity().length()<150,sv.get_velocity()))
at(101,lambda:(mark('resume_stand'),key(driver,'SpaceBar',False),key(driver,'W',True)));at(104,lambda:check('resume_driving',sv.get_velocity().length()>250 and abs(sv.get_velocity().z)<30,sv.get_velocity()));at(105,lambda:(key(driver,'W',False),key(driver,'SpaceBar',True)))
# Exit the open side door by walking; then prove normal world movement is restored.
at(111,lambda:(move(122),mark('exit_approach')));at(113,lambda:(stop_walk(),look(walker,unreal.Rotator(yaw=wv.get_actor_rotation().yaw+90)),key(walker,'W',True)));at(115,lambda:key(walker,'W',False))
at(116,lambda:check('ordinary_world_movement_restored',not wp.get_component_by_class(FC).get_editor_property('ReferenceFrame') and wp.get_component_by_class(unreal.CharacterMovementComponent).get_editor_property('MaxWalkSpeed')==default_speed and wp.get_component_by_class(unreal.CapsuleComponent).get_unscaled_capsule_radius()==default_radius,local(wv,wp)))
at(117,lambda:move_y(10));at(119.5,stop_walk);at(120,lambda:check('reentry',frame_ok(),local(wv,wp)))
def finish():
 global active
 if not active:return
 active=False;stop_walk()
 for pc in [host,client]:
  for k in ['W','S','A','D','E','SpaceBar','MouseX','MouseY']:key(pc,k,False)
 # Explicit measurements retain failures; no acceptance inferred from attachment.
 for p in ['low_speed_stand','acceleration_stand','highway_stand','gentle_turn','strong_turn','braking_stand','resume_stand']:
  rs=[r for r in rows if r['phase']==p]
  if rs:
   a=anchors[p];drift=max(math.dist(r['local'][:2],a[:2]) for r in rs);lost=sum(not r['frame'] for r in rs);cor=max(r['corr'] for r in rs);cm=max(r['maxcorr'] for r in rs)
   check(p+'_stable',drift<10 and lost==0 and cm<10,{'drift_cm':drift,'frame_lost_samples':lost,'corrections':cor,'max_correction_cm':cm})
 rs=[r for r in rows if 37<r['t']<116];check('floor_and_observer',max(math.dist(r['server'],r['client']) for r in rs)<(75 if config.get('network') else 30) and all(165<r['local'][2]<210 and r['frame'] for r in rs),{'min_z':min(r['local'][2] for r in rs),'max_z':max(r['local'][2] for r in rs),'max_observer_local_error_cm':max(math.dist(r['server'],r['client']) for r in rs)})
 check('visible_observer',max(math.dist(r['visual'],r['local']) for r in rs)<(75 if config.get('network') else 30) and all(165<r['visual'][2]<210 and abs(r['visual'][1])<115 for r in rs),{'max_visual_local_error_cm':max(math.dist(r['visual'],r['local']) for r in rs)})
 json.dump({'config':config,'process_id':os.getpid(),'authority':isServer,'station_counts':{n:a.get_editor_property('InteractionCount') for n,a in st.items()},'results':results,'samples':rows,'anchors':anchors},open(B+out+'.json','w'),indent=2);unreal.unregister_slate_post_tick_callback(handle);unreal.log('GATE3_SUITE_DONE '+out)
at(122,finish);events=[(t+6 if t>=44 else t,f) for t,f in events]
at(39,lambda:(mark('low_walk_front'),move(130)))
at(42,lambda:(check('low_speed_front',local(wv,wp)[0]>100 and frame_ok(),local(wv,wp)),mark('low_walk_rear'),move(-190)))
at(45,lambda:(check('low_speed_rear',local(wv,wp)[0]<-160 and frame_ok(),local(wv,wp)),stop_walk(),mark('acceleration_stand'),set_speed(2700)))
events.sort(key=lambda e:e[0])
def tick(dt):
 global elapsed,idx,sample_acc
 elapsed=time.time()-session['start'];sample_acc+=dt
 if elapsed<0:return
 try:
  while idx<len(events) and elapsed>=events[idx][0]:f=events[idx][1];idx+=1;f()
  if speed_target is not None:
   speed=sv.get_velocity().length();drive_key('W',speed<speed_target-25);drive_key('S',speed>speed_target+50)
  if target is not None:
   axis,value=target;d=value-local(wv,wp)[axis];walk_key('W',d>8 if axis==0 else d< -8);walk_key('S',d< -8 if axis==0 else d>8)
  if sample_acc>.05:sample_acc=0;snap()
 except Exception as e:unreal.log_error('GATE3_SUITE_ERROR '+str(e));finish()
handle=unreal.register_slate_post_tick_callback(tick)
