"""Native E parked/moving workstation regression for the configured humanoid."""
"""Rear seating, moving pantry UI, exterior contention and ladder real-input paths.
Only initial/isolated exterior approach fixtures and item seeding use authority helpers.
No seat, rest, door, transfer or climb gameplay RPC shortcut is called.
"""
import unreal,json,time,os,math
from pathlib import Path
B=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate9Validation')
session=json.loads((B/'session.json').read_text());config=session['config'];start=session['start']
w=next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='Gate9CombatInfectedTest' and unreal.GameplayStatics.get_player_controller(w,0) and unreal.GameplayStatics.get_player_controller(w,0).get_controlled_pawn())
authority=unreal.GameplayStatics.get_game_mode(w) is not None
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
exitpoint=None
pantry=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVStoragePoint) if str(a.get_editor_property('Container').get_editor_property('DisplayName'))=='Pantry')
exterior=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVExteriorStoragePoint) if str(a.get_editor_property('DoorPartName'))=='Art_RV_Van_Compartment_01')
ladder=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVLadder)[0]
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
def aim_eye(point):
 origin=p.get_actor_eyes_view_point()[0]
 if p.get_editor_property('bUseControllerRotationYaw'):
  profile=p.get_component_by_class(unreal.RVCharacterPresentationComponent).get_editor_property('Profile');offset=profile.get_editor_property('OwnerCameraOffset');position=p.get_actor_location();angle=math.atan2(point.y-position.y,point.x-position.x)
  origin=position+unreal.Vector(math.cos(angle)*offset.x-math.sin(angle)*offset.y,math.sin(angle)*offset.x+math.cos(angle)*offset.y,p.get_editor_property('BaseEyeHeight')+offset.z)
 return origin


def aim(a):
    point=a.get_editor_property('DoorCollision').get_world_location() if isinstance(a,unreal.RVInteractiveDoor) else a.get_actor_location()
    pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(aim_eye(point),point))
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

def key(k,on):unreal.RVInteriorMotorhome.dispatch_development_key(pc,k,on)

at(0,setup);at(1,lambda:aim(de if isdriver else pe));at(1.2,lambda:key('E',True));at(2.1,lambda:key('E',False))
at(3.5,lambda:check('normal_E_initial_seats',driver.get_editor_property('Occupant')==dp and passenger.get_editor_property('Occupant')==wp))
tap(4,'Three','walker');at(5.5,lambda:check('normal_3_standing',walking(wp)))
at(6,lambda:key('W',True) if isdriver else None)
at(7,lambda:aim(fe) if not isdriver else None);at(7.2,lambda:key('E',True) if not isdriver else None);at(8.1,lambda:key('E',False) if not isdriver else None)
at(9,lambda:check('moving_front_bench_native_E',front.get_editor_property('Occupant')==wp and v.get_velocity().length()>150,local(wp)))
tap(9.5,'E','walker');at(10.8,lambda:check('moving_front_bench_stand',walking(wp) and wp.get_component_by_class(unreal.RVPassengerReferenceFrameComponent).get_editor_property('ReferenceFrame')==v,local(wp)))
def approach_rear_bench():
    if not isdriver:pc.set_control_rotation(unreal.Rotator(yaw=v.get_actor_rotation().yaw+180));key('W',True)
at(10.85,approach_rear_bench);at(11.4,lambda:key('W',False) if not isdriver else None)
at(11.5,lambda:aim(re) if not isdriver else None);at(11.7,lambda:key('E',True) if not isdriver else None);at(12.6,lambda:key('E',False) if not isdriver else None)
at(13.2,lambda:check('moving_rear_bench_native_E',rear.get_editor_property('Occupant')==wp,local(wp)))
tap(13.5,'E','walker');at(14.8,lambda:check('moving_rear_bench_stand',walking(wp) and wp.get_component_by_class(unreal.RVPassengerReferenceFrameComponent).get_editor_property('ReferenceFrame')==v,local(wp)))
at(15,lambda:aim(pantry) if not isdriver else None);at(15.2,lambda:key('E',True) if not isdriver else None);at(16.1,lambda:key('E',False) if not isdriver else None)
def pantry_view_check():
    if authority or not isdriver:
        check('moving_pantry_native_E',inventory(wp).get_editor_property('OpenContainer')==pantry.get_editor_property('Container'))
    else:
        # OpenContainer is intentionally owner-only; shared contents below are public.
        check('other_player_pantry_view_is_private',inventory(wp).get_editor_property('OpenContainer') is None)
at(17,pantry_view_check)
at(17,lambda:key('A',True) if isdriver else None)
tap(17.5,'T','walker');at(19,lambda:check('moving_turn_transfer_to_pantry_native_T',quantity(pantry.get_editor_property('Container'))==1 and quantity(inventory(wp))==0))
at(19,lambda:key('A',False) if isdriver else None)
tap(19.5,'Tab','walker');tap(20.5,'T','walker')
at(22,lambda:check('moving_transfer_back_native_Tab_T',quantity(pantry.get_editor_property('Container'))==0 and quantity(inventory(wp))==1 and abs(inventory(wp).get_items()[0].condition-.62)<.001,{'pantry':quantity(pantry.get_editor_property('Container')),'player':quantity(inventory(wp)),'feedback':inventory(wp).get_editor_property('Feedback'),'open':str(inventory(wp).get_editor_property('OpenContainer'))}))
tap(22.5,'I','walker')

# Stop the isolated moving fixture before relocating exterior approach positions.
def parked_fixture():
 if isdriver:key('W',False);key('SpaceBar',True)
 if authority:
  v.get_editor_property('Mesh').set_physics_linear_velocity(unreal.Vector(),False)
  v.get_editor_property('Mesh').set_physics_angular_velocity_in_degrees(unreal.Vector(),False)
at(24,parked_fixture);tap(26,'Three','driver')
at(28,lambda:check('driver_returned_survivor',walking(dp)))

def exterior_approach():
 if authority:
  q=v.get_actor_transform().inverse_transform_location(exterior.get_actor_location());side=1 if q.y>0 else -1
  place(hp,(q.x-45,side*300,95));place(cp,(q.x+45,side*300,95));seed(exterior.get_editor_property('Container'),'Tool')
at(29,exterior_approach);at(30,lambda:aim(exterior));at(30.2,lambda:key('E',True));at(31.1,lambda:key('E',False))
at(32.5,lambda:check('exterior_normal_E',inventory(p).get_editor_property('OpenContainer')==exterior.get_editor_property('Container')))
tap(33,'Tab','driver');tap(34,'T')
def conserved():
 if not authority:return
 records=[item for c in [inventory(hp),inventory(cp),exterior.get_editor_property('Container')] for item in c.get_items() if str(item.definition.get_editor_property('CatalogId'))=='Tool']
 check('container_contention_no_duplication',sum(item.quantity for item in records)==1 and len({str(item.id) for item in records})==len(records))
at(36,conserved);tap(36.2,'I');tap(37,'I');tap(37.5,'Tab');tap(38,'G','walker')
water_id=None
def water_world():return next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVWorldItem) if str(a.get_editor_property('Item').definition.get_editor_property('CatalogId'))=='Water' and abs(a.get_editor_property('Item').condition-.62)<.001)
def dropped():
 global water_id
 item=water_world().get_editor_property('Item');water_id=item.id
 check('native_G_drop_condition',item.quantity==1 and abs(item.condition-.62)<.001)
 if not isdriver:aim(water_world())
at(39.5,dropped);at(39.7,lambda:key('E',True) if not isdriver else None);at(40.6,lambda:key('E',False) if not isdriver else None)
def repicked():
 if authority or not isdriver:
  water=next(i for i in inventory(wp).get_items() if str(i.definition.get_editor_property('CatalogId'))=='Water')
  check('native_E_repick_identity',unreal.GuidLibrary.equal_equal_guid_guid(water.id,water_id) and abs(water.condition-.62)<.001,{'world_id':unreal.GuidLibrary.conv_guid_to_string(water_id),'inventory_id':unreal.GuidLibrary.conv_guid_to_string(water.id),'condition':water.condition})
at(42,repicked)
# Capacity and needs are unchanged low-level diagnostic smoke; explicit owned RPC.
def needs_fixture():
 if not authority:return
 cmd('rv.Needs.AllowDebug 1')
 needs=wp.get_editor_property('PlayerState').get_component_by_class(unreal.RVNeedsComponent)
 check('needs_set_fixture',needs.debug_set_values(40,40,40));needs.debug_set_time_scale(0);needs.debug_advance_time(3600)
 state=needs.get_editor_property('State');check('needs_hour_drain',state.nutrition<40 and state.hydration<state.nutrition and state.fatigue>40)
 needs.debug_set_values(40,40,40)
 inv=inventory(wp);item=next(i for i in inv.get_items() if str(i.definition.get_editor_property('CatalogId'))=='Water')
 weight=inv.get_editor_property('MaxWeightKg');volume=inv.get_editor_property('MaxVolumeLitres');inv.set_editor_property('MaxWeightKg',0);check('weight_capacity_reject',bool(inv.can_accept(item)));inv.set_editor_property('MaxWeightKg',weight);inv.set_editor_property('MaxVolumeLitres',0);check('volume_capacity_reject',bool(inv.can_accept(item)));inv.set_editor_property('MaxVolumeLitres',volume)
at(43,needs_fixture)
def consume():
 if isdriver:return
 needs=p.get_editor_property('PlayerState').get_component_by_class(unreal.RVNeedsComponent)
 needs.request_consume(water_id);needs.request_consume(water_id)
at(44,consume)
def consumed():
 if authority or not isdriver:
  needs=wp.get_editor_property('PlayerState').get_component_by_class(unreal.RVNeedsComponent)
  check('owned_consume_once',not any(unreal.GuidLibrary.equal_equal_guid_guid(i.id,water_id) for i in inventory(wp).get_items()) and abs(needs.get_editor_property('State').hydration-75)<.1)
  check('medical_component_and_active',wp.get_editor_property('PlayerState').get_editor_property('Health').can_act())
at(46,consumed)
def finish():
 global active
 for k in ['E','W','S','A','D','G','I','Tab','T','Three','SpaceBar']:key(k,False)
 role='server' if authority else 'client';(B/(config['name']+'_'+role+'.json')).write_text(json.dumps({'pid':os.getpid(),'role':role,'results':results,'samples':samples},indent=2))
 active=False;unreal.unregister_slate_post_tick_callback(h)
at(48,finish);events.sort(key=lambda e:e[0])
def tick(dt):
 global idx,input_frame,nextsample
 input_frame+=1;t=time.time()-start
 if not active or t<0:return
 try:
  for k,(deadline,frame) in list(pulses.items()):
   if time.time()>=deadline and input_frame>=frame:key(k,False);del pulses[k]
  while idx<len(events) and t>=events[idx][0] and not pulses:
   fn=events[idx][1];idx+=1;fn()
   if not active:return
 except Exception as e:check('exception',False,repr(e));finish()
h=unreal.register_slate_post_tick_callback(tick)

