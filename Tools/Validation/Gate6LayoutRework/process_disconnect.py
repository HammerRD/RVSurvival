"""Native-control reservations, rear-seat contention and actual client disconnect.
UObjects live only in the runner namespace, released before disconnect/world teardown.
"""
import unreal,json,time,os
from pathlib import Path
B=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate6LayoutRework')
session=json.loads((B/'session.json').read_text());config=session['config'];start=session['start'];mode=config['disconnect']
w=next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='Gate6FuelElectricalTest' and unreal.GameplayStatics.get_player_controller(w,0) and unreal.GameplayStatics.get_player_controller(w,0).get_controlled_pawn())
authority=unreal.GameplayStatics.get_game_mode(w) is not None
pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn()
other=next(c for c in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSurvivorCharacter) if c!=p)
hp=p if authority else other;cp=other if authority else p
v=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSystemsMotorhome)[0]
driver=next(s for s in v.get_seats() if s.get_editor_property('bDriverSeat'))
passenger=next(s for s in v.get_seats() if not s.get_editor_property('bDriverSeat') and not s.get_editor_property('bInteriorOnly'))
front=v.get_editor_property('DinetteFrontSeat')
entries=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVVehicleEntryPoint)
def entry(seat,outside):return next(a for a in entries if a.get_editor_property('Seat')==seat and (abs(v.get_actor_transform().inverse_transform_location(a.get_actor_location()).y)>100)==outside)
de=entry(driver,True);pe=entry(passenger,True);fe=entry(front,False);di=entry(driver,False)
bed=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVRestPoint) if str(a.get_editor_property('DisplayName'))=='Rear bed')
ladder=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVLadder)[0]
pantry=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVStoragePoint) if str(a.get_editor_property('Container').get_editor_property('DisplayName'))=='Pantry')
initial_pantry=[unreal.GuidLibrary.conv_guid_to_string(i.id) for i in pantry.get_editor_property('Container').get_items()]
events=[];idx=0;results=[];active=True
def at(t,fn):events.append((t,fn))
def check(name,ok,detail=''):
 row={'case':name,'pass':bool(ok),'detail':str(detail)};results.append(row);unreal.log('CLEANUP_NATIVE '+json.dumps(row))
def key(k,on):unreal.RVInteriorMotorhome.dispatch_development_key(pc,k,on)
def aim(a):pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p.get_actor_location()+unreal.Vector(0,0,p.get_editor_property('BaseEyeHeight')),a.get_actor_location()))
def hold(t,k,duration,client_only=False):
 at(t,lambda:key(k,True) if not client_only or not authority else None)
 at(t+duration,lambda:key(k,False) if not client_only or not authority else None)
def setup():
 unreal.SystemLibrary.execute_console_command(pc,'t.MaxFPS 60',pc)
 unreal.SystemLibrary.execute_console_command(pc,'t.IdleWhenNotForeground 0',pc)
 if authority:
  for c,a,side in [(hp,de,-1),(cp,pe,1)]:
   q=v.get_actor_transform().inverse_transform_location(a.get_actor_location())
   position=unreal.Vector(-520,75,75) if mode=='Ladder' and c==cp else unreal.Vector(q.x,q.y+side*125,100)
   c.set_actor_location(v.get_actor_transform().transform_location(position),False,True)
at(0,setup);at(1,lambda:aim(de if authority else ladder if mode=='Ladder' else pe));hold(1.2,'E',.9)
at(3.5,lambda:check('normal_E_initial_reservation',driver.get_editor_property('Occupant')==hp and (ladder.get_editor_property('Occupant')==cp if mode=='Ladder' else passenger.get_editor_property('Occupant')==cp)))
if mode=='Bed':
 hold(4,'Three',.15,True)
 def rear_walk():
  if not authority:pc.set_control_rotation(unreal.Rotator(yaw=v.get_actor_rotation().yaw+180));key('W',True)
 at(6,rear_walk);at(7.5,lambda:key('W',False) if not authority else None)
 at(9,lambda:aim(bed) if not authority else None);hold(9.2,'E',.9,True);hold(12,'Z',.15,True)
 at(14,lambda:check('normal_E_Z_actual_bed_sleep',bed.get_editor_property('Occupant')==cp.get_editor_property('PlayerState') and cp.get_component_by_class(unreal.RVRestPoseComponent).get_editor_property('RestPoint')==bed and cp.get_editor_property('PlayerState').get_component_by_class(unreal.RVNeedsComponent).get_editor_property('State').rest_mode==unreal.RVRestMode.SLEEPING))
elif mode=='RearSeat':
 hold(4,'Three',.15)
 at(7,lambda:aim(fe));hold(7.2,'E',.9)
 at(9.5,lambda:check('simultaneous_native_E_one_bench_owner',front.get_editor_property('Occupant') in [hp,cp] and sum(c.get_editor_property('SeatedVehicle')==v for c in [hp,cp])==1))
 at(10,lambda:key('E',True) if front.get_editor_property('Occupant')==p else None)
 at(10.2,lambda:key('E',False))
 at(12,lambda:check('winning_rear_seat_native_E_stand',front.get_editor_property('Occupant') is None))
 at(12.5,lambda:aim(fe) if not authority else None);hold(12.7,'E',.9,True)
 at(14.5,lambda:check('client_native_E_rear_seat_before_disconnect',front.get_editor_property('Occupant')==cp))
else:
 hold(4,'W',1.8,True)
 at(7,lambda:check('client_native_W_ladder_before_disconnect',ladder.get_editor_property('Occupant')==cp and cp.get_component_by_class(unreal.CharacterMovementComponent).get_editor_property('MovementMode')==unreal.MovementMode.MOVE_FLYING))
def finish(release=True):
 global active
 if not active:return
 for k in ['E','W','S','Three','Z']:key(k,False)
 role='server' if authority else 'client'
 (B/(config['name']+'_'+role+'.json')).write_text(json.dumps({'pid':os.getpid(),'role':role,'config':config,'results':results},indent=2),encoding='utf-8')
 active=False;unreal.unregister_slate_post_tick_callback(h)
 if release:
  from runner_runtime import release_runners
  release_runners()
def disconnect_client():
 if authority:return
 check('client_disconnect_requested',True);finish(False)
 controller=pc;execute=unreal.SystemLibrary.execute_console_command
 from runner_runtime import release_runners
 release_runners();execute(controller,'disconnect',controller)
at(16,disconnect_client)
def cleanup_check():
 if not authority:return
 check('disconnect_removes_survivor_and_all_reservations',len(unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSurvivorCharacter))==1 and bed.get_editor_property('Occupant') is None and front.get_editor_property('Occupant') is None and ladder.get_editor_property('Occupant') is None)
 check('shared_pantry_unchanged',initial_pantry==[unreal.GuidLibrary.conv_guid_to_string(i.id) for i in pantry.get_editor_property('Container').get_items()])
 check('remaining_player_needs_awake',pc.player_state.get_component_by_class(unreal.RVNeedsComponent).get_editor_property('State').rest_mode==unreal.RVRestMode.AWAKE)
at(20,cleanup_check)
if mode=='RearSeat':
 at(21,lambda:aim(di) if authority else None);at(21.2,lambda:key('E',True) if authority else None);at(22.1,lambda:key('E',False) if authority else None)
at(23,lambda:key('W',True) if authority else None);at(24,lambda:key('W',False) if authority else None)
at(24.5,lambda:check('remaining_host_can_drive_after_disconnect',driver.get_editor_property('Occupant')==hp and v.get_velocity().length()>10,v.get_velocity().length()) if authority else None)
at(25,finish);events.sort(key=lambda e:e[0])
def tick(dt):
 global idx
 if not active:return
 t=time.time()-start
 if idx<len(events) and t>=events[idx][0]:
  fn=events[idx][1];idx+=1;terminating=fn.__name__=='disconnect_client' and not authority
  try:fn()
  except Exception as e:check('exception',False,repr(e));finish();return
  if terminating:return
h=unreal.register_slate_post_tick_callback(tick)
