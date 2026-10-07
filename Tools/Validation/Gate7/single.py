import unreal,json,time,math
from pathlib import Path
B=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate7Validation')
w=next(a for a in unreal.ObjectIterator(unreal.World) if a.get_name()=='Gate7MechanicalTest' and 'UEDPIE_' in a.get_path_name())
pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn()
v=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVMechanicalMotorhome)[0]
c=v.get_editor_property('CoolingSystem');point=v.get_editor_property('EngineService');inv=p.get_component_by_class(unreal.RVInventoryComponent)
results=[];events=[];start=time.time();held=None;done=False
def check(name,value,detail=''):
 results.append({'case':name,'pass':bool(value),'detail':str(detail)});unreal.log('GATE7 '+name+' '+str(bool(value)))
def cooling(field):return c.get_editor_property('Cooling').get_editor_property(field)
def engine(field):return c.get_editor_property('Engine').get_editor_property(field)
def reset(r=1,l=12,t=20,e=1):assert c.debug_set_state(r,l,t,e)
def advance(s,run=True,load=1,speed=2682.24):assert c.debug_advance(s,run,load,speed)
def inventory(cat):return next(i for i in inv.get_items() if str(i.definition.get_editor_property('CatalogId'))==cat)
def count(cat):return sum(i.quantity for i in inv.get_items() if str(i.definition.get_editor_property('CatalogId'))==cat)
def seed(cat,quantity=1):
 item=unreal.RVItemInstance();item.set_editor_property('Id',unreal.GuidLibrary.new_guid());item.set_editor_property('Definition',unreal.load_asset('/Game/Mechanical/DA_'+cat));item.set_editor_property('Quantity',quantity);item.set_editor_property('Condition',.83)
 result=inv.add_authority(item)
 # Python struct-wrapper identity is not the native GUID value comparison.
 key=lambda guid:tuple(guid.get_editor_property(f) for f in ['A','B','C','D'])
 assert any(key(i.id)==key(item.id) for i in inv.get_items()),str(result)
 return item.id
def press(key,seconds=.2):
 global held
 if held:unreal.RVInteriorMotorhome.dispatch_development_key(pc,held[0],False)
 unreal.RVInteriorMotorhome.dispatch_development_key(pc,key,True);held=(key,time.time()+seconds)
def request(action,item=None,revision=None):
 pc.request_service(action,point.get_editor_property('Revision') if revision is None else revision,item.id if item else unreal.Guid(),item.fuel_revision if item else -1)
def model():
 check('normal_scale_separate',c.debug_set_time_scale(0));reset();advance(3600)
 check('normal_hour_full_load_stable',cooling('TemperatureC')<c.get_editor_property('Tuning').overheat_c,cooling('TemperatureC'))
 check('normal_no_leak_or_engine_damage',cooling('CoolantLitres')==12 and engine('Condition')==1)
 reset(.7);advance(100,False);minor=cooling('CoolantLitres');check('minor_leak_exact',abs(minor-11.9)<1e-8,minor)
 reset(.2);advance(100,False);major=cooling('CoolantLitres');check('major_leak_faster_exact',abs(major-10.5)<1e-8 and major<minor,major)
 reset();advance(300);normal=cooling('TemperatureC');reset(.2);advance(300);check('damaged_radiator_hotter',cooling('TemperatureC')>normal,(normal,cooling('TemperatureC')))
 reset(1,1);advance(300);check('low_coolant_heat_risk',cooling('TemperatureC')>normal,cooling('TemperatureC'))
 reset();advance(300,True,0,0);idle=cooling('TemperatureC');reset();advance(300,True,1,0);loaded=cooling('TemperatureC');check('load_adds_heat',loaded>idle,(idle,loaded))
 reset();advance(300,True,1,2682.24);check('airflow_reduces_heat',cooling('TemperatureC')<loaded,cooling('TemperatureC'))
 reset(.2,0,150);advance(300,False);check('shutdown_cools_no_load_damage',cooling('TemperatureC')<150 and engine('Condition')==1)
 for temp,label in [(20,'NORMAL'),(96,'WARM'),(106,'HOT'),(116,'OVERHEATING'),(131,'CRITICAL')]:
  reset(1,12,temp);check('threshold_'+label,label in str(cooling('Status')))
 reset(.1,0,180);advance(2000);check('prolonged_overheat_engine_shutdown',engine('Condition')<=.1 and engine('bShutdown') and engine('OutputScale')==0,(engine('Condition'),cooling('TemperatureC')))
 check('coolant_temperature_engine_bounded',0<=cooling('CoolantLitres')<=12 and 20<=cooling('TemperatureC')<=200 and 0<=engine('Condition')<=1)
 before=engine('Condition');advance(1000);check('shutdown_stops_combustion_damage',engine('Condition')==before)
 reset(-10,-100,-100,-10);check('lower_clamps',cooling('RadiatorCondition')==0 and cooling('CoolantLitres')==0 and cooling('TemperatureC')==20 and engine('Condition')==0)
 reset(10,100,1000,10);check('upper_clamps',cooling('RadiatorCondition')==1 and cooling('CoolantLitres')==12 and cooling('TemperatureC')==200 and engine('Condition')==1)
 check('nan_rejected',not c.debug_set_state(float('nan'),12,20,1) and not c.debug_set_time_scale(float('nan')))
 reset(.2,0,20);advance(86400,False);check('day_equivalent_bounded',cooling('CoolantLitres')==0 and cooling('TemperatureC')==20 and engine('Condition')==1)
 reset(.7,9,20)
 # Only initial service approach is a placement fixture; E/B/N/M/F paths below
 # invoke real gameplay intent. No direct repair-completion call.
 p.set_actor_location(v.get_actor_transform().transform_location(unreal.Vector(550,0,100)),False,True)
 pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p.get_actor_location()+unreal.Vector(0,0,64),point.get_actor_location()))
def initial_e():
 pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p.get_actor_location()+unreal.Vector(0,0,64),point.get_actor_location()));press('E',.85)
def panel_check():check('normal_E_opens_service',pc.get_editor_property('MechanicalPoint')==point);press('P')
def hood_check():check('normal_P_hood_open',bool(v.get_editor_property('EngineHood').get_editor_property('bOpen')));press('B')
def missing_check():check('repair_without_tool_rejected',not point.get_editor_property('RepairPlayer') and count('RadiatorPatch')==0,pc.get_editor_property('MechanicalFeedback'));seed('MechanicTools');seed('RadiatorPatch',3);press('B')
def start_check():check('normal_B_starts_authority_timer',point.get_editor_property('RepairPlayer')==pc.player_state and count('RadiatorPatch')==3);press('Escape')
def cancel_check():check('normal_Escape_cancels_without_consumption',not point.get_editor_property('RepairPlayer') and count('RadiatorPatch')==3);initial_e()
def restart_patch():press('B')
def patch_done():
 check('temporary_repair_consumes_once_retains_tool',count('RadiatorPatch')==2 and count('MechanicTools')==1)
 check('temporary_patch_reduces_leak',cooling('bTemporaryPatch') and cooling('PatchLeakMultiplier')==.15 and cooling('RadiatorCondition')<1)
 reset(.7,9,20);seed('CoolantFull');request('Refill',inventory('CoolantFull'))
def refill_done():
 i=inventory('CoolantFull');check('exact_partial_refill',abs(i.fuel_litres-2)<1e-8 and cooling('CoolantLitres')==12,i.fuel_litres)
 check('empty_hardware_guid_condition_retained',i.condition>.82 and unreal.GuidLibrary.is_valid_guid(i.id))
 request('Refill',i)
def full_rejected():
 check('full_system_no_item_loss',inventory('CoolantFull').fuel_litres==2)
 reset(.2,10,20);seed('RadiatorReplacement');press('N')
def replacement_done():
 check('full_replacement_consumed_once',count('RadiatorReplacement')==0)
 check('full_radiator_repair',cooling('RadiatorCondition')==1 and not cooling('bTemporaryPatch') and cooling('LeakLitresPerSecond')==0)
 reset(.2,10,20,.05);seed('EngineService');press('M')
def engine_done():
 check('engine_service_recoverable_restart',engine('Condition')>=.649 and not engine('bShutdown') and count('EngineService')==0)
 check('engine_service_not_radiator_repair',cooling('RadiatorCondition')<.3)
 reset(.7,10,20);press('B')
def leave_range():
 check('repair_started_before_range_cancel',bool(point.get_editor_property('RepairPlayer')));pc.set_control_rotation(unreal.Rotator(yaw=v.get_actor_rotation().yaw));press('W',.9)
def canceled_range():check('range_cancel_no_late_completion',not point.get_editor_property('RepairPlayer') and count('RadiatorPatch')==2)
def finish():
 global done
 done=True
 if held:unreal.RVInteriorMotorhome.dispatch_development_key(pc,held[0],False)
 unreal.unregister_slate_post_tick_callback(h)
 (B/'single.json').write_text(json.dumps({'results':results},indent=2),encoding='utf-8')
for t,fn in [(0,model),(1,initial_e),(2.3,panel_check),(2.7,hood_check),(3.5,missing_check),(4.5,start_check),(5.3,cancel_check),(6.5,restart_patch),(15.5,patch_done),(16.5,refill_done),(17.5,full_rejected),(33.5,replacement_done),(54.5,engine_done),(55.5,leave_range),(64.5,canceled_range),(65.5,finish)]:events.append((t,fn))
def tick(dt):
 global held
 try:
  if held and time.time()>held[1]:unreal.RVInteriorMotorhome.dispatch_development_key(pc,held[0],False);held=None
  if events and time.time()-start>=events[0][0]:
   _,fn=events.pop(0);fn()
 except Exception as e:check('harness_exception',False,repr(e));finish()
h=unreal.register_slate_post_tick_callback(tick)
