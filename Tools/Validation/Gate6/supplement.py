import unreal,json
B='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate6Validation/'
w=next(w for w in unreal.ObjectIterator(unreal.World) if 'UEDPIE_' in w.get_path_name() and w.get_name()=='Gate6FuelElectricalTest')
pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn();inv=p.get_component_by_class(unreal.RVInventoryComponent)
v=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSystemsMotorhome)[0];fuel=v.get_editor_property('PropulsionFuel');gfuel=v.get_editor_property('GeneratorFuel');house=v.get_editor_property('HouseBattery');bus=v.get_editor_property('Electrical')
points=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVResourcePoint);fill=next(a for a in points if a.get_editor_property('bFuelFill'));panel=next(a for a in points if not a.get_editor_property('bFuelFill'))
stations={str(a.get_editor_property('StationName')):a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVInteriorStation)}
rows=[];events=[];idx=0;t=0;target=None;startcount=0;startpos=None;canid=None
def check(n,ok,d=''):rows.append({'case':n,'pass':bool(ok),'detail':str(d)});unreal.log('GATE6_SUPPLEMENT '+json.dumps(rows[-1]))
def at(s,f):events.append((s,f))
def aim(a):pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p.get_actor_location()+unreal.Vector(0,0,64),a.get_actor_location()))
def key(k,on):
 if k=='E' and on and target:aim(target)
 unreal.SystemLibrary.execute_console_command(pc,'Input.'+('+' if on else '-')+'key '+k,pc)
def arrange(a,local=None):
 global target
 target=a;p.set_actor_location(v.get_actor_transform().transform_location(unreal.Vector(*local)) if local else a.get_actor_location()+unreal.Vector(-140,0,62),False,True);aim(a)
def request(name,on):pc.request_resource_control(name,on,bus.get_editor_property('ControlRevision'))
def setup():
 unreal.SystemLibrary.execute_console_command(w,'rv.Resources.AllowDebug 1',pc);bus.debug_set_time_scale(.01)
 check('optional_power_binding_saved',str(stations['Navigation'].get_editor_property('RequiredPowerLoad'))=='PoweredStation' and str(stations['Workbench'].get_editor_property('RequiredPowerLoad'))=='None')
 arrange(panel,(70,0,185))
def unpower():
 request('PoweredStation',False);house.debug_set_energy(0);fuel.debug_set_fuel(0);bus.debug_set_solar(0)
def navsetup():
 global startcount
 bus.debug_advance(1,False,0,0);startcount=stations['Navigation'].get_editor_property('InteractionCount')
 arrange(stations['Navigation'],(130,0,180))
def navblocked():
 check('powered_workstation_rejects_no_power',stations['Navigation'].get_editor_property('InteractionCount')==startcount and not bus.is_load_powered('PoweredStation'))
 arrange(stations['Workbench'],(-190,0,195))
def handcheck():
 check('hand_workbench_works_without_power',stations['Workbench'].get_editor_property('InteractionCount')==1)
 house.debug_set_energy(1000);request('PoweredStation',True)
def navrestore():
 bus.debug_advance(1,False,0,0);arrange(stations['Navigation'],(130,0,180))
def navworked():
 check('powered_station_restored_interaction',stations['Navigation'].get_editor_property('InteractionCount')==startcount+1 and bus.is_load_powered('PoweredStation'))
 key('H',True)
def lightcheck():
 key('H',False);check('visible_interior_light_tracks_power',bus.is_load_powered('InteriorLights') and v.get_editor_property('FrontLight').is_visible() and v.get_editor_property('RearLight').is_visible())
 # Configuration test of the alternate source, not a new generator ownership path.
 tuning=bus.get_editor_property('Tuning');tuning.set_editor_property('bSharedGeneratorFuel',False);bus.set_editor_property('Tuning',tuning)
 gfuel.debug_set_fuel(2);request('Generator',True)
def separated():
 bus.debug_advance(3600,False,0,0)
 check('separate_generator_source_conservation',abs(gfuel.get_editor_property('Litres')-.8)<.01 and fuel.get_editor_property('Litres')==0 and bus.get_editor_property('bGeneratorRunning'),gfuel.get_editor_property('Litres'))
 bus.debug_advance(3600,False,0,0)
 check('separate_generator_empty_stop',gfuel.get_editor_property('Litres')==0 and not bus.get_editor_property('bGeneratorRunning') and bus.get_generator_noise_strength()==0)
 full=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVWorldItem) if a.get_editor_property('Item').definition and str(a.get_editor_property('Item').definition.get_editor_property('CatalogId'))=='FuelCanFull')
 arrange(full)
def fullowned():
 global canid
 r=next(x for x in inv.get_items() if str(x.definition.get_editor_property('CatalogId'))=='FuelCanFull');canid=r.id
 check('full_can_owned_before_empty_tank_refuel',r.fuel_litres==20 and fuel.get_editor_property('Litres')==0)
 arrange(fill,(-155,-280,95))
def actualrefuel():pc.request_refuel(canid,0)
def restored():
 r=next(x for x in inv.get_items() if unreal.GuidLibrary.equal_equal_guid_guid(x.id,canid))
 check('real_refuel_empty_tank',abs(fuel.get_editor_property('Litres')-20)<.001 and r.fuel_litres==0 and r.quantity==1)
 driver=next(s for s in v.get_seats() if s.get_editor_property('bDriverSeat'))
 ep=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVVehicleEntryPoint) if a.get_editor_property('Seat')==driver and abs(v.get_actor_transform().inverse_transform_location(a.get_actor_location()).y)<100)
 arrange(ep,(130,0,180))
def drivestart():
 global startpos
 check('seat_possession_after_can_refuel',pc.get_controlled_pawn()==v);startpos=v.get_actor_location();key('W',True)
def drivecheck():
 key('W',False);key('SpaceBar',True)
 check('can_refuel_restores_actual_propulsion',(v.get_actor_location()-startpos).length()>150 and fuel.get_editor_property('Litres')<20,(v.get_actor_location()-startpos).length())
 check('no_respawn_vehicle_or_seat_corruption',len(unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSystemsMotorhome))==1 and pc.get_controlled_pawn()==v)
def finish():
 key('SpaceBar',False);key('E',False);key('W',False);key('H',False);unreal.unregister_slate_post_tick_callback(h);json.dump({'results':rows},open(B+'single.json','w'),indent=2)
at(0,setup);at(.5,lambda:key('E',True));at(1.3,lambda:key('E',False));at(2,unpower);at(2.8,navsetup);at(3.3,lambda:key('E',True));at(4.1,lambda:key('E',False));at(4.8,navblocked)
at(5.3,lambda:key('E',True));at(6.1,lambda:key('E',False));at(6.8,handcheck);at(7.6,navrestore);at(8.1,lambda:key('E',True));at(8.9,lambda:key('E',False));at(9.6,navworked);at(10.3,lightcheck);at(11.1,separated)
at(11.7,lambda:key('E',True));at(12.5,lambda:key('E',False));at(13.2,fullowned);at(13.7,lambda:key('E',True));at(14.5,lambda:key('E',False));at(15.2,actualrefuel);at(16,restored)
at(16.5,lambda:key('E',True));at(17.3,lambda:key('E',False));at(18,drivestart);at(22,drivecheck);at(23,finish)
def tick(dt):
 global t,idx
 t+=dt
 try:
  while idx<len(events) and t>=events[idx][0]:f=events[idx][1];idx+=1;f()
 except Exception as e:check('exception',False,repr(e));finish()
h=unreal.register_slate_post_tick_callback(tick)
