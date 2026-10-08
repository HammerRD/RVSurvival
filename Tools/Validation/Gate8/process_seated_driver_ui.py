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

ps=dp.get_editor_property('PlayerState');health=ps.get_editor_property('Health');inv=inventory(wp);nextsample=0;samples=[]
def medical_seed():
 cmd("rv.Medical.Debug 1")
 if authority:
  health.debug_apply_injury(unreal.RVInjuryKind.WOUND,unreal.RVBodyRegion.TORSO,2);health.debug_apply_injury(unreal.RVInjuryKind.FRACTURE,unreal.RVBodyRegion.LEFT_LEG,2);health.debug_set_vitals(20,20)
  for name in ['PressureDressing','FirstAidKit']:
   i=unreal.RVItemInstance();i.set_editor_property('Id',unreal.GuidLibrary.new_guid());i.set_editor_property('Definition',unreal.load_asset('/Game/Medical/DA_'+name));i.set_editor_property('Quantity',2);i.set_editor_property('Condition',.71);inv.add_authority(i)
 if config.get('network'):
  for k,val in [('PktLagMin',100),('PktLagMax',100),('PktLoss',2)]:cmd('NetEmulation.'+k+' '+str(val))
def finish():
 for k in list(pulses):unreal.RVInteriorMotorhome.dispatch_development_key(pc,k,False)
 unreal.unregister_slate_post_tick_callback(handle);(B/(config['name']+'_'+role+'.json')).write_text(json.dumps({'pid':os.getpid(),'role':role,'kind':'normal OS client F9/UMG; normal E/3 seat fixtures','results':results,'last_sample':samples[-1] if samples else {}},indent=2))
at(0,setup);at(1,lambda:aim(de if isdriver else pe));at(1.2,lambda:key('E',True));at(2.1,lambda:key('E',False));tap(4,'Three','walker');at(6,medical_seed)
def tick(dt):
 global input_frame,nextsample
 input_frame+=1
 try:
  for k,(deadline,frame) in list(pulses.items()):
   if time.time()>=deadline and input_frame>=frame:unreal.RVInteriorMotorhome.dispatch_development_key(pc,k,False);del pulses[k]
  if events and time.time()-start>=events[0][0]:_,fn=events.pop(0);fn()
  if time.time()>nextsample and time.time()-start>7:
   nextsample=time.time()+.5;row={'time':time.time(),'driver_pawn_playerstate_null':dp.get_editor_property('PlayerState') is None,'vehicle_playerstate_patient':v.get_editor_property('PlayerState')==ps,'patient_active':health.can_act(),'injuries':len(health.get_editor_property('Injuries')),'bleeding':health.get_editor_property('Injuries')[0].bleeding_per_minute,'distance_cm':(wp.get_actor_location()-dp.get_actor_location()).length(),'driver_seat_occupied':driver.get_editor_property('Occupant')==dp,'host_controller_possesses_vehicle':pc.get_controlled_pawn()==v if isdriver else None,'blood':ps.get_editor_property('MedicalAttributes').get_editor_property('Blood').get_editor_property('CurrentValue'),'supplies':[(str(i.definition.get_editor_property('DisplayName')),i.quantity) for i in inv.get_items()]};samples.append(row);(B/(config['name']+'_'+role+'_samples.json')).write_text(json.dumps(samples,indent=2))
  if time.time()-start>150 or ((B/'finish-driver-ui.flag').exists() and (B/'finish-driver-ui.flag').stat().st_mtime>start):
   check('driver_medical_state_remains_owned',v.get_editor_property('PlayerState')==ps and len(health.get_editor_property('Injuries'))==2);finish()
 except Exception as e:check('harness_exception',False,repr(e));events.clear();finish()
handle=unreal.register_slate_post_tick_callback(tick)
