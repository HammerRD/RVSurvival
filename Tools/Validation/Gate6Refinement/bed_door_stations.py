import unreal,json
B='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate6Refinement/'
w=next(w for w in unreal.ObjectIterator(unreal.World) if 'UEDPIE_' in w.get_path_name() and w.get_name()=='Gate6FuelElectricalTest')
pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn();v=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSystemsMotorhome)[0]
m=p.get_component_by_class(unreal.CharacterMovementComponent);f=p.get_component_by_class(unreal.RVPassengerReferenceFrameComponent);pose=p.get_component_by_class(unreal.RVRestPoseComponent);cap=p.get_component_by_class(unreal.CapsuleComponent);camera=p.get_component_by_class(unreal.CameraComponent);n=pc.player_state.get_component_by_class(unreal.RVNeedsComponent)
bed=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVRestPoint) if str(a.get_editor_property('DisplayName'))=='Rear bed');door=v.get_editor_property('HouseDoor')
rows=[];events=[];t=0;idx=0;before=0;walk_direction=1;blocker=None;station_count=0;station=None
def at(s,fn):events.append((s,fn))
def check(name,ok,detail=''):r={'case':name,'pass':bool(ok),'detail':str(detail)};rows.append(r);unreal.log('REFINE '+json.dumps(r))
def key(k,on):unreal.SystemLibrary.execute_console_command(pc,'Input.'+('+' if on else '-')+'key '+k,pc)
def local():return v.get_actor_transform().inverse_transform_location(p.get_actor_location())
def place(q):p.set_actor_location(v.get_actor_transform().transform_location(unreal.Vector(*q)),False,True)
def aim(a):pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p.get_actor_location()+unreal.Vector(0,0,p.get_editor_property('BaseEyeHeight')),a.get_actor_location()))
def awake():return n.get_editor_property('State').rest_mode==unreal.RVRestMode.AWAKE and pose.get_editor_property('RestPoint') is None and m.get_editor_property('MovementMode')==unreal.MovementMode.MOVE_WALKING
def bed_check(i):
 check('bed_reserved_'+str(i),n.get_editor_property('State').rest_mode==unreal.RVRestMode.RESTING and bed.get_editor_property('Occupant')==pc.player_state)
 check('lying_pose_collision_camera_'+str(i),pose.get_editor_property('RestPoint')==bed and str(cap.get_collision_enabled()).find('NO_COLLISION')>=0 and abs(camera.get_editor_property('RelativeLocation').z-35)<.01,{'local':str(local()),'collision':str(cap.get_collision_enabled())})
 check('bed_position_'+str(i),-315<local().x<-275 and abs(local().y)<5 and 195<local().z<215,local())
def wake_check(i):
 check('safe_wake_'+str(i),awake() and bed.get_editor_property('Occupant') is None and f.get_editor_property('ReferenceFrame')==v and -225<local().x<-105 and abs(local().y)<5,local())
 check('camera_collision_restored_'+str(i),abs(camera.get_editor_property('RelativeLocation').z-64)<.01 and str(cap.get_collision_enabled()).find('QUERY_AND_PHYSICS')>=0,str(cap.get_collision_enabled()))
def walk():
 global before,walk_direction
 before=local().x;walk_direction=-1 if before>100 else 1
 pc.set_control_rotation(unreal.Rotator(yaw=v.get_actor_rotation().yaw+(180 if walk_direction<0 else 0)));key('W',True)
at(0,lambda:(unreal.SystemLibrary.execute_console_command(pc,'rv.Needs.AllowDebug 1',pc),check('real_separate_door_actor',door is not None and not door.get_editor_property('bOpen')),place((92.4,275,100))))
at(1,lambda:aim(door));at(1.2,lambda:key('E',True));at(2,lambda:key('E',False));at(2.5,lambda:check('door_opens_native_hold',door.get_editor_property('bOpen')))
at(3,lambda:aim(door));at(3.2,lambda:key('E',True));at(4,lambda:key('E',False));at(4.5,lambda:check('door_closes_native_hold',not door.get_editor_property('bOpen')))
at(5,lambda:aim(door));at(5.2,lambda:key('E',True));at(6,lambda:key('E',False));at(6.5,lambda:check('door_reopens',door.get_editor_property('bOpen')))
for i in range(3):
 s=8+i*10
 at(s,lambda:place((-180,0,195)));at(s+.5,lambda:aim(bed));at(s+.7,lambda:key('E',True));at(s+1.5,lambda:key('E',False));at(s+2,lambda i=i:bed_check(i))
 at(s+2.2,lambda:key('Z',True));at(s+2.4,lambda:key('Z',False));at(s+3,lambda i=i:check('sleep_mode_'+str(i),n.get_editor_property('State').rest_mode==unreal.RVRestMode.SLEEPING,{'mode':str(n.get_editor_property('State').rest_mode),'feedback':n.get_editor_property('Feedback')}))
 at(s+3.2,lambda:key('R',True));at(s+3.4,lambda:key('R',False));at(s+4.2,lambda i=i:wake_check(i))
 at(s+4.5,walk);at(s+5.5,lambda:key('W',False));at(s+6,lambda i=i:check('walk_away_after_bed_'+str(i),awake() and local().x>before+60,local()))
def prep_station(a):
 global station,station_count
 station=a;station_count=a.get_editor_property('InteractionCount');q=v.get_actor_transform().inverse_transform_location(a.get_actor_location());place((q.x if q.x<140 else 130,0,195));aim(a)
stations=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVInteriorStation)
for i,a in enumerate(stations):
 s=40+i*5
 at(s,lambda a=a:prep_station(a));at(s+.6,lambda a=a:aim(a));at(s+.8,lambda:key('E',True));at(s+1.6,lambda:key('E',False))
 at(s+2,lambda a=a:check('station_use_'+str(a.get_editor_property('StationName')),a.get_editor_property('InteractionCount')==station_count+1))
 at(s+2.2,lambda:key('Escape',True));at(s+2.4,lambda:key('Escape',False));at(s+2.5,walk);at(s+3.3,lambda:key('W',False))
 at(s+4,lambda a=a:check('station_walk_away_'+str(a.get_editor_property('StationName')),awake() and (local().x-before)*walk_direction>30 and f.get_editor_property('ReferenceFrame')==v,local()))
def visual_check():
 points=stations+unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVInventoryInteractable)+unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVVehicleEntryPoint)
 bad=[]
 for a in points:
  if a.get_attach_parent_actor()==v and not isinstance(a,unreal.RVWorldItem):
   for c in a.get_components_by_class(unreal.StaticMeshComponent):
    if not c.get_editor_property('bHiddenInGame'):bad.append(a.get_name()+':'+c.get_name())
 check('all_RV_debug_targets_hidden',not bad,bad)
at(72,visual_check)
def tick(dt):
 global t,idx
 t+=dt
 try:
  while idx<len(events) and t>=events[idx][0]:events[idx][1]();idx+=1
  if t>75:unreal.unregister_slate_post_tick_callback(h);json.dump({'results':rows},open(B+'bed_door_stations.json','w'),indent=2)
 except Exception as e:
  check('exception',False,repr(e));unreal.unregister_slate_post_tick_callback(h);json.dump({'results':rows},open(B+'bed_door_stations.json','w'),indent=2)
h=unreal.register_slate_post_tick_callback(tick)
