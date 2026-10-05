import unreal,json,math
B='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate3Validation/'
config=json.load(open(B+'case.json'));role=config.get('driver','host');out=config.get('name',role)
ws=sorted([w for w in unreal.ObjectIterator(unreal.World) if '/Game/Maps/UEDPIE_' in w.get_path_name() and w.get_name()=='Gate3MovingInteriorTest'],key=lambda w:w.get_path_name());sw,cw=ws
host=unreal.GameplayStatics.get_player_controller(sw,0);client=unreal.GameplayStatics.get_player_controller(cw,0)
VC=unreal.load_class(None,'/Script/RVSurvival.RVInteriorMotorhome');CC=unreal.load_class(None,'/Script/RVSurvival.RVSurvivorCharacter');FC=unreal.load_class(None,'/Script/RVSurvival.RVPassengerReferenceFrameComponent');EC=unreal.load_class(None,'/Script/RVSurvival.RVVehicleEntryPoint');SC=unreal.load_class(None,'/Script/RVSurvival.RVInteriorStation')
sv=unreal.GameplayStatics.get_all_actors_of_class(sw,VC)[0];cv=unreal.GameplayStatics.get_all_actors_of_class(cw,VC)[0];hp=host.get_controlled_pawn();cp=client.get_controlled_pawn();sp=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(sw,CC) if a!=hp);chp=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(cw,CC) if a!=cp)
driver=host if role=='host' else client;walker=client if role=='host' else host;wp=cp if role=='host' else hp;swp=sp if role=='host' else hp;observer=sp if role=='client' else chp;wv=cv if role=='host' else sv
ss={str(a.get_editor_property('StationName')):a for a in unreal.GameplayStatics.get_all_actors_of_class(sw,SC)};cs={str(a.get_editor_property('StationName')):a for a in unreal.GameplayStatics.get_all_actors_of_class(cw,SC)};st=cs if role=='host' else ss
rows=[];results=[];events=[];idx=0;elapsed=0;sample_acc=0;phase='setup';target=None;held=set();anchors={};counts={};station_initial={};active=True;yaws={};speed_target=None;drive_held=set();default_radius=wp.get_component_by_class(unreal.CapsuleComponent).get_unscaled_capsule_radius();default_speed=wp.get_component_by_class(unreal.CharacterMovementComponent).get_editor_property('MaxWalkSpeed')

def cmd(pc,s):unreal.SystemLibrary.execute_console_command(pc,s,pc)
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
 stop_walk();target=(0,x);walker.set_control_rotation(unreal.Rotator(yaw=wv.get_actor_rotation().yaw))
def move_y(y):
 global target
 stop_walk();target=(1,y);walker.set_control_rotation(unreal.Rotator(yaw=wv.get_actor_rotation().yaw-90))
def mark(p):
 global phase
 phase=p;anchors[p]=local(wv,wp);yaws[p]=sv.get_actor_rotation().yaw;wp.get_component_by_class(FC).reset_diagnostics()
def setup():
 # Only fixture placement is teleported, before any driving. All interior traversal uses accepted input.
 swp.set_actor_location(sv.get_actor_transform().transform_location(unreal.Vector(122,300,110)),False,True);walker.set_control_rotation(unreal.Rotator(yaw=sv.get_actor_rotation().yaw-90))
 e=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(sw,EC) if a.get_editor_property('Seat').get_editor_property('bDriverSeat'));p=hp if role=='host' else sp
 pos=e.get_actor_location()-sv.get_actor_right_vector()*180;pos.z=92;p.set_actor_location(pos,False,True);driver.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(pos+unreal.Vector(0,0,64),e.get_actor_location()))
def frame_ok():return wp.get_component_by_class(FC).get_editor_property('ReferenceFrame')==wv and swp.get_component_by_class(FC).get_editor_property('ReferenceFrame')==sv
def aim_station(n):
 stop_walk();a=st[n];walker.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(wp.get_actor_location()+unreal.Vector(0,0,64),a.get_actor_location()));station_initial[n]=ss[n].get_editor_property('InteractionCount')
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
at(1,lambda:key(driver,'E',True));at(2,lambda:key(driver,'E',False));at(3.2,lambda:check('driver_possession',driver.get_controlled_pawn()==(sv if role=='host' else cv)))
at(3.5,observer_camera)

at(4,lambda:move(-145));at(7,lambda:(stop_walk(),mark('stationary_soak')))
at(12,lambda:(mark('accelerating'),set_speed(2700)))
at(25,lambda:(check('highway_speed',sv.get_velocity().length()>2500 and abs(sv.get_velocity().z)<30,sv.get_velocity()),mark('cruise_soak')))
at(85,lambda:mark('turning_soak'))
for t in [88,100,112,124,136]:
 at(t,lambda:key(driver,'D',True));at(t+.15,lambda:key(driver,'D',False))
at(145,lambda:(mark('braking_soak'),set_speed(None),key(driver,'S',True)))
at(148,lambda:(key(driver,'S',False),key(driver,'SpaceBar',True)))
def finish_soak():
 for pc in [host,client]:
  for k in ['W','S','A','D','E','SpaceBar']:key(pc,k,False)
 for p in ['stationary_soak','cruise_soak','turning_soak','braking_soak']:
  rs=[r for r in rows if r['phase']==p];a=anchors[p]
  drift=max(math.dist(r['local'][:2],a[:2]) for r in rs);lost=sum(not r['frame'] for r in rs);cm=max(r['maxcorr'] for r in rs)
  check(p,drift<10 and lost==0 and cm<10,{'duration':rs[-1]['t']-rs[0]['t'],'samples':len(rs),'drift_cm':drift,'floor_losses':lost,'corrections':max(r['corr'] for r in rs),'max_correction_cm':cm})
 rs=[r for r in rows if r['phase'] in ['cruise_soak','turning_soak']]
 check('continuous_highway',min(r['speed'] for r in rs)>2500,min(r['speed'] for r in rs))
 check('observer_alignment',max(math.dist(r['server'],r['client']) for r in rs)<75,max(math.dist(r['server'],r['client']) for r in rs))
 check('floor_height',all(165<r['local'][2]<210 for r in rs))
 json.dump({'config':config,'results':results,'samples':rows,'anchors':anchors},open(B+out+'.json','w'),indent=2)
 unreal.unregister_slate_post_tick_callback(handle);unreal.log('GATE3_SOAK_DONE '+out)
at(158,finish_soak);events.sort(key=lambda e:e[0])
def tick(dt):
 global elapsed,idx
 elapsed+=dt
 try:
  while idx<len(events) and elapsed>=events[idx][0]:f=events[idx][1];idx+=1;f()
  if speed_target is not None:
   speed=sv.get_velocity().length();drive_key('W',speed<speed_target-25);drive_key('S',speed>speed_target+50)
  if target is not None:
   axis,value=target;d=value-local(wv,wp)[axis];walk_key('W',d>8 if axis==0 else d< -8);walk_key('S',d< -8 if axis==0 else d>8)
  snap()
 except Exception as e:unreal.log_error('GATE3_SOAK_ERROR '+str(e));unreal.unregister_slate_post_tick_callback(handle)
handle=unreal.register_slate_post_tick_callback(tick)
