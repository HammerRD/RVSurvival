import unreal,json,time,math
B='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate6Validation/'
w=next(w for w in unreal.ObjectIterator(unreal.World) if 'UEDPIE_' in w.get_path_name() and w.get_name()=='Gate6FuelElectricalTest')
pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn();inv=p.get_component_by_class(unreal.RVInventoryComponent)
v=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSystemsMotorhome)[0];fuel=v.get_editor_property('PropulsionFuel');house=v.get_editor_property('HouseBattery');bus=v.get_editor_property('Electrical')
points=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVResourcePoint);fill=next(a for a in points if a.get_editor_property('bFuelFill'));panel=next(a for a in points if not a.get_editor_property('bFuelFill'))
pickup=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVWorldItem) if a.get_editor_property('Item').definition and str(a.get_editor_property('Item').definition.get_editor_property('CatalogId'))=='FuelCanPartial')
rows=[];cycles=[];toggles=[];events=[];idx=0;t=0;itemid=None;target=None;actor_count=None;actorcount_after_refuel=None
def check(n,ok,d=''):rows.append({'case':n,'pass':bool(ok),'detail':str(d)});unreal.log('GATE6_STRESS '+json.dumps(rows[-1]))
def at(s,f):events.append((s,f))
def key(k,on):
 if k=='E' and on and target:aim(target)
 unreal.SystemLibrary.execute_console_command(pc,'Input.'+('+' if on else '-')+'key '+k,pc)
def aim(a):pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p.get_actor_location()+unreal.Vector(0,0,64),a.get_actor_location()))
def arrange(a,pos=None):
 global target
 target=a;p.set_actor_location(pos or a.get_actor_location()+unreal.Vector(-140,0,62),False,True);aim(a)
def can():return next(r for r in inv.get_items() if str(r.definition.get_editor_property('CatalogId'))=='FuelCanPartial')
def setup():
 unreal.SystemLibrary.execute_console_command(w,'rv.Resources.AllowDebug 1',pc)
 bus.debug_set_time_scale(.01)
 r=pickup.get_editor_property('Item');entry=unreal.RVItemStateEntry();entry.set_editor_property('Key','Stress');entry.set_editor_property('Value','retain')
 r.set_editor_property('CustomState',[entry]);pickup.set_editor_property('Item',r)
 arrange(pickup)
def gotcan():
 global itemid,actor_count
 r=can();itemid=r.id
 check('stress_owned_can_via_hold',r.fuel_litres==3.75 and abs(r.condition-.73)<.001)
 actor_count=len(unreal.GameplayStatics.get_all_actors_of_class(w,unreal.Actor))
 arrange(fill,v.get_actor_transform().transform_location(unreal.Vector(-155,-280,95)))
def trial(n):
 fuel.debug_set_fuel(197);inv.debug_set_fuel_can(itemid,5)
 r=can()
 pc.request_refuel(itemid,r.fuel_revision);pc.request_refuel(itemid,r.fuel_revision)
def verify(n):
 r=can();cycles.append({'cycle':n,'tank':fuel.get_editor_property('Litres'),'can':r.fuel_litres,'revision':r.fuel_revision,'quantity':r.quantity,'condition':r.condition,'id':unreal.GuidLibrary.conv_guid_to_string(r.id),'state':[(str(x.key),x.value) for x in r.custom_state]})
def afterfuel():
 global actorcount_after_refuel
 check('100_partial_refuels_and_duplicate_rejections',len(cycles)==100 and all(abs(r['tank']-200)<.001 and abs(r['can']-2)<.001 and abs(r['tank']+r['can']-202)<.001 for r in cycles))
 check('100_cycles_guid_state_and_quantity',len({r['id'] for r in cycles})==1 and all(r['quantity']==1 and abs(r['condition']-.73)<.001 and r['state']==[('Stress','retain')] for r in cycles))
 check('revision_exact_two_per_cycle',all(r['revision']==2*(r['cycle']+1) for r in cycles),[cycles[0]['revision'],cycles[-1]['revision']])
 actorcount_after_refuel=len(unreal.GameplayStatics.get_all_actors_of_class(w,unreal.Actor))
 check('refueling_no_actor_accumulation',actorcount_after_refuel==actor_count,[actor_count,actorcount_after_refuel])
 arrange(panel,v.get_actor_transform().transform_location(unreal.Vector(70,0,185)))
def genrequest(n):pc.request_resource_control('Generator',n%2==0,bus.get_editor_property('ControlRevision'))
def genverify(n):toggles.append({'cycle':n,'running':bus.get_editor_property('bGeneratorRunning'),'revision':bus.get_editor_property('ControlRevision'),'fuel':fuel.get_editor_property('Litres'),'noise':bus.get_generator_noise_strength()})
def aftergenerator():
 check('100_native_authoritative_generator_changes',len(toggles)==100 and all(r['running']==(r['cycle']%2==0) for r in toggles))
 check('generator_revision_progress_no_lost_updates',all(r['revision']==r['cycle']+1 for r in toggles))
 check('generator_noise_follows_running',all((r['noise']>0)==r['running'] for r in toggles))
 check('fuel_monotonic_during_generator_cycles',all(toggles[i]['fuel']<=toggles[i-1]['fuel'] for i in range(1,len(toggles))))
 # Multi-source conservation and priority, including the separately configured source option.
 original=bus.get_editor_property('Tuning')
 loads=list(bus.get_editor_property('Loads'))
 for l in loads:l.set_editor_property('bEnabled',False)
 bus.set_editor_property('Loads',loads)
 house.debug_set_energy(0);fuel.debug_set_fuel(100);bus.debug_set_solar(1);bus.set_external_power_authority(True)
 bus.debug_advance(3600,True,.25,1200)
 check('multi_source_charge_capped_and_priority',abs(house.get_editor_property('EnergyWh')-800)<.001 and 'Shore' in bus.get_source_summary(),bus.get_source_summary())
 house.debug_set_energy(2300);bus.debug_advance(86400,False,0,0)
 check('24h_shore_solar_no_overcharge',house.get_editor_property('EnergyWh')==2400)
 bus.set_external_power_authority(False);bus.debug_set_solar(0);house.debug_set_energy(2400)
 for l in loads:l.set_editor_property('bEnabled',True)
 bus.set_editor_property('Loads',loads);bus.debug_advance(86400,False,0,0)
 check('24h_house_depletion_bounded',house.get_editor_property('EnergyWh')==0 and not bus.is_load_powered('InteriorLights') and not bus.is_load_powered('Refrigerator'))
 # The high-priority light survives a limited bus while lower-priority large loads are shed.
 house.debug_set_energy(.01);bus.debug_advance(1,False,0,0)
 check('load_priority_sheds_large_demands',bus.is_load_powered('InteriorLights') and not bus.is_load_powered('Refrigerator') and not bus.is_load_powered('PoweredStation'))
 house.debug_set_energy(1e-10);bus.debug_advance(1,False,0,0)
 check('fractional_energy_not_stranded_by_absolute_epsilon',house.get_editor_property('EnergyWh')==0 and not bus.has_house_power() and not bus.is_load_powered('InteriorLights'))
 check('debug_recovery_not_shipping_gameplay',not bus.debug_advance(float('nan'),True,1,1000))
 check('stress_final_actor_count_stable',len(unreal.GameplayStatics.get_all_actors_of_class(w,unreal.Actor))==actor_count)
def finish():
 key('E',False);unreal.unregister_slate_post_tick_callback(h)
 json.dump({'results':rows,'refuel_cycles':cycles,'generator_cycles':toggles},open(B+'single.json','w'),indent=2)
at(0,setup);at(.5,lambda:key('E',True));at(1.3,lambda:key('E',False));at(2,gotcan)
at(2.5,lambda:key('E',True));at(3.3,lambda:key('E',False));at(4,lambda:check('stress_fill_hold',pc.get_editor_property('ResourcePoint')==fill))
for n in range(100):
 at(4.5+n*.3,lambda n=n:trial(n));at(4.7+n*.3,lambda n=n:verify(n))
at(35,afterfuel);at(35.5,lambda:key('E',True));at(36.3,lambda:key('E',False));at(37,lambda:check('stress_panel_hold',pc.get_editor_property('ResourcePoint')==panel))
for n in range(100):
 at(37.5+n*.25,lambda n=n:genrequest(n));at(37.68+n*.25,lambda n=n:genverify(n))
at(63,aftergenerator);at(64,finish)
def tick(dt):
 global t,idx
 t+=dt
 try:
  while idx<len(events) and t>=events[idx][0]:f=events[idx][1];idx+=1;f()
 except Exception as e:check('exception',False,repr(e));finish()
h=unreal.register_slate_post_tick_callback(tick)
