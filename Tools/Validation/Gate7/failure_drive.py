"""Actual throttle creates thermal engine failure, then normal timed service recovers.
Only initial fault, test time scale, supplies and isolated approaches are fixtures.
"""
import unreal,time,json
from pathlib import Path
B=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate7Validation')
w=next(a for a in unreal.ObjectIterator(unreal.World) if a.get_name()=='Gate7MechanicalTest' and 'UEDPIE_' in a.get_path_name())
pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn();v=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVMechanicalMotorhome)[0];c=v.get_editor_property('CoolingSystem');point=v.get_editor_property('EngineService');inv=p.get_component_by_class(unreal.RVInventoryComponent)
events=[];rows=[];samples=[];start=time.time();held={};initial_temperature=0
def check(n,ok,d=''):rows.append({'case':n,'pass':bool(ok),'detail':str(d)});unreal.log('GATE7_FAILURE_DRIVE '+json.dumps(rows[-1]))
def key(k,d=.2):unreal.RVInteriorMotorhome.dispatch_development_key(pc,k,True);held[k]=time.time()+d
def aim(a):pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p.get_actor_location()+unreal.Vector(0,0,64),a.get_actor_location()))
def driver_entry():return next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVVehicleEntryPoint) if a.get_editor_property('Seat').get_editor_property('bDriverSeat') and abs(v.get_actor_transform().inverse_transform_location(a.get_actor_location()).y)>100)
def setup():
 unreal.SystemLibrary.execute_console_command(pc,'t.MaxFPS 60',pc);c.debug_set_time_scale(50);c.debug_set_state(.2,.5,100,1)
 for cat in ['MechanicTools','EngineService','RadiatorReplacement','CoolantFull']:
  r=unreal.RVItemInstance();r.set_editor_property('Id',unreal.GuidLibrary.new_guid());r.set_editor_property('Definition',unreal.load_asset('/Game/Mechanical/DA_'+cat));r.set_editor_property('Condition',.83);inv.add_authority(r)
 approach_driver()
def approach_driver():p.set_actor_location(v.get_actor_transform().transform_location(unreal.Vector(190,-290,100)),False,True)
def drive_fault():
 global initial_temperature
 check('normal_E_faulty_driver',pc.get_controlled_pawn()==v);initial_temperature=c.get_editor_property('Cooling').temperature_c;key('W',13)
def failed():
 engine=c.get_editor_property('Engine');cool=c.get_editor_property('Cooling')
 check('actual_W_caused_overheat_then_damage_shutdown',engine.get_editor_property('bShutdown') and engine.condition<=.101 and engine.output_scale==0 and cool.coolant_litres==0,{'condition':engine.condition,'temperature':cool.temperature_c,'initial_c':initial_temperature})
 check('causal_trace_crossed_critical',max(s['temperature'] for s in samples)>130 and any(s['engine']<.75 and not s['shutdown'] for s in samples))
 key('S',4)
def parked():check('braked_shutdown_vehicle_stopped',v.get_velocity().length()<10,v.get_velocity().length());check('natural_cooldown_safe_for_service',c.get_editor_property('Cooling').temperature_c<=60,c.get_editor_property('Cooling').temperature_c);key('E',.85)
def approach_service():check('normal_E_exit_after_causal_failure',pc.get_controlled_pawn()==p);p.set_actor_location(v.get_actor_transform().transform_location(unreal.Vector(550,0,100)),False,True)
def recovered_engine():check('normal_timed_M_restores_recoverable_engine',c.get_editor_property('Engine').condition>=.649 and not c.get_editor_property('Engine').get_editor_property('bShutdown'))
def recovered_radiator():check('normal_timed_N_restores_radiator',c.get_editor_property('Cooling').radiator_condition==1 and c.get_editor_property('Cooling').leak_litres_per_second==0);key('I')
def refilled():check('normal_inventory_F_adds_owned_coolant',abs(c.get_editor_property('Cooling').coolant_litres-5)<1e-8 and next(i for i in inv.get_items() if str(i.definition.get_editor_property('CatalogId'))=='CoolantFull').fuel_litres==0);key('I');c.debug_set_time_scale(1)
def continued():check('actual_E_W_resume_after_causal_failure',pc.get_controlled_pawn()==v and v.get_velocity().length()>100 and not c.get_editor_property('Engine').get_editor_property('bShutdown'),v.get_velocity().length());finish()
def finish():
 for k in held:unreal.RVInteriorMotorhome.dispatch_development_key(pc,k,False)
 unreal.unregister_slate_post_tick_callback(h);(B/'failure-drive.json').write_text(json.dumps({'results':rows,'samples':samples},indent=2),encoding='utf-8')
for t,fn in [(0,setup),(1,lambda:aim(driver_entry())),(1.5,lambda:key('E',.85)),(3,drive_fault),(17,failed),(21.5,lambda:key('SpaceBar',12)),(36,parked),(37.5,approach_service),(39,lambda:aim(point)),(39.5,lambda:key('E',.85)),(41,lambda:key('P')),(41.5,lambda:key('M')),(62.5,recovered_engine),(63,lambda:key('N')),(79,recovered_radiator),(79.5,lambda:key('Down')),(80,lambda:key('F')),(81,refilled),(81.5,lambda:key('P')),(82.5,approach_driver),(84,lambda:aim(driver_entry())),(84.5,lambda:key('E',.85)),(86,lambda:key('W',2)),(89,continued)]:events.append((t,fn))
def tick(dt):
 try:
  now=time.time()
  for k,deadline in list(held.items()):
   if now>deadline:unreal.RVInteriorMotorhome.dispatch_development_key(pc,k,False);del held[k]
  if events and now-start>=events[0][0]:_,fn=events.pop(0);fn()
  s=c.get_editor_property('Cooling');e=c.get_editor_property('Engine');samples.append({'t':now-start,'temperature':s.temperature_c,'engine':e.condition,'shutdown':e.get_editor_property('bShutdown'),'coolant':s.coolant_litres,'speed':v.get_velocity().length()})
 except Exception as e:check('harness_exception',False,repr(e));finish()
h=unreal.register_slate_post_tick_callback(tick)
