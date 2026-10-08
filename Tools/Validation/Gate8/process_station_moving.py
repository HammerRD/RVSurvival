"""Rear seating, moving pantry UI, exterior contention and ladder real-input paths.
Only initial/isolated exterior approach fixtures and item seeding use authority helpers.
No seat, rest, door, transfer or climb gameplay RPC shortcut is called.
"""
import unreal,json,time,os
from pathlib import Path
B=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate8Validation')
session=json.loads((B/'session.json').read_text());config=session['config'];start=session['start']
w=next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='Gate8MedicalTest' and unreal.GameplayStatics.get_player_controller(w,0) and unreal.GameplayStatics.get_player_controller(w,0).get_controlled_pawn())
authority=unreal.GameplayStatics.get_game_mode(w) is not None
role='server' if authority else 'client'
pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn()
other=next(c for c in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSurvivorCharacter) if c!=p)
hp=p if authority else other;cp=other if authority else p
isdriver=authority==(config['driver']=='host');dp=p if isdriver else other;wp=other if isdriver else p
climbing_host=config['driver']=='client';isclimber=authority==climbing_host
climber=hp if climbing_host else cp;ladder_driver=cp if climbing_host else hp;walk_origin=None
v=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSystemsMotorhome)[0]
driver=next(s for s in v.get_seats() if s.get_editor_property('bDriverSeat'))
passenger=next(s for s in v.get_seats() if not s.get_editor_property('bDriverSeat') and not s.get_editor_property('bInteriorOnly'))
front=v.get_editor_property('DinetteFrontSeat');rear=v.get_editor_property('DinetteRearSeat')
entries=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVVehicleEntryPoint)
def entry(seat,outside):return next(a for a in entries if a.get_editor_property('Seat')==seat and (abs(v.get_actor_transform().inverse_transform_location(a.get_actor_location()).y)>100)==outside)
de=entry(driver,True);pe=entry(passenger,True);fe=entry(front,False);re=entry(rear,False)
door=v.get_editor_property('HouseDoor')
events=[];idx=0;results=[];samples=[];active=True;nextsample=0;input_frame=0;pulses={}
def at(t,fn):events.append((t,fn))
def check(name,ok,detail=''):
    row={'case':name,'pass':bool(ok),'detail':str(detail)};results.append(row);unreal.log('AUX_NET '+json.dumps(row))
def cmd(text):unreal.SystemLibrary.execute_console_command(pc,text,pc)
def key(k,on):cmd('Input.'+('+' if on else '-')+'key '+k)
def tap(t,k,role=None):
    def press():
        if role is None or (role=='driver' and isdriver) or (role=='walker' and not isdriver) or (role=='host' and authority) or (role=='client' and not authority):
            unreal.RVInteriorMotorhome.dispatch_development_key(pc,k,True);pulses[k]=(time.time()+.15,input_frame+3)
    at(t,press)
def local(c):
    q=v.get_actor_transform().inverse_transform_location(c.get_actor_location());return [q.x,q.y,q.z]
def aim(a):
    point=a.get_editor_property('DoorCollision').get_world_location() if isinstance(a,unreal.RVInteractiveDoor) else a.get_actor_location()
    pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p.get_actor_location()+unreal.Vector(0,0,p.get_editor_property('BaseEyeHeight')),point))
def inventory(c):return c.get_component_by_class(unreal.RVInventoryComponent)
def quantity(component):return sum(item.quantity for item in component.get_items())
def seed(component,definition):
    item=unreal.RVItemInstance();item.set_editor_property('Id',unreal.GuidLibrary.new_guid());item.set_editor_property('Definition',unreal.load_asset('/Game/Items/DA_'+definition));item.set_editor_property('Condition',.62)
    component.add_authority(item)
def place(c,xyz):
    if authority:c.set_actor_location(v.get_actor_transform().transform_location(unreal.Vector(*xyz)),False,True)
def walking(c):return c.get_editor_property('SeatedVehicle') is None and c.get_component_by_class(unreal.CharacterMovementComponent).get_editor_property('MovementMode')==unreal.MovementMode.MOVE_WALKING
def setup():
    cmd('t.MaxFPS 60');cmd('t.IdleWhenNotForeground 0')
    if authority:
        for character,a,side in [(dp,de,-1),(wp,pe,1)]:
            q=v.get_actor_transform().inverse_transform_location(a.get_actor_location());place(character,(q.x,q.y+side*125,100))
        seed(inventory(wp),'Water')

station=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVMedicalStation)[0]
health=wp.get_editor_property('PlayerState').get_editor_property('Health')
inv=inventory(wp);storage=station.get_editor_property('LinkedStorage')
def kit():return next(i for i in inv.get_items() if str(i.definition.get_editor_property('DisplayName'))=='AdvancedKit')
def injury():return health.get_editor_property('Injuries')[0]
def begin():
 if not isdriver:health.request_treatment(wp.get_editor_property('PlayerState'),injury().id,kit().id,injury().revision)
def fixture():
 cmd('t.MaxFPS 60')
 if config.get('network'):
  for k,value in [('PktLagMin',100),('PktLagMax',100),('PktLoss',2)]:cmd('NetEmulation.'+k+' '+str(value))
 if authority:
  q=v.get_actor_transform().inverse_transform_location(station.get_actor_location());place(wp,(q.x,0,180));d=v.get_actor_transform().inverse_transform_location(de.get_actor_location());place(dp,(d.x,d.y-125,100))
  health.debug_apply_injury(unreal.RVInjuryKind.WOUND,unreal.RVBodyRegion.LEFT_ARM,3)
  item=unreal.RVItemInstance();item.set_editor_property('Id',unreal.GuidLibrary.new_guid());item.set_editor_property('Definition',unreal.load_asset('/Game/Medical/DA_AdvancedKit'));item.set_editor_property('Quantity',2);item.set_editor_property('Condition',.81);inv.add_authority(item)
def precheck():
 check('advanced_without_station_rejected',kit().quantity==2 and injury().bleeding_per_minute>0,health.get_editor_property('Feedback'))
 if not isdriver:aim(station);key('E',True)
def station_check():
 if not isdriver:
  check('normal_E_station_registered',pc.get_editor_property('MedicalStation')==station,health.get_editor_property('Feedback'))
  check('linked_storage_opened',inv.get_editor_property('OpenContainer')==storage)
  inv.request_transfer(kit().id,1,True)
def transferred():
 check('linked_medical_storage_transfer',kit().quantity==1 and sum(i.quantity for i in storage.get_items())>=1)
 if not isdriver:
  item=next(i for i in storage.get_items() if str(i.definition.get_editor_property('DisplayName'))=='AdvancedKit');inv.request_transfer(item.id,1,False)
def returned():
 items=[i for i in inv.get_items() if str(i.definition.get_editor_property('DisplayName'))=='AdvancedKit']
 check('station_supply_returned_state',sum(i.quantity for i in items)==2 and all(abs(i.condition-.81)<.0001 for i in items),[(i.quantity,i.condition,unreal.GuidLibrary.conv_guid_to_string(i.id)) for i in items])
 begin()
def treated():
 check('advanced_parked_completed',injury().bleeding_per_minute==0,health.get_editor_property('Feedback'))
 check('advanced_consumed_once',sum(i.quantity for i in inv.get_items() if str(i.definition.get_editor_property('DisplayName'))=='AdvancedKit')==1)
def moving_reject():
 check('medical_station_vehicle_moving',v.get_velocity().length()>200,v.get_velocity().length());begin()
def moving_transfer():
 check('advanced_requires_parked',kit().quantity==1 and 'Park the RV' in str(health.get_editor_property('Feedback')),health.get_editor_property('Feedback'))
 if not isdriver:inv.request_transfer(kit().id,1,True)
def moving_transferred():
 check('moving_medical_storage_authoritative',sum(i.quantity for i in inv.get_items() if str(i.definition.get_editor_property('DisplayName'))=='AdvancedKit')==0 and sum(i.quantity for i in storage.get_items() if str(i.definition.get_editor_property('DisplayName'))=='AdvancedKit')==1)
def finish():
 if isdriver:key('W',False)
 for k in list(pulses):unreal.RVInteriorMotorhome.dispatch_development_key(pc,k,False)
 unreal.unregister_slate_post_tick_callback(handle)
 (B/(config['name']+'_'+role+'.json')).write_text(json.dumps({'pid':os.getpid(),'role':role,'config':config,'kind':'normal E station entry; owned inventory/treatment requests','results':results,'power_requirement':str(station.get_editor_property('RequiredPowerLoad'))},indent=2))
at(0,fixture);at(1,lambda:aim(de) if isdriver else None);at(1.2,lambda:key('E',True) if isdriver else None);at(2.2,lambda:key('E',False) if isdriver else None);at(3,begin);at(5,precheck);at(6,lambda:key('E',False) if not isdriver else None);at(7,station_check);at(9,transferred);at(11,returned);at(19,treated);at(20,lambda:key('W',True) if isdriver else None);at(23,moving_reject);at(25,moving_transfer);at(28,moving_transferred);at(30,finish)
def tick(dt):
 try:
  if events and time.time()-start>=events[0][0]:_,fn=events.pop(0);fn()
 except Exception as e:check('harness_exception',False,repr(e));events.clear();finish()
handle=unreal.register_slate_post_tick_callback(tick)
