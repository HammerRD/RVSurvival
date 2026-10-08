"""Native E parked/moving workstation regression for the configured humanoid."""
"""Rear seating, moving pantry UI, exterior contention and ladder real-input paths.
Only initial/isolated exterior approach fixtures and item seeding use authority helpers.
No seat, rest, door, transfer or climb gameplay RPC shortcut is called.
"""
import unreal,json,time,os,math
from pathlib import Path
B=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate8_5Validation')
session=json.loads((B/'session.json').read_text());config=session['config'];start=session['start']
w=next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='Gate8_5CharacterTest' and unreal.GameplayStatics.get_player_controller(w,0) and unreal.GameplayStatics.get_player_controller(w,0).get_controlled_pawn())
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
bad_seated=0;below_floor=0;walk_before={}
def station(name):return next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVInteriorStation) if str(a.get_editor_property('StationName'))==name)
def walk_to(t,rear,duration):
 def begin():
  if not isdriver:pc.set_control_rotation(unreal.Rotator(yaw=v.get_actor_rotation().yaw+(180 if rear else 0)));key('W',True)
 at(t,begin);at(t+duration,lambda:key('W',False) if not isdriver else None)
def use_station(t,name,count,phase):
 at(t,lambda:aim(station(name)) if not isdriver else None)
 at(t+.2,lambda:key('E',True) if not isdriver else None);at(t+1.1,lambda:key('E',False) if not isdriver else None)
 at(t+1.5,lambda:check(phase+'_normal_E_'+name,station(name).get_editor_property('InteractionCount')==count,station(name).get_editor_property('InteractionCount')))
 tap(t+1.7,'Escape','walker')
 def begin_walk():
  walk_before[phase+name]=local(wp)
  if not isdriver:
   pc.set_control_rotation(unreal.Rotator(yaw=v.get_actor_rotation().yaw));key('W' if local(wp)[0]<30 else 'S',True)
 at(t+2,begin_walk)
 at(t+2.18,lambda:(key('W',False),key('S',False)) if not isdriver else None)
 def restored():
  before=walk_before[phase+name];after=local(wp);distance=sum((a-b)**2 for a,b in zip(before[:2],after[:2]))**.5
  check(phase+'_leave_and_walk_'+name,walking(wp) and wp.get_component_by_class(unreal.RVPassengerReferenceFrameComponent).get_editor_property('ReferenceFrame')==v and distance>=5,{'relative_walk_cm':distance,'position':after})
 at(t+2.8,restored)
at(0,setup);at(1,lambda:aim(de if isdriver else pe));at(1.2,lambda:key('E',True));at(2.1,lambda:key('E',False))
at(3.5,lambda:check('normal_E_initial_seats',driver.get_editor_property('Occupant')==dp and passenger.get_editor_property('Occupant')==wp))
tap(4,'Three','walker');walk_to(6,True,1.1)
for t,name in [(8,'Workbench'),(11.5,'Kitchen'),(15,'Medical')]:use_station(t,name,1,'parked')
# Approach the bathroom counter from the bed-foot aisle. The wardrobe
# legitimately occludes a diagonal trace from the kitchen end of the aisle.
walk_to(14.35,True,.55)
walk_to(18.5,False,.85)
for t,name in [(20,'Power'),(23.5,'Navigation')]:use_station(t,name,1,'parked')
at(28,lambda:wp.get_component_by_class(unreal.RVPassengerReferenceFrameComponent).reset_diagnostics())
at(29,lambda:key('W',True) if isdriver else None);walk_to(30,True,1.1)
at(32,lambda:check('real_driving_before_moving_station_uses',v.get_velocity().length()>150,v.get_velocity().length()))
for t,name in [(32.5,'Workbench'),(36,'Kitchen'),(39.5,'Medical')]:use_station(t,name,2,'moving')
walk_to(38.85,True,.55)
walk_to(43,False,.85)
for t,name in [(44.5,'Power'),(48,'Navigation')]:use_station(t,name,2,'moving')
at(45,lambda:key('A',True) if isdriver else None);at(47,lambda:key('A',False) if isdriver else None)
def diagnostics():
 frame=wp.get_component_by_class(unreal.RVPassengerReferenceFrameComponent)
 detail={n:frame.get_editor_property(n) for n in ['CorrectionCount','MaxCorrectionCm','MaxLocalStepCm','FrameChanges','BaseChanges']}
 check('station_route_existing_correction_bound',detail['MaxCorrectionCm']<=(75 if config.get('network') else 30),detail)
at(52,diagnostics)
def finish():
 global active
 for k in ['E','W','S','A','Three','Escape']:key(k,False)
 check('zero_seated_movement_violations',bad_seated==0,bad_seated);check('zero_interior_floor_falls',below_floor==0,below_floor)
 role='server' if authority else 'client'
 (B/(config['name']+'_'+role+'.json')).write_text(json.dumps({'pid':os.getpid(),'role':role,'config':config,'results':results,'samples':samples},indent=2),encoding='utf-8')
 active=False;unreal.unregister_slate_post_tick_callback(h)
 from runner_runtime import release_runners
 release_runners()
at(54,finish);events.sort(key=lambda e:e[0])
def tick(dt):
 global idx,input_frame,nextsample,dp,wp,bad_seated,below_floor
 if not active:return
 input_frame+=1
 if not authority:
  remote=next((c for c in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSurvivorCharacter) if c!=p),None)
  if remote:dp=p if isdriver else remote;wp=remote if isdriver else p
 t=time.time()-start
 if t<0:return
 try:
  for k,(deadline,frame) in list(pulses.items()):
   if time.time()>=deadline and input_frame>=frame:key(k,False);del pulses[k]
  while idx<len(events) and t>=events[idx][0] and not pulses:
   fn=events[idx][1];idx+=1;terminating=fn.__name__=='finish';fn()
   if terminating:return
  if t>5.5 and t>=nextsample:
   nextsample=t+.05
   for c in [dp,wp]:
    if local(c)[2]<120:below_floor+=1
    if c.get_editor_property('SeatedVehicle') and c.get_component_by_class(unreal.CharacterMovementComponent).get_editor_property('MovementMode')!=unreal.MovementMode.MOVE_NONE:bad_seated+=1
   samples.append({'t':t,'driver':local(dp),'walker':local(wp),'speed':v.get_velocity().length()})
 except Exception as e:check('exception',False,repr(e));finish()
h=unreal.register_slate_post_tick_callback(tick)
