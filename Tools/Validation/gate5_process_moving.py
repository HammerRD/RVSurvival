import unreal,json,math,time,os
B='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate5Validation/'
session=json.load(open(B+'process_session.json'));config=session['config'];role=config['driver']
VC=unreal.load_class(None,'/Script/RVSurvival.RVInteriorMotorhome');CC=unreal.load_class(None,'/Script/RVSurvival.RVSurvivorCharacter');FC=unreal.load_class(None,'/Script/RVSurvival.RVPassengerReferenceFrameComponent');EC=unreal.load_class(None,'/Script/RVSurvival.RVVehicleEntryPoint');SC=unreal.load_class(None,'/Script/RVSurvival.RVInteriorStation')
world=next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='Gate5SurvivalTest' and unreal.GameplayStatics.get_player_controller(w,0) and unreal.GameplayStatics.get_player_controller(w,0).get_controlled_pawn())
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
 rs=[r for r in rows if 37<r['t']<116]
 if rs:
  check('floor_and_observer',max(math.dist(r['server'],r['client']) for r in rs)<(75 if config.get('network') else 30) and all(165<r['local'][2]<210 and r['frame'] for r in rs),{'min_z':min(r['local'][2] for r in rs),'max_z':max(r['local'][2] for r in rs),'max_observer_local_error_cm':max(math.dist(r['server'],r['client']) for r in rs)})
  check('visible_observer',max(math.dist(r['visual'],r['local']) for r in rs)<(75 if config.get('network') else 30) and all(165<r['visual'][2]<210 and abs(r['visual'][1])<115 for r in rs),{'max_visual_local_error_cm':max(math.dist(r['visual'],r['local']) for r in rs)})
 else:
  check('floor_and_observer',False,'No movement samples collected')
  check('visible_observer',False,'No movement samples collected')
 check('completed_moving_storage_sequence',elapsed>=175,elapsed)
 storage_rows=[r for r in rows if 130<r['t']<176]
 check('storage_floor_and_corrections',bool(storage_rows) and all(r['frame'] and 165<r['local'][2]<210 and r['maxcorr']<10 for r in storage_rows))
 json.dump({'config':config,'process_id':os.getpid(),'authority':isServer,'station_counts':{n:a.get_editor_property('InteractionCount') for n,a in st.items()},'results':results,'samples':rows,'anchors':anchors},open(B+out+'.json','w'),indent=2);unreal.unregister_slate_post_tick_callback(handle);unreal.log('GATE3_SUITE_DONE '+out)
at(178,finish);events=[(t+6 if t>=44 else t,f) for t,f in events]
at(39,lambda:(mark('low_walk_front'),move(130)))
at(42,lambda:(check('low_speed_front',local(wv,wp)[0]>100 and frame_ok(),local(wv,wp)),mark('low_walk_rear'),move(-190)))
at(45,lambda:(check('low_speed_rear',local(wv,wp)[0]<-160 and frame_ok(),local(wv,wp)),stop_walk(),mark('acceleration_stand'),set_speed(2700)))
IC=unreal.load_class(None,'/Script/RVSurvival.RVInventoryComponent');StorageClass=unreal.load_class(None,'/Script/RVSurvival.RVStoragePoint');PickupClass=unreal.load_class(None,'/Script/RVSurvival.RVWorldItem')
server_inv=swp.get_component_by_class(IC);local_inv=wp.get_component_by_class(IC)
server_storage={str(a.get_editor_property('Container').get_editor_property('DisplayName')):a for a in unreal.GameplayStatics.get_all_actors_of_class(sw,StorageClass)}
client_storage={str(a.get_editor_property('Container').get_editor_property('DisplayName')):a for a in unreal.GameplayStatics.get_all_actors_of_class(cw,StorageClass)}
local_storage=client_storage if role=='host' else server_storage
seed_ids={};storage_yaw=0

def guid(i):return unreal.GuidLibrary.conv_guid_to_string(i)
def item_named(inv,name):return next(x for x in inv.get_items() if str(x.definition.get_editor_property('CatalogId'))==name)
def seed_inventory():
 if not isServer:return
 for name in ['Water','Bandage','Tool','EnginePart','Food']:
  item=unreal.RVItemInstance();item.set_editor_property('Id',unreal.GuidLibrary.new_guid());item.set_editor_property('Definition',unreal.load_asset('/Game/Items/DA_'+name));item.set_editor_property('Condition',.62);item.set_editor_property('Quantity',3 if name=='Food' else 1)
  state=unreal.RVItemStateEntry();state.set_editor_property('Key','Batch');state.set_editor_property('Value','MovingStorageTest');item.set_editor_property('CustomState',[state])
  seed_ids[name]=guid(item.id);server_inv.add_authority(item)
 check('inventory_seed_fixture',len(server_inv.get_items())==5)
def aim_storage(name):
 stop_walk();a=local_storage[name];look(walker,unreal.MathLibrary.find_look_at_rotation(wp.get_actor_location()+unreal.Vector(0,0,64),a.get_actor_location()))
def storage_open_check(name):
 if not isServer and not walker:return
 a=server_storage[name].get_editor_property('Container');b=local_storage[name].get_editor_property('Container')
 check('open_'+name,server_inv.get_editor_property('OpenContainer')==a and local_inv.get_editor_property('OpenContainer')==b and frame_ok(),local(wv,wp))
def transfer_to(name):
 if not walker:return
 local_inv.request_transfer(item_named(local_inv,name).id,1,True)
def transfer_back(storage):
 if not walker:return
 local_inv.request_transfer(local_storage[storage].get_editor_property('Container').get_items()[0].id,1,False)
def stored_check(storage,name,phase_name,min_speed):
 a=server_storage[storage].get_editor_property('Container').get_items();b=client_storage[storage].get_editor_property('Container').get_items()
 good=len(a)==1 and len(b)==1 and guid(a[0].id)==seed_ids[name] and guid(b[0].id)==seed_ids[name] and abs(a[0].condition-.62)<.001 and a[0].custom_state[0].value=='MovingStorageTest'
 check(phase_name,good and frame_ok() and sv.get_velocity().length()>=min_speed,{'server_quantity':sum(x.quantity for x in a),'client_quantity':sum(x.quantity for x in b),'speed':sv.get_velocity().length(),'passenger_local':local(wv,wp),'corrections':wp.get_component_by_class(FC).get_editor_property('CorrectionCount')})
def returned_check(name,phase_name):
 a=item_named(server_inv,name);b=item_named(local_inv,name)
 check(phase_name,guid(a.id)==seed_ids[name] and guid(b.id)==seed_ids[name] and a.quantity==b.quantity==1 and abs(a.condition-.62)<.001 and frame_ok())
def start_turn():
 global storage_yaw
 storage_yaw=sv.get_actor_rotation().yaw;mark('storage_gentle_turn');key(driver,'D 0.08',True)
def turn_check():
 angular=sv.get_editor_property('Mesh').get_physics_angular_velocity_in_degrees().z
 check('storage_transfer_during_actual_turn',abs(angular)>1 and abs(sv.get_actor_rotation().yaw-storage_yaw)>1 and frame_ok(),{'angular_deg_s':angular,'yaw':sv.get_actor_rotation().yaw})
def dropped():
 return next(a for a in unreal.GameplayStatics.get_all_actors_of_class(sw,PickupClass) if guid(a.get_editor_property('Item').id)==seed_ids['Tool'])
def drop_check():
 a=dropped();b=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(cw,PickupClass) if guid(a.get_editor_property('Item').id)==seed_ids['Tool'])
 check('moving_drop_floor_attachment',a.get_attach_parent_actor()==sv and b.get_attach_parent_actor()==cv and abs(a.get_editor_property('Item').condition-.62)<.001 and sv.get_velocity().length()>1000,{'server_local':local(sv,a),'client_local':local(cv,b)})
def aim_drop():
 a=dropped();look(walker,unreal.MathLibrary.find_look_at_rotation(wp.get_actor_location()+unreal.Vector(0,0,64),a.get_actor_location()))
at(.2,seed_inventory)
at(130,lambda:(mark('storage_stationary'),move(-195)));at(133,lambda:aim_storage('General cabinet'));at(133.2,lambda:key(walker,'E',True));at(134.1,lambda:key(walker,'E',False));at(134.5,lambda:storage_open_check('General cabinet'))
at(134.7,lambda:transfer_to('EnginePart'));at(135.6,lambda:stored_check('General cabinet','EnginePart','stationary_rv_storage',0));at(135.8,lambda:transfer_back('General cabinet'));at(136.7,lambda:returned_check('EnginePart','stationary_return'));at(137,local_inv.request_close_container)
at(138,lambda:(key(driver,'SpaceBar',False),mark('storage_low_speed'),set_speed(500)));at(140,lambda:aim_storage('General cabinet'));at(140.2,lambda:key(walker,'E',True));at(141.1,lambda:key(walker,'E',False));at(141.5,lambda:transfer_to('EnginePart'));at(142.4,lambda:stored_check('General cabinet','EnginePart','low_speed_rv_storage',250));at(142.6,lambda:transfer_back('General cabinet'));at(143.5,lambda:returned_check('EnginePart','low_speed_return'));at(144,local_inv.request_close_container)
at(145,lambda:(mark('storage_road_speed'),set_speed(1800),move(-40)));at(148,lambda:aim_storage('Pantry'));at(148.2,lambda:key(walker,'E',True));at(149.1,lambda:key(walker,'E',False));at(149.5,lambda:storage_open_check('Pantry'));at(149.7,lambda:transfer_to('Water'));at(150.7,lambda:stored_check('Pantry','Water','road_speed_pantry_storage',1000));at(150.9,lambda:transfer_back('Pantry'));at(151.8,lambda:returned_check('Water','road_speed_return'));at(152,lambda:transfer_to('Tool'));at(152.8,lambda:check('pantry_tag_filter',len(server_storage['Pantry'].get_editor_property('Container').get_items())==0 and guid(item_named(server_inv,'Tool').id)==seed_ids['Tool']));at(153,local_inv.request_close_container)
at(154,lambda:(move(-145),start_turn()));at(156,lambda:aim_storage('Medical storage'));at(156.2,lambda:key(walker,'E',True));at(157.1,lambda:key(walker,'E',False));at(157.5,lambda:storage_open_check('Medical storage'));at(157.7,lambda:transfer_to('Bandage'));at(158.7,lambda:(stored_check('Medical storage','Bandage','turning_medical_storage',1000),turn_check()));at(158.9,lambda:transfer_back('Medical storage'));at(159.8,lambda:returned_check('Bandage','turning_return'));at(160,local_inv.request_close_container);at(161,lambda:key(driver,'D',False))
at(162,lambda:(mark('storage_tool'),move(-190)));at(164,lambda:aim_storage('Tool storage'));at(164.2,lambda:key(walker,'E',True));at(165.1,lambda:key(walker,'E',False));at(165.5,lambda:storage_open_check('Tool storage'));at(165.7,lambda:transfer_to('Tool'));at(166.7,lambda:stored_check('Tool storage','Tool','moving_tool_storage',1000));at(166.9,lambda:transfer_back('Tool storage'));at(167.8,lambda:returned_check('Tool','tool_return'));at(168,local_inv.request_close_container)
at(170,lambda:local_inv.request_drop(item_named(local_inv,'Tool').id,1));at(172,drop_check);at(172.2,aim_drop);at(172.5,lambda:key(walker,'E',True));at(173.5,lambda:key(walker,'E',False));at(175,lambda:returned_check('Tool','moving_drop_repick'))
def collect_ids():
 if not isServer:seed_ids.update({str(x.definition.get_editor_property('CatalogId')):guid(x.id) for x in server_inv.get_items()})
at(3.8,collect_ids)
def record_signature(component):
 return sorted((guid(x.id),str(x.definition.get_editor_property('CatalogId')),x.quantity,round(x.condition,4),[(str(s.key),s.value) for s in x.custom_state]) for x in component.get_items())
movement_snap=snap
def snap():
 movement_snap()
 rows[-1]['inventory']=record_signature(server_inv)
 rows[-1]['containers']={name:record_signature(actor.get_editor_property('Container')) for name,actor in server_storage.items()}

# Gate 5 survival integration: preserve the accepted full movement/storage route.
host_needs=hp.get_editor_property('PlayerState').get_editor_property('Needs')
client_needs=cp.get_editor_property('PlayerState').get_editor_property('Needs')
passenger_needs=client_needs if role=='host' else host_needs
def survival_setup():
 if not isServer:return
 cmd(own,'rv.Needs.AllowDebug 1')
 passenger_needs.debug_set_values(20,20,10)
 (host_needs if role=='host' else client_needs).debug_set_values(70,60,15)
consume_expected={}
def consume(name):
 st=passenger_needs.get_editor_property('State');consume_expected[name]=min(100,(st.nutrition+25) if name=='Food' else (st.hydration+35))
 if walker:passenger_needs.request_consume(item_named(local_inv,name).id)
def consumed_check(name,count,need,value,label,moving=False):
 state=passenger_needs.get_editor_property('State');actual=getattr(state,need)
 check(label,sum(x.quantity for x in local_inv.get_items() if str(x.definition.get_editor_property('CatalogId'))==name)==count and abs(actual-consume_expected[name])<.1 and frame_ok() and (not moving or sv.get_velocity().length()>1000),{'value':actual,'speed':sv.get_velocity().length(),'local':local(wv,wp)})
at(.3,survival_setup)
at(35,lambda:consume('Food'));at(36,lambda:consumed_check('Food',2,'nutrition',45,'stationary_eating'))
at(54,lambda:consume('Food'));at(55,lambda:consumed_check('Food',1,'nutrition',70,'highway_eating',True))
at(152,lambda:consume('Water'));at(153.5,lambda:consumed_check('Water',0,'hydration',55,'road_speed_drinking',True))
at(158,lambda:consume('Food'));at(159.5,lambda:consumed_check('Food',0,'nutrition',95,'turning_eating',True))
def continued_needs():
 a=passenger_needs.get_editor_property('State');d=(host_needs if role=='host' else client_needs).get_editor_property('State')
 check('needs_update_during_riding',a.simulated_seconds>160 and a.fatigue>10 and a.hydration<55,{'seconds':a.simulated_seconds,'fatigue':a.fatigue,'hydration':a.hydration})
 check('possession_preserves_independent_needs',60<d.nutrition<71 and 50<d.hydration<61 and d.fatigue>15,{'nutrition':d.nutrition,'hydration':d.hydration,'fatigue':d.fatigue})
at(176,continued_needs)
old_survival_snap=snap
def needs_signature(component):
 s=component.get_editor_property('State');return {'nutrition':s.nutrition,'hydration':s.hydration,'fatigue':s.fatigue,'reserve':s.survival_reserve,'seconds':s.simulated_seconds,'rest':str(s.rest_mode)}
def snap():
 old_survival_snap();rows[-1]['needs']={'host':needs_signature(host_needs),'client':needs_signature(client_needs)}


rest_test_point=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.RVRestPoint) if str(a.get_editor_property('DisplayName'))=='Rear bed')
def aim_rest():
 stop_walk();look(walker,unreal.MathLibrary.find_look_at_rotation(wp.get_actor_location()+unreal.Vector(0,0,64),rest_test_point.get_actor_location()))
def enter_sleep_if_walking():
 if walker:passenger_needs.request_rest_mode(unreal.RVRestMode.SLEEPING)
def sleeping_check():
 check('parked_passenger_sleep',passenger_needs.get_editor_property('State').rest_mode==unreal.RVRestMode.SLEEPING and rest_test_point.get_editor_property('Occupant') is not None and frame_ok())
def automatic_wake():
 check('moving_platform_automatically_wakes_and_frees_rest',passenger_needs.get_editor_property('State').rest_mode==unreal.RVRestMode.AWAKE and rest_test_point.get_editor_property('Occupant') is None and sv.get_velocity().length()>50 and frame_ok(),sv.get_velocity().length())
at(112,aim_rest);at(112.2,lambda:key(walker,'E',True));at(113.1,lambda:key(walker,'E',False));at(113.5,enter_sleep_if_walking);at(114.2,sleeping_check)
at(114.5,lambda:(key(driver,'SpaceBar',False),key(driver,'W',True)));at(116,automatic_wake);at(116.1,lambda:(key(driver,'W',False),key(driver,'SpaceBar',True)))

events.sort(key=lambda e:e[0])
def tick(dt):
 global elapsed,idx,sample_acc
 elapsed=time.time()-session['start'];sample_acc+=dt
 if elapsed<0:return
 try:
  while idx<len(events) and elapsed>=events[idx][0]:f=events[idx][1];idx+=1;f()
  if not active:return
  if speed_target is not None:
   speed=sv.get_velocity().length();drive_key('W',speed<speed_target-25);drive_key('S',speed>speed_target+50)
  if target is not None:
   axis,value=target;d=value-local(wv,wp)[axis];walk_key('W',d>8 if axis==0 else d< -8);walk_key('S',d< -8 if axis==0 else d>8)
  if sample_acc>.05:sample_acc=0;snap()
 except Exception as e:check('runner_exception',False,repr(e));unreal.log_error('GATE4_PROCESS_ERROR '+repr(e));finish()
handle=unreal.register_slate_post_tick_callback(tick)




