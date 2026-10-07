"""Paired authority/contention and normal-input roadside service plus driving."""
import unreal,json,time,os,math
from pathlib import Path
B=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate7Validation')
session=json.loads((B/'session.json').read_text());config=session['config'];start=session['start']
w=next(a for a in unreal.ObjectIterator(unreal.World) if a.get_name()=='Gate7MechanicalTest' and unreal.GameplayStatics.get_player_controller(a,0) and unreal.GameplayStatics.get_player_controller(a,0).get_controlled_pawn())
authority=unreal.GameplayStatics.get_game_mode(w) is not None;role='server' if authority else 'client'
pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn()
v=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVMechanicalMotorhome)[0];c=v.get_editor_property('CoolingSystem');point=v.get_editor_property('EngineService')
inv=p.get_component_by_class(unreal.RVInventoryComponent);results=[];samples=[];events=[];held={};frames=0;route=None

def stop_route():
 global route
 if route:unreal.RVInteriorMotorhome.dispatch_development_key(pc,'W',False)
 route=None

def walk_route(points):
 global route
 if not isdriver():return
 stop_route();route={'points':list(points),'until':time.time()+5}
 unreal.RVInteriorMotorhome.dispatch_development_key(pc,'W',True)

def steer_route():
 global route
 if not route:return
 q=v.get_actor_transform().inverse_transform_location(p.get_actor_location());x,y=route['points'][0]
 if math.hypot(x-q.x,y-q.y)<9:
  route['points'].pop(0)
  if not route['points']:stop_route();return
  x,y=route['points'][0]
 if time.time()>route['until']:raise RuntimeError('Physical roadside walking waypoint timed out')
 pc.set_control_rotation(unreal.Rotator(yaw=v.get_actor_rotation().yaw+math.degrees(math.atan2(y-q.y,x-q.x))))
def other():return next(x for x in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSurvivorCharacter) if x!=p and x.get_editor_property('PlayerState'))
def cooling(f):return c.get_editor_property('Cooling').get_editor_property(f)
def engine(f):return c.get_editor_property('Engine').get_editor_property(f)
def check(n,value,d=''):results.append({'case':n,'pass':bool(value),'detail':str(d)});unreal.log('GATE7_NET '+role+' '+n+' '+str(bool(value)))
def item(cat):return next(i for i in inv.get_items() if str(i.definition.get_editor_property('CatalogId'))==cat)
def count(cat,inventory=None):return sum(i.quantity for i in (inventory or inv).get_items() if str(i.definition.get_editor_property('CatalogId'))==cat)
def fluids():return sum(i.fuel_litres for q in [inv,other().get_component_by_class(unreal.RVInventoryComponent)] for i in q.get_items() if i.definition and str(i.definition.get_editor_property('CatalogId'))=='CoolantFull')
def press(key,seconds=.2):
 if key in held:unreal.RVInteriorMotorhome.dispatch_development_key(pc,key,False)
 unreal.RVInteriorMotorhome.dispatch_development_key(pc,key,True);held[key]=(time.time()+seconds,frames+3)
def aim(a):
 stop_route()
 pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(pc.get_controlled_pawn().get_actor_location()+unreal.Vector(0,0,p.get_editor_property('BaseEyeHeight')),a.get_actor_location()))
def request(action,i=None,revision=None):pc.request_service(action,point.get_editor_property('Revision') if revision is None else revision,i.id if i else unreal.Guid(),i.fuel_revision if i else -1)
def setup():
 for command in ['t.MaxFPS 60','t.IdleWhenNotForeground 0']:
  unreal.SystemLibrary.execute_console_command(pc,command,pc)
 if authority:
  c.debug_set_time_scale(0);c.debug_set_state(.2,9,20,1)
  for index,pawn in enumerate([p,other()]):
   pawn.set_actor_location(v.get_actor_transform().transform_location(unreal.Vector(550,-75 if index==0 else 75,100)),False,True)
   target=pawn.get_component_by_class(unreal.RVInventoryComponent)
   for cat,qty in [('MechanicTools',1),('RadiatorPatch',3),('RadiatorReplacement',1),('EngineService',1),('CoolantFull',1)]:
    if index==1 and cat=='MechanicTools':continue
    record=unreal.RVItemInstance();record.set_editor_property('Id',unreal.GuidLibrary.new_guid());record.set_editor_property('Definition',unreal.load_asset('/Game/Mechanical/DA_'+cat));record.set_editor_property('Quantity',qty);record.set_editor_property('Condition',.83);target.add_authority(record)
def aim_service():aim(point)
def inspect():press('E',.85)
def panel():check('normal_E_diagnosis_authoritative',pc.get_editor_property('MechanicalPoint')==point and cooling('RadiatorCondition')<.3,{'point':str(pc.get_editor_property('MechanicalPoint')),'radiator':cooling('RadiatorCondition'),'location':str(p.get_actor_location()),'target':str(point.get_actor_location()),'prompt':str(p.get_component_by_class(unreal.RVInteractionComponent).get_prompt())})
def panel_photo():unreal.SystemLibrary.execute_console_command(pc,'shot filename='+str(B/(config['name']+'_'+role+'_service.png'))+' -nosuffix showui',pc)
def open_hood():
 if authority:press('P')
def hood_check():check('hood_open_replicates',bool(v.get_editor_property('EngineHood').get_editor_property('bOpen')))
def debug_guard():
 if not authority:
  before=(cooling('RadiatorCondition'),cooling('CoolantLitres'),cooling('TemperatureC'),engine('Condition'))
  check('client_debug_cannot_author_fault_clear_or_temperature',not c.debug_set_state(1,12,20,1) and not c.debug_advance(86400,True,1,0) and not c.debug_set_time_scale(100) and before==(cooling('RadiatorCondition'),cooling('CoolantLitres'),cooling('TemperatureC'),engine('Condition')))
def initial_attempt():
 if not authority:press('B')
def client_missing_check():
 if not authority:check('client_missing_tool_rejected',count('MechanicTools')==0 and 'Missing usable' in pc.get_editor_property('MechanicalFeedback'),pc.get_editor_property('MechanicalFeedback'))
def host_begin():
 if authority:press('B')
def reserved():
 check('one_authoritative_repair_reservation',bool(point.get_editor_property('RepairPlayer')) and str(point.get_editor_property('ActiveRepair'))=='Patch');check('start_does_not_consume',count('RadiatorPatch')==3)
def hostcancel():
 if authority:press('Escape')
def cancel_receipt():check('cancellation_converges_without_consumption',not point.get_editor_property('RepairPlayer') and count('RadiatorPatch')==3)
def give_client_tool():
 if authority:
  record=unreal.RVItemInstance();record.set_editor_property('Id',unreal.GuidLibrary.new_guid());record.set_editor_property('Definition',unreal.load_asset('/Game/Mechanical/DA_MechanicTools'));record.set_editor_property('Condition',.83);other().get_component_by_class(unreal.RVInventoryComponent).add_authority(record)
def clientpatch():
 if not authority:press('B')
def valid_contention():
 if authority:press('B')
def busy_check():
 if authority:check('valid_second_repair_rejected_no_consumption','already in progress' in pc.get_editor_property('MechanicalFeedback') and count('RadiatorPatch')==3,pc.get_editor_property('MechanicalFeedback'))
def wrong_owner_refill():
 foreign=next(i for i in other().get_component_by_class(unreal.RVInventoryComponent).get_items() if str(i.definition.get_editor_property('CatalogId'))=='CoolantFull');request('Refill',foreign)
def wrong_owner_check():check('foreign_guid_cannot_drain_coolant',fluids()==10 and cooling('CoolantLitres')==9,pc.get_editor_property('MechanicalFeedback'))
def patch_done():
 check('client_patch_replicates',cooling('bTemporaryPatch') and abs(cooling('PatchLeakMultiplier')-.15)<1e-8)
 check('only_client_patch_consumed',count('RadiatorPatch')==(3 if authority else 2) and count('MechanicTools')==1)
def concurrent_refill():
 i=item('CoolantFull');r=point.get_editor_property('Revision');request('Refill',i,r);request('Refill',i,r)
def refill_done():
 check('coolant_converges_capacity',abs(cooling('CoolantLitres')-12)<1e-8)
 check('duplicate_requests_conserve_fluid',abs(fluids()-7)<1e-8,fluids())
 check('fluid_guids_state_intact',item('CoolantFull').condition>.82 and item('CoolantFull').fuel_litres>=0)
def damage_again():
 if authority:c.debug_set_state(.2,12,20,1)
def replace():
 if authority:press('N')
def replace_done():
 check('host_full_repair_replicates',cooling('RadiatorCondition')==1 and not cooling('bTemporaryPatch') and cooling('LeakLitresPerSecond')==0)
 check('host_replacement_consumed_only_once',count('RadiatorReplacement')==(0 if authority else 1))
def force_shutdown():
 if authority:c.debug_set_state(.1,0,180,.05)
def shutdown():
 check('shutdown_warning_output_replicated',engine('bShutdown') and engine('OutputScale')==0 and 'CRITICAL' in str(cooling('Status')))
 if authority:c.debug_set_state(.1,12,20,.05)
def client_engine_repair():
 if not authority:press('M')
def engine_done():
 check('client_engine_service_restores_operation',engine('Condition')>=.649 and not engine('bShutdown') and count('EngineService')==(1 if authority else 0))
 check('engine_service_preserves_radiator_fault',cooling('RadiatorCondition')<.2)
 if not authority:press('N')
def radiator_done():check('client_radiator_replace_restores_cooling',cooling('RadiatorCondition')==1 and cooling('LeakLitresPerSecond')==0)
def arrange_drive():
 if authority:
  c.debug_set_state(1,12,70,1);c.debug_set_time_scale(1)
  driver=p if config['driver']=='host' else other();walker=other() if config['driver']=='host' else p
  entry=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVVehicleEntryPoint) if a.get_editor_property('Seat').get_editor_property('bDriverSeat') and abs(v.get_actor_transform().inverse_transform_location(a.get_actor_location()).y)>100)
  driver.set_actor_location(v.get_actor_transform().transform_location(unreal.Vector(190,-290,100)),False,True)
  walker.set_actor_location(v.get_actor_transform().transform_location(unreal.Vector(100,0,185)),False,True)
  stock=next(a.get_editor_property('Container') for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVExteriorStoragePoint) if str(a.get_editor_property('DoorPartName'))=='Art_RV_Van_Compartment_02')
  record=unreal.RVItemInstance();record.set_editor_property('Id',unreal.GuidLibrary.new_guid());record.set_editor_property('Definition',unreal.load_asset('/Game/Mechanical/DA_CoolantPartial'));record.set_editor_property('Condition',.61);stock.add_authority(record)
def close_hood():
 if authority:press('P')
def reset_frame():p.get_component_by_class(unreal.RVPassengerReferenceFrameComponent).reset_diagnostics()
def isdriver():return authority==(config['driver']=='host')
def aim_driver():
 if isdriver():
  entry=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVVehicleEntryPoint) if a.get_editor_property('Seat').get_editor_property('bDriverSeat') and abs(v.get_actor_transform().inverse_transform_location(a.get_actor_location()).y)>100);aim(entry)
def enter_driver():
 if isdriver():
  unreal.log('GATE7_DRIVER_ENTRY '+json.dumps({'location':str(p.get_actor_location()),'prompt':str(p.get_component_by_class(unreal.RVInteractionComponent).get_prompt()),'control_rotation':str(pc.get_control_rotation()),'feedback':str(pc.get_editor_property('SeatFeedback')),'hood_open':v.get_editor_property('EngineHood').get_editor_property('bOpen'),'movement_active':p.get_component_by_class(unreal.CharacterMovementComponent).is_active()}))
  press('E',.85)
def drive():
 if isdriver():check('normal_E_driver_possession',pc.get_controlled_pawn()==v,{'feedback':str(pc.get_editor_property('SeatFeedback')),'prompt':str(p.get_component_by_class(unreal.RVInteractionComponent).get_prompt())});press('W',18)
def minorfault():
 if authority:c.debug_set_state(.7,12,70,1);c.debug_set_time_scale(20)
def walk():
 if not isdriver():pc.set_control_rotation(unreal.Rotator(yaw=v.get_actor_rotation().yaw+180));press('W',.7)
def turn():
 if isdriver():press('A',.3)
def moving():
 check('actual_vehicle_moving_under_fault',v.get_velocity().length()>400,v.get_velocity().length())
 check('moving_coolant_leak_replicates',cooling('CoolantLitres')<12 and cooling('LeakLitresPerSecond')>0,cooling('CoolantLitres'))
 check('fault_causes_temperature_rise_under_actual_drive',cooling('TemperatureC')>71,cooling('TemperatureC'))
 if not isdriver():
  frame=p.get_component_by_class(unreal.RVPassengerReferenceFrameComponent);q=v.get_actor_transform().inverse_transform_location(p.get_actor_location());check('moving_passenger_frame_and_floor',frame.get_editor_property('ReferenceFrame')==v and q.z>140,q);check('moving_passenger_corrections_bounded',frame.get_editor_property('MaxCorrectionCm')<30,frame.get_editor_property('MaxCorrectionCm'))
def brake():
 if isdriver():press('W',.01);press('S',6)
def handbrake():
 if isdriver():press('SpaceBar',9)
def stopped():check('roadside_braking_stops',v.get_velocity().length()<150,v.get_velocity().length())
def exit_driver():
 if isdriver():press('E',.85)
def outside():
 if isdriver():
  check('roadside_normal_E_exit',pc.get_controlled_pawn()==p and p.get_component_by_class(unreal.CharacterMovementComponent).get_editor_property('MovementMode')==unreal.MovementMode.MOVE_WALKING)
  target=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVExteriorStoragePoint) if str(a.get_editor_property('DoorPartName'))=='Art_RV_Van_Compartment_02')
  q=v.get_actor_transform().inverse_transform_location(target.get_actor_location());walk_route([(q.x,-210)])
def aim_stock():
 if isdriver():
  target=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVExteriorStoragePoint) if str(a.get_editor_property('DoorPartName'))=='Art_RV_Van_Compartment_02');aim(target)
def access_stock():
 if isdriver():press('E',.85)
def select_stock():
 if isdriver():check('roadside_exterior_supplies_access',inv.get_editor_property('OpenContainer') is not None);press('Tab')
def take_stock():
 if isdriver():press('T')
def retrieved():
 if isdriver():check('roadside_coolant_guid_state_from_storage',count('CoolantPartial')==1 and abs(item('CoolantPartial').fuel_litres-1.75)<1e-8 and abs(item('CoolantPartial').condition-.61)<.001);press('I')
def walk_front():
 if isdriver():walk_route([(500,-210),(550,0)])
def walk_center():
 pass # waypoint route already turns after physically clearing the front bumper
def roadside_inspect():
 if isdriver():press('E',.85)
def roadside_aim():
 if isdriver():aim(point)
def roadside_open():
 if isdriver():check('roadside_normal_E_diagnosis',pc.get_editor_property('MechanicalPoint')==point,{'location':str(v.get_actor_transform().inverse_transform_location(p.get_actor_location())),'prompt':str(p.get_component_by_class(unreal.RVInteractionComponent).get_prompt())});press('P')
def roadside_patch():
 if isdriver():check('roadside_stopped_off_cool_service',c.can_service());press('B')
def roadside_refill():
 if isdriver():check('roadside_timed_patch_complete',cooling('bTemporaryPatch') and not point.get_editor_property('RepairPlayer'));request('Refill',item('CoolantPartial'))
def roadside_refilled():
 if isdriver():check('roadside_refill_restores_supply',cooling('CoolantLitres')>11.9 and item('CoolantPartial').fuel_litres<1.75);press('P')
def back_side():
 if isdriver():walk_route([(550,-210),(190,-220)])
def back_cab():
 pass # continuing the same native walking route, no placement shortcut
def continue_travel():
 if isdriver():check('roadside_driver_reentry',pc.get_controlled_pawn()==v);press('W',4)
def recovered_driving():
 check('recoverable_fault_returns_to_travel',v.get_velocity().length()>200 and cooling('TemperatureC')<c.get_editor_property('Tuning').overheat_c and engine('Condition')>.5,{'speed':v.get_velocity().length(),'temperature':cooling('TemperatureC')})
def finish():
 stop_route()
 for key in held:unreal.RVInteriorMotorhome.dispatch_development_key(pc,key,False)
 unreal.unregister_slate_post_tick_callback(h)
 (B/(config['name']+'_'+role+'.json')).write_text(json.dumps({'pid':os.getpid(),'role':role,'config':config,'results':results,'samples':samples},indent=2),encoding='utf-8')
for t,fn in [(0,setup),(1,aim_service),(2,inspect),(3.8,panel),(4,open_hood),(4.8,hood_check),(4.9,debug_guard),(5,initial_attempt),(5.4,client_missing_check),(5.6,host_begin),(6.3,reserved),(7,hostcancel),(8,cancel_receipt),(8.2,inspect),(8.7,give_client_tool),(10,clientpatch),(10.3,valid_contention),(11,busy_check),(12,panel_photo),(19,patch_done),(19.2,wrong_owner_refill),(19.8,wrong_owner_check),(20,concurrent_refill),(22,refill_done),(23,damage_again),(24,replace),(40,replace_done),(41,force_shutdown),(42,shutdown),(44,client_engine_repair),(65,engine_done),(81,radiator_done),(81.5,close_hood),(83,arrange_drive),(84,aim_driver),(85,enter_driver),(87,drive),(90,reset_frame),(95,minorfault),(96,walk),(98,turn),(101,moving),(105,brake),(112,handbrake),(118,stopped),(122,exit_driver),(123.5,outside),(124.5,aim_stock),(125,access_stock),(126.5,select_stock),(127,take_stock),(128,retrieved),(129,walk_front),(131,walk_center),(132.3,roadside_aim),(133,roadside_inspect),(134.5,roadside_open),(135.5,roadside_patch),(145,roadside_refill),(147,roadside_refilled),(148,back_side),(150,back_cab),(151.3,aim_driver),(152,enter_driver),(154,continue_travel),(159,recovered_driving),(161,finish)]:events.append((t,fn))
if config.get('entry_probe'):events=[(t,fn) for t,fn in events if t<7]+[(7.2,finish)]
nextsample=0
def tick(dt):
 global frames,nextsample
 frames+=1
 try:
  for key,(deadline,frame) in list(held.items()):
   if time.time()>deadline and frames>=frame:unreal.RVInteriorMotorhome.dispatch_development_key(pc,key,False);del held[key]
  if events and time.time()-start>=events[0][0]:
   _,fn=events.pop(0);fn()
  steer_route()
  if time.time()>nextsample:
   nextsample=time.time()+.25
   frame=p.get_component_by_class(unreal.RVPassengerReferenceFrameComponent);q=v.get_actor_transform().inverse_transform_location(p.get_actor_location())
   samples.append({'t':time.time()-start,'temperature':cooling('TemperatureC'),'coolant':cooling('CoolantLitres'),'engine':engine('Condition'),'output':engine('OutputScale'),'revision':c.get_editor_property('ServiceRevision'),'repair':str(point.get_editor_property('ActiveRepair')),'local':[q.x,q.y,q.z],'base':str(frame.get_editor_property('CurrentBase')),'correction_count':frame.get_editor_property('CorrectionCount'),'max_correction':frame.get_editor_property('MaxCorrectionCm'),'speed':v.get_velocity().length(),'slate_dt':dt})
 except Exception as e:check('harness_exception',False,repr(e));finish()
h=unreal.register_slate_post_tick_callback(tick)
