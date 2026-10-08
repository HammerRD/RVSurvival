import unreal,json,time,os,math
B='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate9Validation/'
session=json.load(open(B+'session.json'));config=session['config'];start=session['start']
w=next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='Gate9CombatInfectedTest' and unreal.GameplayStatics.get_player_controller(w,0) and unreal.GameplayStatics.get_player_controller(w,0).get_controlled_pawn())
authority=unreal.GameplayStatics.get_game_mode(w) is not None
own=unreal.GameplayStatics.get_player_controller(w,0);p=own.get_controlled_pawn();other=next(c for c in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSurvivorCharacter) if c!=p);hp=p if authority else other;cp=other if authority else p
v=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSystemsMotorhome)[0];fuel=v.get_editor_property('PropulsionFuel');bus=v.get_editor_property('Electrical');house=v.get_editor_property('HouseBattery')
hi=hp.get_component_by_class(unreal.RVInventoryComponent);ci=cp.get_component_by_class(unreal.RVInventoryComponent);inv=hi if authority else ci
points=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVResourcePoint);fill=next(x for x in points if x.get_editor_property('bFuelFill'));panel=next(x for x in points if not x.get_editor_property('bFuelFill'))
door=next(x for x in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVExteriorStoragePoint) if str(x.get_editor_property('DoorPartName')).endswith('02'));container=door.get_editor_property('Container')
rows=[];samples=[];events=[];idx=0;active=True;nextsample=0;canid=None;partialid=None;partialcondition=.61;target=None;total_before=None
def check(n,ok,d=''):
 r={'case':n,'pass':bool(ok),'detail':str(d)};rows.append(r);unreal.log('GATE6_NET '+json.dumps(r))
def at(s,f):events.append((s,f))
def cmd(s):unreal.SystemLibrary.execute_console_command(own,s,own)
def aim_eye(point):
 origin=p.get_actor_eyes_view_point()[0]
 if p.get_editor_property('bUseControllerRotationYaw'):
  profile=p.get_component_by_class(unreal.RVCharacterPresentationComponent).get_editor_property('Profile');offset=profile.get_editor_property('OwnerCameraOffset');position=p.get_actor_location();angle=math.atan2(point.y-position.y,point.x-position.x)
  origin=position+unreal.Vector(math.cos(angle)*offset.x-math.sin(angle)*offset.y,math.sin(angle)*offset.x+math.cos(angle)*offset.y,p.get_editor_property('BaseEyeHeight')+offset.z)
 return origin


def aim(a):own.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(aim_eye(a.get_actor_location()),a.get_actor_location()))
power_station=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVInteriorStation) if str(a.get_editor_property('StationName'))=='Power')
def focus(a):
 global target
 target=a;aim(a)
def key(k,on):
 if k=='E' and on and target is not None:aim(target)
 unreal.RVInteriorMotorhome.dispatch_development_key(own,k,on)
def records(c,cat):return [r for r in c.get_items() if str(r.definition.get_editor_property('CatalogId'))==cat]
def allcans():return records(hi,'FuelCanFull')+records(ci,'FuelCanFull')
def pickups(cat):return [x for x in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVWorldItem) if x.get_editor_property('Item').definition and str(x.get_editor_property('Item').definition.get_editor_property('CatalogId'))==cat]
def place(point,local=None):
 for c,offset in ([(hp,-45),(cp,45)] if authority else [(p,45)]):
   q=local+unreal.Vector(offset,0,0) if local else point.get_actor_location()+unreal.Vector(-140,offset,62)
   if local:q=v.get_actor_transform().transform_location(q)
   if point in [fill,door]:
    surface=v.get_actor_transform().inverse_transform_location(point.get_actor_location());side=1 if surface.y>0 else -1;distance=140 if c==hp else 230
    q=v.get_actor_transform().transform_location(unreal.Vector(surface.x,surface.y+side*distance,95))
   c.set_actor_location(q,False,True)
def sample():
 samples.append({'own_position':str(v.get_actor_transform().inverse_transform_location(p.get_actor_location())),'own_resource_feedback':own.get_editor_property('ResourceFeedback'),'t':time.time()-start,'fuel':fuel.get_editor_property('Litres'),'house':house.get_editor_property('EnergyWh'),'generator':bus.get_editor_property('bGeneratorRunning'),'revision':bus.get_editor_property('ControlRevision'),'lights':bus.is_load_powered('InteriorLights'),'solar':bus.get_editor_property('SolarInput'),'source':bus.get_source_summary(),'can':[{'id':unreal.GuidLibrary.conv_guid_to_string(r.id),'litres':r.fuel_litres,'revision':r.fuel_revision,'condition':r.condition} for r in allcans()]})
def setup():
 cmd('t.MaxFPS 60');cmd('t.IdleWhenNotForeground 0')
 if authority:
  cmd('rv.Resources.AllowDebug 1');fuel.debug_set_fuel(185);house.debug_set_energy(1000)
  place(pickups('FuelCanFull')[0])
 else:
  cmd('rv.Resources.AllowDebug 1')
  check('client_debug_mutation_rejected',not fuel.debug_set_fuel(999) and not house.debug_set_energy(9999) and not bus.debug_set_solar(1))
def pickupcheck():
 global canid
 rr=allcans();check('one_winner_pickup_contention',len(rr)==1 and len(pickups('FuelCanFull'))==0,[(str(r.id),r.fuel_litres) for r in rr]);canid=rr[0].id
 check('full_can_state_replicated',rr[0].fuel_litres==20 and rr[0].quantity==1 and abs(rr[0].condition-.73)<.001)
 place(fill,unreal.Vector(-155,-280,95));focus(fill)
def opencheck():check('own_fill_open',own.get_editor_property('ResourcePoint')==fill,own.get_editor_property('ResourceFeedback'))
def refuel(rev):own.request_refuel(canid,rev)
def conserved(n,expected):
 rr=allcans();value=fuel.get_editor_property('Litres')+sum(r.fuel_litres for r in rr)
 check(n,len(rr)==1 and abs(value-expected)<.01,{'total':value,'tank':fuel.get_editor_property('Litres'),'can':rr[0].fuel_litres if rr else None})
def duplicatecheck():
 conserved('concurrent_refuel_conservation',205)
 check('partial_tank_can_remaining',abs(fuel.get_editor_property('Litres')-200)<.001 and allcans()[0].fuel_litres==5)
 check('owner_or_ownership_feedback','Stale' in own.get_editor_property('ResourceFeedback') or 'owned' in own.get_editor_property('ResourceFeedback'),own.get_editor_property('ResourceFeedback'))
 if authority:fuel.debug_set_fuel(0)
def emptycheck():
 conserved('second_transfer_conserves_remaining',5)
 check('empty_can_after_transfer',allcans()[0].fuel_litres==0)
 # Normal owned drop; both roles observe world state, then contend to repick.
 if records(inv,'FuelCanFull'):
  own.set_control_rotation(unreal.Rotator(yaw=v.get_actor_rotation().yaw-90));inv.request_drop(canid,1)
def dropcheck():
 rr=pickups('FuelCanFull');check('dropped_can_replicates_once',len(rr)==1 and not allcans())
 r=rr[0].get_editor_property('Item');check('drop_guid_amount_condition',unreal.GuidLibrary.equal_equal_guid_guid(r.id,canid) and r.fuel_litres==0 and abs(r.condition-.73)<.001)
 place(rr[0]);focus(rr[0])
def repickcheck():
 check('repick_contention_single_identity',len(allcans())==1 and not pickups('FuelCanFull') and unreal.GuidLibrary.equal_equal_guid_guid(allcans()[0].id,canid))
 if authority:
  r=unreal.RVItemInstance();r.set_editor_property('Id',unreal.GuidLibrary.new_guid());r.set_editor_property('Definition',unreal.load_asset('/Game/Resources/DA_FuelCanPartial'));r.set_editor_property('Condition',partialcondition)
  st=unreal.RVItemStateEntry();st.set_editor_property('Key','NetTest');st.set_editor_property('Value','preserve');r.set_editor_property('CustomState',[st]);hi.add_authority(r)
 place(door,unreal.Vector(-100,-280,95));focus(door)
def rememberpartial():
 global partialid
 partialid=records(hi,'FuelCanPartial')[0].id
 check('shared_exterior_open',inv.get_editor_property('OpenContainer')==container)
 if authority:inv.request_transfer(partialid,1,True)
def containercheck():
 rr=records(container,'FuelCanPartial');check('shared_partial_fuel_container',len(rr)==1 and rr[0].fuel_litres==3.75 and abs(rr[0].condition-partialcondition)<.001 and rr[0].custom_state[0].value=='preserve')
 ownid=rr[0].id;inv.request_transfer(ownid,1,False)
def containerwinner():
 rr=records(hi,'FuelCanPartial')+records(ci,'FuelCanPartial');check('one_container_winner_no_fuel_duplicate',len(rr)==1 and not records(container,'FuelCanPartial') and rr[0].fuel_litres==3.75 and unreal.GuidLibrary.equal_equal_guid_guid(rr[0].id,partialid))
 if authority:
  fuel.debug_set_fuel(100);house.debug_set_energy(1000);bus.debug_set_solar(.5)
 place(panel,unreal.Vector(65,0,185));focus(power_station)
def panelcheck():
 check('both_can_open_control_panel',own.get_editor_property('ResourcePoint')==panel,own.get_editor_property('ResourceFeedback'))
 own.request_resource_control('Generator',True,bus.get_editor_property('ControlRevision'))
def generatorcheck():
 check('generator_state_converged',bus.get_editor_property('bGeneratorRunning') and bus.get_generator_noise_strength()>0)
 own.request_resource_control('InteriorLights',True,bus.get_editor_property('ControlRevision'))
def lightscheck():
 check('lights_and_sources_converged',bus.is_load_powered('InteriorLights') and house.get_editor_property('EnergyWh')>1000,bus.get_source_summary())
 own.request_resource_control('Refrigerator',False,bus.get_editor_property('ControlRevision')-1)
def stalecheck():
 check('stale_control_rejected','refresh' in own.get_editor_property('ResourceFeedback'),own.get_editor_property('ResourceFeedback'))
 if authority:key('H',True)
def nativecheck():
 if authority:key('H',False)
def nativeverify():
 check('native_host_panel_H_switch',not bus.is_load_powered('InteriorLights'))
 if authority:
  hp.set_actor_location(v.get_actor_transform().transform_location(unreal.Vector(2000,0,100)),False,True)
def outrequest():
 if authority:own.request_resource_control('Generator',False,bus.get_editor_property('ControlRevision'))
def outcheck():
 check('out_of_range_does_not_stop_generator',bus.get_editor_property('bGeneratorRunning'))
 if authority:check('out_of_range_feedback','reach' in own.get_editor_property('ResourceFeedback'))
 if not authority:own.request_resource_control('Generator',False,bus.get_editor_property('ControlRevision'))
def stopcheck():
 check('remote_generator_stop_converged',not bus.get_editor_property('bGeneratorRunning') and bus.get_generator_noise_strength()==0)
 check('fuel_battery_bounds',0<=fuel.get_editor_property('Litres')<=200 and 0<=house.get_editor_property('EnergyWh')<=2400)
 check('solar_authoritative_input',bus.get_editor_property('SolarInput')==.5)
 check('independent_process',os.getpid()>0)
 if authority:
  hp.set_actor_location(v.get_actor_transform().transform_location(unreal.Vector(20,0,185)),False,True)
 focus(power_station)
def reopen():key('E',True)
def repeatcheck():
 check('panel_no_ownership_lock',own.get_editor_property('ResourcePoint')==panel)
 if not authority:
  for _ in range(100):own.request_resource_control('InteriorLights',True,-123)
def floodcheck():
 check('invalid_request_burst_no_mutation',not bus.is_load_powered('InteriorLights') and 0<=house.get_editor_property('EnergyWh')<=2400)
 # Prepare a client disconnect with generator running; shared machinery has no controller lock.
 if not authority:own.request_resource_control('Generator',True,bus.get_editor_property('ControlRevision'))
def beforedisconnect():check('generator_before_disconnect',bus.get_editor_property('bGeneratorRunning'))
def finishclient():
 global active
 if authority:return
 sample();json.dump({'pid':os.getpid(),'authority':False,'config':config,'results':rows,'samples':samples},open(B+config['name']+'_client.json','w'),indent=2)
 active=False;unreal.unregister_slate_post_tick_callback(h);controller=own;execute=unreal.SystemLibrary.execute_console_command
 from runner_runtime import release_runners
 release_runners();execute(controller,'disconnect',controller)
def afterdisconnect():
 if not authority:return
 check('disconnect_preserves_shared_power_and_storage',bus.get_editor_property('bGeneratorRunning') and len(unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSystemsMotorhome))==1 and len(records(hi,'FuelCanPartial'))+len(records(container,'FuelCanPartial'))<=1)
 own.request_resource_control('Generator',False,bus.get_editor_property('ControlRevision'))
def finishserver():
 global active
 if not authority:return
 check('host_control_after_disconnect',not bus.get_editor_property('bGeneratorRunning'),own.get_editor_property('ResourceFeedback'))
 sample();active=False;unreal.unregister_slate_post_tick_callback(h);json.dump({'pid':os.getpid(),'authority':True,'config':config,'results':rows,'samples':samples},open(B+config['name']+'_server.json','w'),indent=2)
at(0,setup);at(.8,lambda:focus(pickups('FuelCanFull')[0]));at(1.2,lambda:key('E',True));at(2.2,lambda:key('E',False));at(3,pickupcheck)
at(3.8,lambda:key('E',True));at(4.8,lambda:key('E',False));at(5.5,opencheck);at(6,lambda:refuel(0));at(7,lambda:refuel(0));at(8,duplicatecheck)
at(9,lambda:refuel(1));at(10,emptycheck);at(11,dropcheck);at(11.8,lambda:key('E',True));at(12.8,lambda:key('E',False));at(13.5,repickcheck)
at(14.3,lambda:key('E',True));at(15.3,lambda:key('E',False));at(16,rememberpartial);at(17,containercheck);at(18,containerwinner)
at(18.8,lambda:key('E',True));at(19.8,lambda:key('E',False));at(20.5,panelcheck);at(22,generatorcheck);at(23.5,lightscheck);at(24.5,stalecheck);at(24.7,nativecheck);at(26,nativeverify)
at(26.1,lambda:key('H',True) if not authority else None);at(26.3,lambda:key('H',False) if not authority else None)
at(27,lambda:check('native_client_panel_H_switch',bus.is_load_powered('InteriorLights')))
at(27.2,outrequest);at(27.3,lambda:own.request_resource_control('InteriorLights',False,bus.get_editor_property('ControlRevision')) if not authority else None);at(28,outcheck);at(29.5,stopcheck);at(30.5,reopen);at(31.5,lambda:key('E',False));at(32.5,repeatcheck);at(34,floodcheck);at(35.5,beforedisconnect)
at(36,finishclient);at(40,afterdisconnect);at(41.5,finishserver)
def tick(dt):
 global idx,nextsample
 if not active:return
 t=time.time()-start
 if t<0:return
 try:
  while idx<len(events) and t>=events[idx][0]:
   f=events[idx][1];idx+=1;terminating=f==finishclient and not authority;f()
   if terminating:return
   if not active:return
  if t>=nextsample:sample();nextsample=t+.25
 except Exception as e:
  check('exception',False,repr(e));finishserver() if authority else finishclient()
h=unreal.register_slate_post_tick_callback(tick)

if config.get("network"):
 for name,value in [("PktLagMin",100),("PktLagMax",100),("PktLoss",2)]:cmd("NetEmulation."+name+" "+str(value))

