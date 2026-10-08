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
medical=wp.get_editor_property('PlayerState').get_editor_property('Health')
walk_start=None
def medical_seed():
 setup()
 if authority:
  medical.debug_apply_injury(unreal.RVInjuryKind.WOUND,unreal.RVBodyRegion.LEFT_ARM,1)
  item=unreal.RVItemInstance();item.set_editor_property('Id',unreal.GuidLibrary.new_guid());item.set_editor_property('Definition',unreal.load_asset('/Game/Medical/DA_Bandage'));item.set_editor_property('Quantity',2);item.set_editor_property('Condition',.77);inventory(wp).add_authority(item)
 if config.get('network'):
  for k,value in [('PktLagMin',100),('PktLagMax',100),('PktLoss',2)]:cmd('NetEmulation.'+k+' '+str(value))
def treat():
 if not isdriver:
  i=medical.get_editor_property('Injuries')[0];s=next(i for i in inventory(wp).get_items() if i.definition.get_editor_property('Medical').get_editor_property('bMedicalSupply'))
  medical.request_treatment(wp.get_editor_property('PlayerState'),i.id,s.id,i.revision)
def treated():
 global walk_start
 check('moving_bandage_completed',medical.get_editor_property('Injuries')[0].bleeding_per_minute==0,medical.get_editor_property('Feedback'))
 check('moving_supply_consumed_once',sum(i.quantity for i in inventory(wp).get_items() if i.definition.get_editor_property('Medical').get_editor_property('bMedicalSupply'))==1)
 check('moving_frame_intact',wp.get_component_by_class(unreal.RVPassengerReferenceFrameComponent).get_editor_property('ReferenceFrame')==v and 140<local(wp)[2]<230,local(wp))
 check('vehicle_actually_moving',v.get_velocity().length()>200,v.get_velocity().length())
 walk_start=local(wp)
def walk():
 if not isdriver:pc.set_control_rotation(unreal.Rotator(yaw=v.get_actor_rotation().yaw+180));unreal.RVInteriorMotorhome.dispatch_development_key(pc,'W',True);pulses['W']=(time.time()+.6,input_frame+3)
def walked():
 q=local(wp);f=wp.get_component_by_class(unreal.RVPassengerReferenceFrameComponent)
 check('normal_walk_after_medical',q[0]<walk_start[0]-20 and 140<q[2]<230 and f.get_editor_property('ReferenceFrame')==v,{'local':q,'before':walk_start,'corrections':f.get_editor_property('CorrectionCount'),'max_cm':f.get_editor_property('MaxCorrectionCm')})
def finish():
 if isdriver:key('W',False);key('S',False)
 for k in list(pulses):unreal.RVInteriorMotorhome.dispatch_development_key(pc,k,False)
 unreal.unregister_slate_post_tick_callback(handle)
 (B/(config['name']+'_'+role+'.json')).write_text(json.dumps({'pid':os.getpid(),'role':role,'config':config,'kind':'normal seat/drive/walk input; medical owned RPC diagnostic','results':results,'samples':samples},indent=2))
at(0,medical_seed);at(1,lambda:aim(de if isdriver else pe));at(1.2,lambda:key('E',True));at(2.1,lambda:key('E',False))
at(3.5,lambda:check('normal_E_initial_seats',driver.get_editor_property('Occupant')==dp and passenger.get_editor_property('Occupant')==wp))
tap(4,'Three','walker');at(5.5,lambda:check('normal_3_standing',walking(wp)))
at(5.6,lambda:wp.get_component_by_class(unreal.RVPassengerReferenceFrameComponent).reset_diagnostics())
at(6,lambda:key('W',True) if isdriver else None);at(9,treat);at(15,treated)
at(15.5,lambda:key('D',True) if isdriver else None);at(16.2,lambda:key('D',False) if isdriver else None);at(17,walk);at(20,walked)
at(21,lambda:key('W',False) if isdriver else None);at(22,lambda:key('S',True) if isdriver else None);at(26,lambda:key('S',False) if isdriver else None);at(28,finish)
def tick(dt):
 global input_frame,nextsample
 input_frame+=1
 try:
  for k,(deadline,frame) in list(pulses.items()):
   if time.time()>=deadline and input_frame>=frame:unreal.RVInteriorMotorhome.dispatch_development_key(pc,k,False);del pulses[k]
  if events and time.time()-start>=events[0][0]:_,fn=events.pop(0);fn()
  if time.time()>nextsample:
   nextsample=time.time()+.5;samples.append({'t':time.time()-start,'speed':v.get_velocity().length(),'passenger_local':local(wp)})
 except Exception as e:check('harness_exception',False,repr(e));events.clear();finish()
handle=unreal.register_slate_post_tick_callback(tick)




