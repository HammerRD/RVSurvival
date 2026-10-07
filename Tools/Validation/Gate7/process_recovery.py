"""Separate-process rollover recovery through normal Enhanced Input F8.
Only setup/fault injection uses development fixtures. No direct recovery call.
"""
import unreal,json,time,os,math
from pathlib import Path
B=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate7Validation')
session=json.loads((B/'session.json').read_text());config=session['config'];start=session['start']
w=next(a for a in unreal.ObjectIterator(unreal.World) if a.get_name()=='Gate7MechanicalTest' and unreal.GameplayStatics.get_player_controller(a,0) and unreal.GameplayStatics.get_player_controller(a,0).get_controlled_pawn())
authority=unreal.GameplayStatics.get_game_mode(w) is not None;role='server' if authority else 'client'
pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn()
other=next(c for c in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSurvivorCharacter) if c!=p)
v=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVMechanicalMotorhome)[0];r=v.get_editor_property('Recovery')
driver=next(s for s in v.get_seats() if s.get_editor_property('bDriverSeat'))
passenger=next(s for s in v.get_seats() if not s.get_editor_property('bDriverSeat') and not s.get_editor_property('bInteriorOnly'))
isdriver=authority==(config['driver']=='host');dp=p if isdriver else other;wp=other if isdriver else p
entries=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVVehicleEntryPoint)
de=next(a for a in entries if a.get_editor_property('Seat')==driver and abs(v.get_actor_transform().inverse_transform_location(a.get_actor_location()).y)>100)
pe=next(a for a in entries if a.get_editor_property('Seat')==passenger and abs(v.get_actor_transform().inverse_transform_location(a.get_actor_location()).y)>100)
events=[];held={};results=[];samples=[];before=None;resources=None;frames=0;maximum_speed=0;walk_start=None;interior_start=None
def check(n,b,d=''):
 results.append({'case':n,'pass':bool(b),'detail':str(d)});unreal.log('RECOVERY_NET '+role+' '+n+' '+str(bool(b)))
def press(key,seconds=.2):
 unreal.RVInteriorMotorhome.dispatch_development_key(pc,key,True);held[key]=(time.time()+seconds,frames+3)
def snapshot():
 items=[]
 for c in [p,other]:
  for i in c.get_component_by_class(unreal.RVInventoryComponent).get_items():
   items.append((unreal.GuidLibrary.conv_guid_to_string(i.id),i.quantity,i.condition,i.fuel_litres,i.fuel_revision))
 for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.Actor):
  if a==v or a.get_attach_parent_actor()==v:
   for container in a.get_components_by_class(unreal.RVContainerComponent):
    for i in container.get_items():items.append((unreal.GuidLibrary.conv_guid_to_string(i.id),i.quantity,i.condition,i.fuel_litres,i.fuel_revision))
 needs=[]
 for player_state in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVPlayerState):
  state=player_state.get_component_by_class(unreal.RVNeedsComponent).get_editor_property('State')
  needs.append((str(player_state.get_player_name()),state.nutrition,state.hydration,state.fatigue,state.survival_reserve,str(state.rest_mode)))
 cooling=v.get_editor_property('CoolingSystem').get_editor_property('Cooling')
 engine=v.get_editor_property('CoolingSystem').get_editor_property('Engine')
 return {'items':sorted(items),'needs':sorted(needs),'mechanical':(cooling.radiator_condition,cooling.coolant_litres,cooling.temperature_c,engine.condition),'resources':[v.get_editor_property('PropulsionFuel').get_editor_property('Litres'),v.get_editor_property('GeneratorFuel').get_editor_property('Litres'),v.get_editor_property('HouseBattery').get_editor_property('EnergyWh'),v.get_editor_property('ChassisBattery').get_editor_property('EnergyWh')]}
def setup():
 unreal.SystemLibrary.execute_console_command(pc,'t.MaxFPS 60',pc)
 unreal.SystemLibrary.execute_console_command(pc,'rv.Needs.AllowDebug 1',pc)
 unreal.SystemLibrary.execute_console_command(pc,'rv.Resources.AllowDebug 1',pc)
 if not authority:return
 assert v.get_editor_property('CoolingSystem').debug_set_time_scale(0)
 assert v.get_editor_property('CoolingSystem').debug_set_state(.72,8.5,88,.83)
 assert v.get_editor_property('Electrical').debug_set_time_scale(0)
 assert v.get_editor_property('PropulsionFuel').debug_set_fuel(47.3)
 assert v.get_editor_property('GeneratorFuel').debug_set_fuel(4.7)
 assert v.get_editor_property('HouseBattery').debug_set_energy(888.4)
 assert v.get_editor_property('ChassisBattery').debug_set_energy(111.2)
 storage=next(a.get_editor_property('Container') for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVExteriorStoragePoint) if unreal.GameplayTagLibrary.get_num_gameplay_tags_in_container(a.get_editor_property('Container').get_editor_property('AllowedTags'))==0)
 cargo=unreal.RVItemInstance();cargo.set_editor_property('Id',unreal.GuidLibrary.new_guid());cargo.set_editor_property('Definition',unreal.load_asset('/Game/Items/DA_Tool'));cargo.set_editor_property('Condition',.61);cargo.set_editor_property('Quantity',1);storage.add_authority(cargo)
 check('seeded_shared_cargo',any(unreal.GuidLibrary.conv_guid_to_string(i.id)==unreal.GuidLibrary.conv_guid_to_string(cargo.id) for i in storage.get_items()))
 for c,entry,side in [(dp,de,-1),(wp,pe,1)]:
  c.get_editor_property('PlayerState').get_component_by_class(unreal.RVNeedsComponent).debug_set_time_scale(0)
  c.get_editor_property('PlayerState').get_component_by_class(unreal.RVNeedsComponent).debug_set_values(62 if c==dp else 81,73 if c==dp else 58,41 if c==dp else 22)
  q=v.get_actor_transform().inverse_transform_location(entry.get_actor_location())
  c.set_actor_location(v.get_actor_transform().transform_location(unreal.Vector(q.x,q.y+side*125,100)),False,True)
  i=unreal.RVItemInstance();i.set_editor_property('Id',unreal.GuidLibrary.new_guid());i.set_editor_property('Definition',unreal.load_asset('/Game/Items/DA_Food'));i.set_editor_property('Quantity',3);i.set_editor_property('Condition',.73)
  c.get_component_by_class(unreal.RVInventoryComponent).add_authority(i)
def aim():
 target=de if isdriver else pe
 pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p.get_actor_location()+unreal.Vector(0,0,p.get_editor_property('BaseEyeHeight')),target.get_actor_location()))
def occupants():return driver.get_editor_property('Occupant')==dp and passenger.get_editor_property('Occupant')==wp
def hold_throttle(on):
 if isdriver:unreal.RVInteriorMotorhome.dispatch_development_key(pc,'W',on)
def fixture(roll,uneven=False):
 if uneven:
  assert r.debug_create_surface(unreal.Vector(6000,6000,20),unreal.Rotator(pitch=2,roll=1),unreal.Vector(1000,1000,10))
 if not authority:return
 v.set_actor_location(unreal.Vector(6000,6000,160 if uneven else 145),False,True);r.debug_overturn(roll)
 v.get_editor_property('Electrical').debug_advance(.001,False,0,0)
def preflight(label):
 global before,resources
 check(label+'_confirmed',r.get_editor_property('bConfirmedOverturned'),str(v.get_actor_rotation()))
 before=v.get_actor_location();resources=snapshot()
def recover(request_host):
 if authority==request_host:press('F8')
def complete(label,revision,seated=True):
 check(label+'_upright_converged',v.get_actor_up_vector().z>.98 and r.get_editor_property('RecoveryRevision')==revision,str(v.get_actor_rotation()))
 check(label+'_nearby',math.hypot(before.x-v.get_actor_location().x,before.y-v.get_actor_location().y)<450)
 after=snapshot();deltas=[b-a for a,b in zip(resources['resources'],after['resources'])]
 # Electrical debug rates clamp to 0.01; ordinary idle/load balances continue.
 # Check exact items/needs/mechanics and bound the legitimate five-second flow.
 check(label+'_items_needs_mechanics_exact',all(after[k]==resources[k] for k in ['items','needs','mechanical']),{'before':resources,'after':after})
 check(label+'_resources_no_reset_or_loss',all(abs(d)<=limit for d,limit in zip(deltas,[.001,.001,.1,.1])),deltas)
 if seated:check(label+'_seats_possession_preserved',occupants() and (pc.get_controlled_pawn()==v if isdriver else pc.get_controlled_pawn()==p))
def reject_repeat(revision):check('upright_repeat_rejected_'+str(revision),r.get_editor_property('RecoveryRevision')==revision,pc.get_editor_property('RecoveryFeedback'))
def stand():
 if not isdriver:press('Three')
def standing_check():
 check('passenger_standing_interior',wp.get_editor_property('SeatedVehicle') is None and wp.get_component_by_class(unreal.RVPassengerReferenceFrameComponent).get_editor_property('ReferenceFrame')==v)
def evac_check():
 check('standing_passenger_safe_after_recovery',wp.get_editor_property('SeatedVehicle') is None and wp.get_actor_location().z>0 and wp.get_component_by_class(unreal.CharacterMovementComponent).get_editor_property('MovementMode')==unreal.MovementMode.MOVE_WALKING,str(wp.get_actor_location()))
 check('driver_preserved_after_standing_recovery',driver.get_editor_property('Occupant')==dp)
def drive():
 if isdriver:press('W',5)
def walk_after_recovery():
 global walk_start
 walk_start=wp.get_actor_location()
 if not isdriver:pc.set_control_rotation(unreal.Rotator(yaw=90));press('W',1.5)
def walked():
 q=wp.get_actor_location();check('standing_movement_after_recovery',math.hypot(q.x-walk_start.x,q.y-walk_start.y)>150,str(q))
def driven():check('driving_after_recovery',maximum_speed>200,maximum_speed)
def brake():
 if isdriver:press('S',3)
def park():
 if isdriver:press('SpaceBar',5)
def approach_passenger():
 if not authority:return
 check('stopped_for_reentry',v.get_velocity().length()<30,v.get_velocity().length())
 q=v.get_actor_transform().inverse_transform_location(pe.get_actor_location())
 wp.set_actor_location(v.get_actor_transform().transform_location(unreal.Vector(q.x,q.y+125,100)),False,True)
def aim_passenger():
 if not isdriver:pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p.get_actor_location()+unreal.Vector(0,0,p.get_editor_property('BaseEyeHeight')),pe.get_actor_location()))
def enter_passenger():
 if not isdriver:press('E',.85)
def enter_interior():
 if not isdriver:press('Three')
def restored_interior():
 global interior_start
 interior_start=v.get_actor_transform().inverse_transform_location(wp.get_actor_location())
 wp.get_component_by_class(unreal.RVPassengerReferenceFrameComponent).reset_diagnostics()
 check('normal_E_3_reentry_after_recovery',occupants()==False and driver.get_editor_property('Occupant')==dp and wp.get_component_by_class(unreal.RVPassengerReferenceFrameComponent).get_editor_property('ReferenceFrame')==v)
def walk_inside():
 if not isdriver:pc.set_control_rotation(unreal.Rotator(yaw=v.get_actor_rotation().yaw+180));press('W',.35)
def interior_walking():
 q=v.get_actor_transform().inverse_transform_location(wp.get_actor_location());frame=wp.get_component_by_class(unreal.RVPassengerReferenceFrameComponent)
 check('moving_interior_walking_after_recovery',frame.get_editor_property('ReferenceFrame')==v and 140<q.z<230 and q.x<interior_start.x-20,{'local':str(q),'start':str(interior_start),'corrections':frame.get_editor_property('CorrectionCount'),'max_cm':frame.get_editor_property('MaxCorrectionCm')})
def turn():
 if isdriver:press('D',1)
def turning_interior():
 q=v.get_actor_transform().inverse_transform_location(wp.get_actor_location());frame=wp.get_component_by_class(unreal.RVPassengerReferenceFrameComponent)
 check('moving_interior_turn_after_recovery',frame.get_editor_property('ReferenceFrame')==v and 140<q.z<230,{'local':str(q),'corrections':frame.get_editor_property('CorrectionCount'),'max_cm':frame.get_editor_property('MaxCorrectionCm')})
def finish():
 hold_throttle(False)
 for key in list(held):unreal.RVInteriorMotorhome.dispatch_development_key(pc,key,False)
 unreal.unregister_slate_post_tick_callback(h)
 (B/(config['name']+'_'+role+'.json')).write_text(json.dumps({'pid':os.getpid(),'role':role,'config':config,'results':results,'samples':samples},indent=2),encoding='utf-8')
events=[(0,setup),(1,aim),(1.3,lambda:press('E',.85)),(4,lambda:check('normal_E_two_seats',occupants()))]
events.extend([(7.5,lambda:hold_throttle(True)),(25.5,lambda:check('held_throttle_requires_release_after_recovery',v.get_velocity().length()<30,v.get_velocity().length())),(26,lambda:hold_throttle(False))])
for i,roll in enumerate([90,-90,180]):
 t=8+i*20;label=str(roll);revision=i+1
 events.extend([(t,lambda roll=roll:fixture(roll)),(t+11,lambda label=label:preflight(label)),(t+12,lambda host=i!=1:recover(host)),(t+16,lambda label=label,rev=revision:complete(label,rev)),(t+17,lambda:press('F8')),(t+19,lambda rev=revision:reject_repeat(rev))])
events.extend([(69,stand),(72,standing_check),(74,lambda:fixture(90,True)),(85,lambda:preflight('uneven')),(86,lambda:recover(False)),(90,lambda:complete('uneven',4,False)),(92,evac_check),(92.5,walk_after_recovery),(95,walked),(96,drive),(102,driven),(102.2,brake),(106,park),(113,approach_passenger),(114,aim_passenger),(114.5,enter_passenger),(116.5,lambda:check('normal_passenger_seat_reentry',occupants())),(118,enter_interior),(120,restored_interior),(121,drive),(122,walk_inside),(125,interior_walking),(126.5,turn),(129,turning_interior),(131,finish)])
events.sort(key=lambda e:e[0])
def tick(dt):
 global frames,maximum_speed
 frames+=1
 try:
  for k,(deadline,frame) in list(held.items()):
   if time.time()>=deadline and frames>=frame:unreal.RVInteriorMotorhome.dispatch_development_key(pc,k,False);del held[k]
  if events and time.time()-start>=events[0][0] and not held:
   _,fn=events.pop(0);fn()
  if time.time()-start>94:maximum_speed=max(maximum_speed,v.get_velocity().length())
  samples.append({'t':time.time()-start,'ready':r.get_editor_property('bConfirmedOverturned'),'revision':r.get_editor_property('RecoveryRevision'),'roll':v.get_actor_rotation().roll,'speed':v.get_velocity().length()})
 except Exception as e:check('harness_exception',False,repr(e));finish()
h=unreal.register_slate_post_tick_callback(tick)


