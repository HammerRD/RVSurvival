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

ps=wp.get_editor_property('PlayerState');health=ps.get_editor_property('Health');needs=ps.get_editor_property('Needs');bed=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVRestPoint) if str(a.get_editor_property('DisplayName'))=='Rear bed');ids=[]
def snapshot():return [(unreal.GuidLibrary.conv_guid_to_string(i.id),str(i.kind),str(i.region)) for i in health.get_editor_property('Injuries')]
def fixture():
 setup()
 if authority:health.debug_apply_injury(unreal.RVInjuryKind.FRACTURE,unreal.RVBodyRegion.LEFT_ARM,1)
 if config.get('network'):
  for k,val in [('PktLagMin',100),('PktLagMax',100),('PktLoss',2)]:cmd('NetEmulation.'+k+' '+str(val))
def initial():
 global ids
 ids=snapshot();check('injury_present_seated',len(ids)==1 and passenger.get_editor_property('Occupant')==wp)
def standing():check('injury_survives_rear_transition',snapshot()==ids and walking(wp),local(wp))
def tobed():
 if authority:place(wp,(-115,0,180))
def bedcheck():check('injury_survives_normal_E_bed',snapshot()==ids and bed.get_editor_property('Occupant')==ps,local(wp))
def sleepcheck():check('medical_survives_normal_Z_sleep',snapshot()==ids and needs.get_editor_property('State').rest_mode==unreal.RVRestMode.SLEEPING)
def wakecheck():check('medical_survives_normal_R_wake',snapshot()==ids and walking(wp) and bed.get_editor_property('Occupant') is None,local(wp))
def down():
 if authority:health.debug_set_vitals(20,20)
def down_action():
 if not isdriver:
  unreal.RVInteriorMotorhome.dispatch_development_key(pc,'W',True);pulses['W']=(time.time()+.5,input_frame+3)
  inventory(wp).request_drop(inventory(wp).get_items()[0].id,1)
  needs.request_rest_mode(unreal.RVRestMode.SLEEPING)
def downcheck():
 check('downed_native_walk_restricted',not health.can_act() and health.get_movement_scale()==0)
 check('downed_drop_retains_item',quantity(inventory(wp))==1)
 check('downed_sleep_rejected',needs.get_editor_property('State').rest_mode==unreal.RVRestMode.AWAKE and bed.get_editor_property('Occupant') is None)
 check('injury_retained_downed',snapshot()==ids)
def finish():
 for k in list(pulses):unreal.RVInteriorMotorhome.dispatch_development_key(pc,k,False)
 unreal.unregister_slate_post_tick_callback(handle);(B/(config['name']+'_'+role+'.json')).write_text(json.dumps({'pid':os.getpid(),'role':role,'results':results,'fixture':'authority positions at bed approach; all seat/bed controls normal input'},indent=2))
at(0,fixture);at(1,lambda:aim(de if isdriver else pe));at(1.2,lambda:key('E',True));at(2.1,lambda:key('E',False));at(3.5,initial);tap(4,'Three','walker');at(6,standing);at(7,tobed);at(9,lambda:aim(bed) if not isdriver else None);at(9.2,lambda:key('E',True) if not isdriver else None);at(10.2,lambda:key('E',False) if not isdriver else None);at(12,bedcheck);tap(13,'Z','walker');at(15,sleepcheck);tap(16,'R','walker');at(19,wakecheck);at(20,down);at(22,down_action);at(25,downcheck);at(27,finish)
def tick(dt):
 global input_frame
 input_frame+=1
 try:
  for k,(deadline,frame) in list(pulses.items()):
   if time.time()>=deadline and input_frame>=frame:unreal.RVInteriorMotorhome.dispatch_development_key(pc,k,False);del pulses[k]
  if events and time.time()-start>=events[0][0]:_,fn=events.pop(0);fn()
 except Exception as e:check('harness_exception',False,repr(e));events.clear();finish()
handle=unreal.register_slate_post_tick_callback(tick)

