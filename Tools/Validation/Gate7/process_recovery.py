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
events=[];held={};results=[];samples=[];before=None;resources=None;frames=0;maximum_speed=0
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
  needs.append((str(player_state.get_player_name()),state.nutrition,state.hydration,state.fatigue))
 cooling=v.get_editor_property('CoolingSystem').get_editor_property('Cooling')
 engine=v.get_editor_property('CoolingSystem').get_editor_property('Engine')
 return {'items':sorted(items),'needs':sorted(needs),'mechanical':(cooling.radiator_condition,cooling.coolant_litres,cooling.temperature_c,engine.condition),'resources':[v.get_editor_property('PropulsionFuel').get_editor_property('Litres'),v.get_editor_property('GeneratorFuel').get_editor_property('Litres'),v.get_editor_property('HouseBattery').get_editor_property('EnergyWh'),v.get_editor_property('ChassisBattery').get_editor_property('EnergyWh')]}
def setup():
 unreal.SystemLibrary.execute_console_command(pc,'t.MaxFPS 60',pc)
 unreal.SystemLibrary.execute_console_command(pc,'rv.Needs.AllowDebug 1',pc)
 if not authority:return
 v.get_editor_property('CoolingSystem').debug_set_time_scale(0)
 v.get_editor_property('Electrical').debug_set_time_scale(0)
 for c,entry,side in [(dp,de,-1),(wp,pe,1)]:
  c.get_editor_property('PlayerState').get_component_by_class(unreal.RVNeedsComponent).debug_set_time_scale(0)
  q=v.get_actor_transform().inverse_transform_location(entry.get_actor_location())
  c.set_actor_location(v.get_actor_transform().transform_location(unreal.Vector(q.x,q.y+side*125,100)),False,True)
  i=unreal.RVItemInstance();i.set_editor_property('Id',unreal.GuidLibrary.new_guid());i.set_editor_property('Definition',unreal.load_asset('/Game/Items/DA_Food'));i.set_editor_property('Quantity',3);i.set_editor_property('Condition',.73)
  c.get_component_by_class(unreal.RVInventoryComponent).add_authority(i)
def aim():
 target=de if isdriver else pe
 pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p.get_actor_location()+unreal.Vector(0,0,p.get_editor_property('BaseEyeHeight')),target.get_actor_location()))
def occupants():return driver.get_editor_property('Occupant')==dp and passenger.get_editor_property('Occupant')==wp
def fixture(roll,uneven=False):
 if not authority:return
 if uneven:
  transform=unreal.Transform(location=unreal.Vector(6000,6000,20),rotation=unreal.Rotator(pitch=2,roll=1),scale=unreal.Vector(20,20,.2))
  ramp=unreal.GameplayStatics.begin_deferred_actor_spawn_from_class(w,unreal.StaticMeshActor,transform,unreal.SpawnActorCollisionHandlingMethod.ALWAYS_SPAWN,None)
  ramp.static_mesh_component.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Cube'));ramp.static_mesh_component.set_collision_profile_name('BlockAll')
  unreal.GameplayStatics.finish_spawning_actor(ramp,transform)
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
 check(label+'_state_conserved',snapshot()==resources)
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
def driven():check('driving_after_recovery',maximum_speed>200,maximum_speed)
def finish():
 for key in list(held):unreal.RVInteriorMotorhome.dispatch_development_key(pc,key,False)
 unreal.unregister_slate_post_tick_callback(h)
 (B/(config['name']+'_'+role+'.json')).write_text(json.dumps({'pid':os.getpid(),'role':role,'config':config,'results':results,'samples':samples},indent=2),encoding='utf-8')
events=[(0,setup),(1,aim),(1.3,lambda:press('E',.85)),(4,lambda:check('normal_E_two_seats',occupants()))]
for i,roll in enumerate([90,-90,180]):
 t=8+i*20;label=str(roll);revision=i+1
 events.extend([(t,lambda roll=roll:fixture(roll)),(t+11,lambda label=label:preflight(label)),(t+12,lambda host=i!=1:recover(host)),(t+16,lambda label=label,rev=revision:complete(label,rev)),(t+17,lambda:press('F8')),(t+19,lambda rev=revision:reject_repeat(rev))])
events.extend([(69,stand),(72,standing_check),(74,lambda:fixture(90,True)),(85,lambda:preflight('uneven')),(86,lambda:recover(False)),(90,lambda:complete('uneven',4,False)),(92,evac_check),(94,drive),(100,driven),(102,finish)])
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
