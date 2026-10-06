import unreal,json,math
B='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate6Validation/'
w=next(w for w in unreal.ObjectIterator(unreal.World) if 'UEDPIE_' in w.get_path_name() and w.get_name()=='Gate6FuelElectricalTest')
pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn()
v=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSystemsMotorhome)[0]
fuel=v.get_editor_property('PropulsionFuel');house=v.get_editor_property('HouseBattery');chassis=v.get_editor_property('ChassisBattery');bus=v.get_editor_property('Electrical')
inv=p.get_component_by_class(unreal.RVInventoryComponent)
points=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVResourcePoint);fill=next(x for x in points if x.get_editor_property('bFuelFill'));panel=next(x for x in points if not x.get_editor_property('bFuelFill'))
rows=[];events=[];t=0;idx=0;full_id=None;full_before=None;partial_id=None;empty_id=None;tank_before=0;driver_start=None;target=None
def check(n,ok,d=''):
 r={'case':n,'pass':bool(ok),'detail':str(d)};rows.append(r);unreal.log('GATE6 '+json.dumps(r))
def at(s,f):events.append((s,f))
def key(k,on):
 if k=='E' and on and target is not None:
  aim(target)
  unreal.log('GATE6_HOLD '+str((target.get_name(),p.get_actor_location(),pc.get_editor_property('ResourceFeedback'))))
 unreal.SystemLibrary.execute_console_command(pc,'Input.'+('+' if on else '-')+'key '+k,pc)
def items():return inv.get_items()
def record(cat):return next(x for x in items() if str(x.definition.get_editor_property('CatalogId'))==cat)
def pickup(cat):return next(x for x in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVWorldItem) if x.get_editor_property('Item').definition and str(x.get_editor_property('Item').definition.get_editor_property('CatalogId'))==cat)
def aim(a):pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p.get_actor_location()+unreal.Vector(0,0,64),a.get_actor_location()))
def arrange(a,pos=None):
 global target
 target=a
 p.set_actor_location(pos or a.get_actor_location()+unreal.Vector(-140,0,62),False,True);aim(a)
def placefill():arrange(fill,v.get_actor_transform().transform_location(unreal.Vector(-155,-280,95)))
def placepanel():arrange(panel,v.get_actor_transform().transform_location(unreal.Vector(70,0,185)))
def toggle(name,on):pc.request_resource_control(name,on,bus.get_editor_property('ControlRevision'))
def simulate(seconds,engine=False,throttle=0,speed=0):return bus.debug_advance(seconds,engine,throttle,speed)
def loads(enabled):
 a=list(bus.get_editor_property('Loads'))
 for x in a:x.set_editor_property('bEnabled',enabled)
 bus.set_editor_property('Loads',a)
def initial():
 check('configured_fuel_and_batteries',abs(fuel.get_editor_property('Litres')-150)<.01 and house.get_editor_property('CapacityWh')==2400 and chassis.get_editor_property('CapacityWh')==800)
 check('debug_disabled_default',not fuel.debug_set_fuel(1))
 unreal.SystemLibrary.execute_console_command(w,'rv.Resources.AllowDebug 1',pc);bus.debug_set_time_scale(.01)
 check('invalid_nan_rejected',not fuel.debug_set_fuel(float('nan')) and not house.debug_set_energy(float('nan')) and not bus.debug_set_solar(float('nan')))
 fuel.debug_set_fuel(-5);house.debug_set_energy(-5);check('lower_bounds',fuel.get_editor_property('Litres')==0 and house.get_editor_property('EnergyWh')==0)
 fuel.debug_set_fuel(1000);house.debug_set_energy(1e9);check('upper_bounds',fuel.get_editor_property('Litres')==200 and house.get_editor_property('EnergyWh')==2400)
 loads(False);fuel.debug_set_fuel(100);simulate(3600,True);check('hour_idle_fuel',abs(fuel.get_editor_property('Litres')-98.5)<.0001,fuel.get_editor_property('Litres'))
 fuel.debug_set_fuel(100);simulate(3600,True,.5,2682.24);check('hour_load_and_road_fuel',abs(fuel.get_editor_property('Litres')-87.5)<.0001,fuel.get_editor_property('Litres'))
 fuel.debug_set_fuel(.01);simulate(3600,True,1,2682.24);check('fuel_exhaustion_clamped',fuel.get_editor_property('Litres')==0 and not bus.get_editor_property('bEngineRunning'))
 # Fridge is an actual reusable load with a native interval energy balance.
 a=list(bus.get_editor_property('Loads'));a[1].set_editor_property('bEnabled',True);bus.set_editor_property('Loads',a)
 house.debug_set_energy(1000);simulate(3600);check('fridge_90wh_drain',abs(house.get_editor_property('EnergyWh')-910)<.001 and bus.is_load_powered('Refrigerator'),house.get_editor_property('EnergyWh'))
 house.debug_set_energy(0);simulate(1);check('fridge_power_loss_hook',not bus.is_load_powered('Refrigerator'))
 loads(True);simulate(1);check('lights_fail_at_empty',not bus.is_load_powered('InteriorLights') and not v.get_editor_property('FrontLight').is_visible())
 house.debug_set_energy(500);simulate(1);check('all_loads_restore_and_draw',bus.is_load_powered('InteriorLights') and bus.is_load_powered('Refrigerator') and bus.is_load_powered('PoweredStation') and bus.get_editor_property('Flow').requested_watts==234)
 loads(False);house.debug_set_energy(0);bus.debug_set_solar(1);simulate(3600);check('solar_hour_300wh',abs(house.get_editor_property('EnergyWh')-300)<.001)
 bus.debug_set_solar(0);old=house.get_editor_property('EnergyWh');simulate(3600);check('solar_zero_no_energy',house.get_editor_property('EnergyWh')==old)
 house.debug_set_energy(0);bus.set_external_power_authority(True);simulate(3600)
 check('shore_accepts_external_supply',abs(house.get_editor_property('EnergyWh')-800)<.001 and 'Shore' in bus.get_source_summary())
 bus.set_external_power_authority(False)
 house.debug_set_energy(0);chassis.debug_set_energy(0);fuel.debug_set_fuel(100);simulate(3600,True,.5,2682.24)
 check('alternator_distinct_batteries',abs(house.get_editor_property('EnergyWh')-500)<.001 and abs(chassis.get_editor_property('EnergyWh')-250)<.001)
 loads(False);fuel.debug_set_fuel(150);house.debug_set_energy(1500);arrange(pickup('FuelCanFull'))
def fullpicked():
 global full_id,full_before
 r=record('FuelCanFull');full_id=r.id;full_before=r
 check('full_can_native_pickup',r.fuel_litres==20 and r.get_editor_property('bFuelInitialized') and abs(r.condition-.73)<.001);placefill()
def fullrefuel():
 fuel.debug_set_fuel(195);pc.request_refuel(full_id,record('FuelCanFull').fuel_revision)
def fullcheck():
 r=record('FuelCanFull');check('partial_tank_conserves_fuel',abs(fuel.get_editor_property('Litres')-200)<.001 and abs(r.fuel_litres-15)<.001)
 check('refuel_preserves_guid_condition',unreal.GuidLibrary.equal_equal_guid_guid(r.id,full_before.id) and r.condition==full_before.condition and r.quantity==1)
 pc.request_refuel(full_id,0)
def stalecheck():
 check('duplicate_revision_rejected',record('FuelCanFull').fuel_litres==15 and 'Stale' in pc.get_editor_property('ResourceFeedback'))
 pc.set_control_rotation(unreal.Rotator(yaw=v.get_actor_rotation().yaw-90));inv.request_drop(full_id,1)
def dropcheck():
 a=pickup('FuelCanFull');r=a.get_editor_property('Item')
 check('partial_can_drop_state',r.fuel_litres==15 and r.condition==full_before.condition and unreal.GuidLibrary.equal_equal_guid_guid(r.id,full_id))
 arrange(a)
def repick():check('partial_can_repicked',record('FuelCanFull').fuel_litres==15);arrange(next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVExteriorStoragePoint) if str(a.get_editor_property('DoorPartName')).endswith('02')),v.get_actor_transform().transform_location(unreal.Vector(-100,-280,95)))
def transferout():inv.request_transfer(full_id,1,True)
def transfercheck():
 c=inv.get_editor_property('OpenContainer');rr=next(x for x in c.get_items() if unreal.GuidLibrary.equal_equal_guid_guid(x.id,full_id))
 check('fuel_can_exterior_transfer_preserved',rr.fuel_litres==15 and rr.condition==full_before.condition);inv.request_transfer(full_id,1,False)
def partialarrange():
 check('fuel_can_transfer_back',record('FuelCanFull').fuel_litres==15);arrange(pickup('FuelCanPartial'))
def partialpicked():
 global partial_id
 check('partial_pickup_capacity',any(str(x.definition.get_editor_property('CatalogId'))=='FuelCanPartial' for x in items()),(inv.get_editor_property('Feedback'),inv.get_volume_litres(),[(str(x.definition.get_editor_property('CatalogId')),x.quantity) for x in items()]));r=record('FuelCanPartial');partial_id=r.id;check('variable_capacity_partial_can',r.fuel_litres==3.75 and r.definition.get_editor_property('Fuel').capacity_litres==10);placefill()
def partialrefuel():fuel.debug_set_fuel(0);pc.request_refuel(partial_id,record('FuelCanPartial').fuel_revision)
def partialcheck():
 check('partial_can_exact_transfer',abs(fuel.get_editor_property('Litres')-3.75)<.001 and record('FuelCanPartial').fuel_litres==0)
 # Clear the first can to make room through a normal drop, rather than bypassing capacity.
 pc.set_control_rotation(unreal.Rotator(yaw=v.get_actor_rotation().yaw-90));inv.request_drop(full_id,1)
def emptypicked():
 global empty_id
 r=record('FuelCanEmpty');empty_id=r.id;placefill()
def emptyrefuel():pc.request_refuel(empty_id,record('FuelCanEmpty').fuel_revision)
def invalids():
 check('empty_can_rejected',record('FuelCanEmpty').fuel_litres==0 and 'empty' in pc.get_editor_property('ResourceFeedback'))
 pc.request_refuel(unreal.GuidLibrary.new_guid(),0)
def invalidcheck():
 check('unowned_guid_rejected','owned' in pc.get_editor_property('ResourceFeedback'))
 pc.set_control_rotation(unreal.Rotator(yaw=v.get_actor_rotation().yaw-90));inv.request_drop(empty_id,1)
def dieselpicked():placefill()
def dieselcheck():
 check('incompatible_fuel_rejected','Incompatible' in pc.get_editor_property('ResourceFeedback') and record('FuelCanDiesel').fuel_litres==20);placepanel()
def genstart():fuel.debug_set_fuel(100);toggle('Generator',True)
def gentest():
 check('generator_started_authority',bus.get_editor_property('bGeneratorRunning'))
 loads(False);fuel.debug_set_fuel(100);house.debug_set_energy(0);simulate(3600)
 check('generator_burn_and_charge',abs(fuel.get_editor_property('Litres')-98.8)<.01 and abs(house.get_editor_property('EnergyWh')-800)<.01,(fuel.get_editor_property('Litres'),house.get_editor_property('EnergyWh')))
 check('generator_noise_hook',bus.get_generator_noise_strength()>0)
 fuel.debug_set_fuel(20.1);house.debug_set_energy(0);simulate(3600)
 check('generator_stops_at_pickup_reserve',not bus.get_editor_property('bGeneratorRunning') and abs(fuel.get_editor_property('Litres')-20)<.001 and 0<house.get_editor_property('EnergyWh')<200)
 check('generator_noise_cleans_on_stop',bus.get_generator_noise_strength()==0)
 toggle('Generator',True)
def emptygencheck():
 check('reserve_start_rejected',not bus.get_editor_property('bGeneratorRunning') and 'reserve' in pc.get_editor_property('ResourceFeedback'))
 house.debug_set_energy(1000);toggle('InteriorLights',True)
def lightscheck():
 simulate(1);check('panel_switch_and_visible_light',bus.is_load_powered('InteriorLights'))
 pc.request_resource_control('Refrigerator',True,bus.get_editor_property('ControlRevision')-1)
def stalecontrol():
 check('stale_panel_revision_rejected','refresh' in pc.get_editor_property('ResourceFeedback'))
 pc.request_resource_control('Fake',True,bus.get_editor_property('ControlRevision'))
def fakecheck():
 check('unknown_control_rejected','Unknown' in pc.get_editor_property('ResourceFeedback'))
 # Safe development-only simulation stress; real requests are tested separately.
 loads(True);fuel.debug_set_fuel(200);house.debug_set_energy(2400);bus.debug_set_solar(.5);simulate(86400,True,.3,1800)
 check('24h_simulation_all_bounds',0<=fuel.get_editor_property('Litres')<=200 and 0<=house.get_editor_property('EnergyWh')<=2400 and 0<=chassis.get_editor_property('EnergyWh')<=800)
 check('no_negative_can_quantity',all(x.quantity>=1 and x.fuel_litres>=0 for x in items()))
 bus.debug_set_solar(0);loads(False);fuel.debug_set_fuel(0)
 # Drive through accepted seat entry/input/possession.
 driver=next(s for s in v.get_seats() if s.get_editor_property('bDriverSeat'))
 ep=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVVehicleEntryPoint) if a.get_editor_property('Seat')==driver and abs(v.get_actor_transform().inverse_transform_location(a.get_actor_location()).y)<100)
 arrange(ep,v.get_actor_transform().transform_location(unreal.Vector(130,0,180)))
def drive_start():
 global driver_start
 check('empty_tank_seat_and_possession_intact',pc.get_controlled_pawn()==v)
 driver_start=v.get_actor_location();key('W',True)
def emptydrive():
 key('W',False);d=(v.get_actor_location()-driver_start).length();check('empty_fuel_no_propulsion',d<30,d)
 fuel.debug_set_fuel(100)
def restoredrive():
 global driver_start
 driver_start=v.get_actor_location();key('W',True)
def restorecheck():
 key('W',False);key('SpaceBar',True);d=(v.get_actor_location()-driver_start).length();check('refuel_restores_chaos_propulsion',d>150,d)
 check('real_drive_consumes_fuel',fuel.get_editor_property('Litres')<100)
def finish():
 key('SpaceBar',False);key('W',False);key('E',False)
 unreal.unregister_slate_post_tick_callback(h);json.dump({'results':rows,'map':'Gate6FuelElectricalTest'},open(B+'single.json','w'),indent=2)
at(0,initial);at(.4,lambda:key('E',True));at(1.2,lambda:key('E',False));at(1.8,fullpicked)
at(2.4,lambda:key('E',True));at(3.2,lambda:key('E',False));at(3.8,lambda:check('fuel_fill_native_hold',pc.get_editor_property('ResourcePoint')==fill,(pc.get_editor_property('ResourceFeedback'),pc.get_editor_property('ResourcePoint'))));at(4,fullrefuel);at(4.7,fullcheck);at(5.3,stalecheck);at(6,dropcheck)
at(6.4,lambda:key('E',True));at(7.2,lambda:key('E',False));at(7.8,repick);at(8.4,lambda:key('E',True));at(9.2,lambda:key('E',False));at(9.8,transferout);at(10.5,transfercheck);at(11.2,partialarrange)
at(11.6,lambda:key('E',True));at(12.4,lambda:key('E',False));at(13,partialpicked);at(13.5,lambda:key('E',True));at(14.3,lambda:key('E',False));at(15,partialrefuel);at(15.7,partialcheck)
at(16.4,lambda:arrange(pickup('FuelCanEmpty')));at(16.8,lambda:key('E',True));at(17.6,lambda:key('E',False));at(18.2,emptypicked);at(18.7,lambda:key('E',True));at(19.5,lambda:key('E',False));at(20.2,emptyrefuel);at(20.8,invalids);at(21.5,invalidcheck)
at(22.2,lambda:arrange(pickup('FuelCanDiesel')));at(22.6,lambda:key('E',True));at(23.4,lambda:key('E',False));at(24,dieselpicked);at(24.5,lambda:key('E',True));at(25.3,lambda:key('E',False));at(26,lambda:pc.request_refuel(record('FuelCanDiesel').id,0));at(26.7,dieselcheck)
at(27.2,lambda:key('E',True));at(28,lambda:key('E',False));at(28.7,genstart);at(29.4,gentest);at(30.1,emptygencheck);at(30.8,lightscheck);at(31.5,stalecontrol);at(32.2,fakecheck)
at(32.8,lambda:key('E',True));at(33.6,lambda:key('E',False));at(34.3,drive_start);at(37.3,emptydrive);at(38,restoredrive);at(42,restorecheck);at(43,finish)
def tick(dt):
 global t,idx
 t+=dt
 try:
  while idx<len(events) and t>=events[idx][0]:
   f=events[idx][1];idx+=1;f()
 except Exception as e:check('exception',False,repr(e));finish()
h=unreal.register_slate_post_tick_callback(tick)


