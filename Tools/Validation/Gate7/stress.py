"""Meaningful serial authority stress: fluid conservation, timer cancellation,
stack exhaustion, repair commits and heat/cool bounds. Development profile only.
"""
import unreal,json,time
from pathlib import Path
B=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate7Validation')
w=next(a for a in unreal.ObjectIterator(unreal.World) if a.get_name()=='Gate7MechanicalTest' and 'UEDPIE_' in a.get_path_name())
pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn();v=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVMechanicalMotorhome)[0];c=v.get_editor_property('CoolingSystem');point=v.get_editor_property('EngineService');inv=p.get_component_by_class(unreal.RVInventoryComponent)
results=[];phase='prepare';deadline=0;start=time.time();cycles=0;held=None;normal_profile=c.get_editor_property('Profile');drop_index=0;drop_expected=None
def check(n,ok,d=''):results.append({'case':n,'pass':bool(ok),'detail':str(d)})
def cool(f):return c.get_editor_property('Cooling').get_editor_property(f)
def item(cat):return next(i for i in inv.get_items() if str(i.definition.get_editor_property('CatalogId'))==cat)
def qty(cat):return sum(i.quantity for i in inv.get_items() if str(i.definition.get_editor_property('CatalogId'))==cat)
def key(k,s=.2):
 global held
 unreal.RVInteriorMotorhome.dispatch_development_key(pc,k,True);held=(k,time.time()+s)
def seed(cat,q=1):
 r=unreal.RVItemInstance();r.set_editor_property('Id',unreal.GuidLibrary.new_guid());r.set_editor_property('Definition',unreal.load_asset('/Game/Mechanical/DA_'+cat));r.set_editor_property('Quantity',q);r.set_editor_property('Condition',.83);inv.add_authority(r)
def request(a,i=None,revision=None):pc.request_service(a,point.get_editor_property('Revision'),i.id if i else unreal.Guid(),i.fuel_revision if i and revision is None else revision if revision is not None else -1)
def finish():
 c.set_editor_property('Profile',normal_profile)
 if held:unreal.RVInteriorMotorhome.dispatch_development_key(pc,held[0],False)
 unreal.unregister_slate_post_tick_callback(h);(B/'stress.json').write_text(json.dumps({'results':results,'elapsed_seconds':time.time()-start},indent=2),encoding='utf-8')
def tick(dt):
 global phase,deadline,cycles,held,drop_index,drop_expected
 try:
  now=time.time()
  if held and now>held[1]:unreal.RVInteriorMotorhome.dispatch_development_key(pc,held[0],False);held=None
  if now<deadline:return
  if phase=='prepare':
   unreal.SystemLibrary.execute_console_command(pc,'t.MaxFPS 60',pc);c.debug_set_time_scale(0);c.debug_set_state(.2,12,20,1)
   # Test-only logistics capacity permits 100 repair consumables; normal player
   # capacity remains25kg/35L and is separately regression tested.
   inv.set_editor_property('MaxWeightKg',1000);inv.set_editor_property('MaxVolumeLitres',2000)
   seed('MechanicTools');seed('CoolantFull')
   for _ in range(10):seed('RadiatorPatch',10)
   p.set_actor_location(v.get_actor_transform().transform_location(unreal.Vector(550,0,100)),False,True);deadline=now+1;phase='inspect'
  elif phase=='inspect':
   pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p.get_actor_location()+unreal.Vector(0,0,64),point.get_actor_location()));deadline=now+.5;phase='press_inspect'
  elif phase=='press_inspect':key('E',.85);deadline=now+1.1;phase='open'
  elif phase=='open':
   check('normal_E_stress_service',pc.get_editor_property('MechanicalPoint')==point);key('P');deadline=now+.5;phase='fluid_reset'
  elif phase=='fluid_reset':
   c.debug_set_state(1,11.99,20,1);request('Refill',item('CoolantFull'));deadline=now+.12;phase='fluid_check'
  elif phase=='fluid_check':
   cycles+=1
   if abs(cool('CoolantLitres')-12)>1e-8:raise AssertionError('fluid cycle '+str(cycles))
   if cycles<100:phase='fluid_reset'
   else:
    check('100_exact_fluid_transfers_conserve_litres',abs(item('CoolantFull').fuel_litres-4)<1e-8 and item('CoolantFull').fuel_revision==100,item('CoolantFull').fuel_litres)
    seed('CoolantPartial');seed('CoolantEmpty');phase='drop_start'
  elif phase=='drop_start':
   cat=['CoolantFull','CoolantPartial','CoolantEmpty'][drop_index];i=item(cat)
   drop_expected=(cat,unreal.GuidLibrary.conv_guid_to_string(i.id),i.fuel_litres,i.fuel_revision,i.condition)
   inv.request_drop(i.id,1);deadline=now+.4;phase='drop_aim'
  elif phase=='drop_aim':
   cat,guid,litres,revision,condition=drop_expected
   pickup=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVWorldItem) if unreal.GuidLibrary.conv_guid_to_string(a.get_editor_property('Item').id)==guid)
   i=pickup.get_editor_property('Item');check(cat+'_drop_preserves_guid_fluid_revision_condition',qty(cat)==0 and i.fuel_litres==litres and i.fuel_revision==revision and i.condition==condition)
   pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p.get_actor_location()+unreal.Vector(0,0,64),pickup.get_actor_location()));deadline=now+.3;phase='drop_pick'
  elif phase=='drop_pick':key('E',.85);deadline=now+1.2;phase='drop_check'
  elif phase=='drop_check':
   cat,guid,litres,revision,condition=drop_expected;i=item(cat)
   check(cat+'_normal_E_repick_preserves_state',unreal.GuidLibrary.conv_guid_to_string(i.id)==guid and i.fuel_litres==litres and i.fuel_revision==revision and i.condition==condition)
   drop_index+=1
   if drop_index<3:phase='drop_start'
   else:c.debug_set_state(.2,12,20,1);cycles=0;phase='cancel_start'
  elif phase=='cancel_start':request('Patch');deadline=now+.12;phase='cancel'
  elif phase=='cancel':
   if not point.get_editor_property('RepairPlayer'):raise AssertionError('reservation not started')
   request('Cancel');deadline=now+.12;phase='cancel_check'
  elif phase=='cancel_check':
   if point.get_editor_property('RepairPlayer'):raise AssertionError('reservation not canceled')
   cycles+=1
   if cycles<100:phase='cancel_start'
   else:check('100_cancels_preserve_all_parts_tools',qty('RadiatorPatch')==100 and qty('MechanicTools')==1);deadline=now+9;phase='no_late'
  elif phase=='no_late':
   check('canceled_timers_no_late_completions',qty('RadiatorPatch')==100 and not point.get_editor_property('RepairPlayer'))
   c.set_editor_property('Profile',unreal.load_asset('/Game/Development/Mechanical/DA_AcceleratedMechanical'));cycles=0;phase='repair_start'
  elif phase=='repair_start':c.debug_set_state(.2,12,20,1);request('Patch');deadline=now+.6;phase='repair_check'
  elif phase=='repair_check':
   cycles+=1
   if qty('RadiatorPatch')!=100-cycles or point.get_editor_property('RepairPlayer') or not cool('bTemporaryPatch'):raise AssertionError('repair cycle '+str(cycles))
   if cycles<100:phase='repair_start'
   else:
    check('100_repair_completions_consume_exact_parts',qty('RadiatorPatch')==0 and qty('MechanicTools')==1)
    c.debug_set_state(.2,12,20,1);request('Patch');deadline=now+.5;phase='exhausted'
  elif phase=='exhausted':
   check('last_stack_removed_no_negative_no_free_repair',qty('RadiatorPatch')==0 and not point.get_editor_property('RepairPlayer') and not cool('bTemporaryPatch'))
   # Acceleration exercises the actual subsystem integrator and causal shutdown,
   # not thousands of tautological value assignments counted as tests.
   worst=0;valid=True
   for _ in range(100):
    c.debug_set_state(.15,.2,120,1);c.debug_advance(1800,True,1,2682.24)
    e=c.get_editor_property('Engine');s=c.get_editor_property('Cooling');worst=max(worst,s.temperature_c)
    valid=valid and 0<=s.coolant_litres<=12 and 20<=s.temperature_c<=200 and 0<=e.condition<=1 and e.get_editor_property('bShutdown')
    c.debug_advance(1800,False,0,0);valid=valid and cool('TemperatureC')<60
   check('100_heat_shutdown_cool_cycles_bounded',valid,{'maximum_c':worst})
   c.debug_set_state(1,12,20,.05);key('P');deadline=now+.5;phase='shutdown_approach'
  elif phase=='shutdown_approach':
   p.set_actor_location(v.get_actor_transform().transform_location(unreal.Vector(190,-290,100)),False,True);deadline=now+1;phase='driver_aim'
  elif phase=='driver_aim':
   entry=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVVehicleEntryPoint) if a.get_editor_property('Seat').get_editor_property('bDriverSeat') and abs(v.get_actor_transform().inverse_transform_location(a.get_actor_location()).y)>100)
   pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p.get_actor_location()+unreal.Vector(0,0,64),entry.get_actor_location()));deadline=now+.3;phase='driver_enter'
  elif phase=='driver_enter':key('E',.85);deadline=now+1.3;phase='shutdown_drive'
  elif phase=='shutdown_drive':
   check('actual_E_driver_before_shutdown_input',pc.get_controlled_pawn()==v and not v.get_editor_property('EngineHood').get_editor_property('bOpen'));key('W',2);deadline=now+2.5;phase='shutdown_check'
  elif phase=='shutdown_check':
   check('actual_W_shutdown_prevents_propulsion',v.get_velocity().length()<10 and c.get_editor_property('Engine').output_scale==0 and not v.get_editor_property('Electrical').get_editor_property('bEngineRunning'),v.get_velocity().length());key('E',.85);deadline=now+1.3;phase='engine_approach'
  elif phase=='engine_approach':
   check('actual_E_exit_after_shutdown',pc.get_controlled_pawn()==p)
   seed('EngineService');p.set_actor_location(v.get_actor_transform().transform_location(unreal.Vector(550,0,100)),False,True);deadline=now+1;phase='engine_aim'
  elif phase=='engine_aim':
   pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p.get_actor_location()+unreal.Vector(0,0,64),point.get_actor_location()));deadline=now+.3;phase='engine_inspect'
  elif phase=='engine_inspect':key('E',.85);deadline=now+1.3;phase='engine_hood'
  elif phase=='engine_hood':key('P');deadline=now+.4;phase='engine_repair'
  elif phase=='engine_repair':key('M');deadline=now+.8;phase='engine_repaired'
  elif phase=='engine_repaired':
   check('actual_M_recovers_shutdown',c.get_editor_property('Engine').condition>=.649 and not c.get_editor_property('Engine').get_editor_property('bShutdown') and qty('EngineService')==0);key('P');deadline=now+.4;phase='recovered_approach'
  elif phase=='recovered_approach':
   p.set_actor_location(v.get_actor_transform().transform_location(unreal.Vector(190,-290,100)),False,True);deadline=now+1;phase='recovered_aim'
  elif phase=='recovered_aim':
   entry=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVVehicleEntryPoint) if a.get_editor_property('Seat').get_editor_property('bDriverSeat') and abs(v.get_actor_transform().inverse_transform_location(a.get_actor_location()).y)>100)
   pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p.get_actor_location()+unreal.Vector(0,0,64),entry.get_actor_location()));deadline=now+.3;phase='recovered_enter'
  elif phase=='recovered_enter':key('E',.85);deadline=now+1.3;phase='recovered_drive'
  elif phase=='recovered_drive':key('W',2);deadline=now+2.5;phase='recovered_check'
  elif phase=='recovered_check':
   check('actual_W_after_repair_restores_traction',pc.get_controlled_pawn()==v and v.get_velocity().length()>100 and v.get_editor_property('Electrical').get_editor_property('bEngineRunning'),v.get_velocity().length());finish();phase='done'
  if now-start>240:raise TimeoutError('stress timed out')
 except Exception as e:check('harness_exception',False,repr(e));finish();phase='done'
h=unreal.register_slate_post_tick_callback(tick)
