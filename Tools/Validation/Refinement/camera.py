import unreal,json,time
B='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate5Refinement/'
w=next(w for w in unreal.ObjectIterator(unreal.World) if 'UEDPIE_' in w.get_path_name() and w.get_name()=='Gate5SurvivalTest');pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn();v=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVInteriorMotorhome)[0];arm=v.get_component_by_class(unreal.SpringArmComponent);cam=v.get_component_by_class(unreal.CameraComponent)
e=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVVehicleEntryPoint) if a.get_editor_property('Seat').get_editor_property('bDriverSeat') and abs(v.get_actor_transform().inverse_transform_location(a.get_actor_location()).y)>100)
rows=[];samples=[];events=[];idx=0;t=0;acc=0;target_speed=None;held=set();obstacle=None;initial_yaw=0

def cmd(s):unreal.SystemLibrary.execute_console_command(pc,s,pc)
def key(k,on):
 cmd('Input.'+('+' if on else '-')+'key '+k)
 if k in ['W','S']:
  if on:held.add(k)
  else:held.discard(k)
def speed(s):
 global target_speed
 target_speed=s
 for k in list(held):key(k,False)
def loc():q=v.get_actor_transform().inverse_transform_location(cam.get_world_location());return [q.x,q.y,q.z]
def check(n,ok,d=''):rows.append({'case':n,'pass':bool(ok),'detail':str(d)});unreal.log('REFINE_CAM '+json.dumps(rows[-1]))
def snap(n):
 cmd('shot filename='+B+'camera_'+n+'.png -nosuffix');check(n+'_camera_clear',loc()[0]<-900 and loc()[2]>550 and not arm.is_collision_fix_applied(),{'camera_local':loc(),'speed':v.get_velocity().length(),'yaw':v.get_actor_rotation().yaw,'view':str(cam.get_world_rotation())})
def setup():
 pos=e.get_actor_location()-v.get_actor_right_vector()*180;pos.z=92;p.set_actor_location(pos,False,True);pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(pos+unreal.Vector(0,0,64),e.get_actor_location()))
 check('saved_tunable_config',arm.get_editor_property('TargetArmLength')==1400 and cam.get_editor_property('FieldOfView')==85 and arm.get_editor_property('bDoCollisionTest'))
def turn_start():
 global initial_yaw
 initial_yaw=v.get_actor_rotation().yaw;key('D 0.12',True)
def make_obstacle(x):
 global obstacle
 q=v.get_actor_transform().transform_location(unreal.Vector(x,0,450))
 if obstacle is None:
  obstacle=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.StaticMeshActor) if a.get_actor_label().startswith('Gate2_Reference'));assert 'UEDPIE_' in obstacle.get_path_name();m=obstacle.get_component_by_class(unreal.StaticMeshComponent);m.set_mobility(unreal.ComponentMobility.MOVABLE);m.set_collision_profile_name('BlockAll');m.set_world_scale3d(unreal.Vector(1,5,7));obstacle.set_actor_rotation(unreal.Rotator(yaw=v.get_actor_rotation().yaw),True);obstacle.set_actor_location(q,False,True)
 else:obstacle.set_actor_location(q,False,True)
def obstruction_check(name,limit):
 actual=cam.get_world_location();desired=arm.get_unfixed_camera_position();c=loc();cmd('shot filename='+B+'camera_'+name+'.png -nosuffix');check(name,arm.is_collision_fix_applied() and (actual-desired).length()>300 and c[0]>limit and c[2]>330,{'camera_local':c,'retraction':(actual-desired).length()})
def finish():
 speed(None)
 for k in ['W','S','D','SpaceBar','E']:key(k,False)
 json.dump({'results':rows,'samples':samples},open(B+'camera.json','w'),indent=2);unreal.unregister_slate_post_tick_callback(h)
def at(t,f):events.append((t,f))
cmd('t.MaxFPS 60');cmd('t.IdleWhenNotForeground 0')
at(0,setup);at(.5,lambda:key('E',True));at(1.5,lambda:key('E',False));at(2.5,lambda:check('native_driver_camera',pc.get_controlled_pawn()==v));at(3,lambda:speed(500));at(7,lambda:(check('low_speed',250<v.get_velocity().length()<850,v.get_velocity().length()),snap('low')));at(8,lambda:speed(1800));at(18,lambda:(check('road_speed',v.get_velocity().length()>1400,v.get_velocity().length()),snap('road')));at(19,lambda:speed(2700));at(32,lambda:(check('approximately_60mph',v.get_velocity().length()>2500,v.get_velocity().length()),snap('highway')))
at(33,turn_start);at(34.2,lambda:key('D',False));at(36,lambda:(check('turn_camera_follows_yaw',abs(v.get_actor_rotation().yaw-initial_yaw)>5 and abs(unreal.MathLibrary.normalized_delta_rotator(cam.get_world_rotation(),v.get_actor_rotation()).yaw)<1),snap('turn')))
at(38,lambda:(speed(None),key('S',True)));at(42,lambda:(key('S',False),key('SpaceBar',True)));at(46,lambda:(key('SpaceBar',False),key('S',True)));at(49,lambda:(check('actual_reverse',v.get_velocity().dot(v.get_actor_forward_vector())<-50,v.get_velocity().dot(v.get_actor_forward_vector())),snap('reverse')));at(50,lambda:(key('S',False),key('SpaceBar',True)));at(58,lambda:check('stopped_for_obstacle',v.get_velocity().length()<50,v.get_velocity().length()));at(59,lambda:make_obstacle(-900));at(60,lambda:obstruction_check('boom_obstacle',-870));at(62,lambda:make_obstacle(-470));at(63,lambda:obstruction_check('near_obstacle',-440));at(65,lambda:obstacle.destroy_actor());at(66,lambda:(check('camera_recovers_after_obstacle',not arm.is_collision_fix_applied() and (cam.get_world_location()-arm.get_unfixed_camera_position()).length()<1),snap('recovered')));at(68,finish)
def tick(dt):
 global t,idx,acc
 t+=dt;acc+=dt
 try:
  while idx<len(events) and t>=events[idx][0]:events[idx][1]();idx+=1
  if t>=68:return
  if target_speed is not None:
   s=v.get_velocity().length()
   for k,on in [('W',s<target_speed-25),('S',s>target_speed+50)]:
    if (k in held)!=on:key(k,on)
  if acc>.1:acc=0;samples.append({'t':t,'speed':v.get_velocity().length(),'camera_local':loc(),'collision_fix':arm.is_collision_fix_applied(),'vehicle_pitch':v.get_actor_rotation().pitch,'vehicle_roll':v.get_actor_rotation().roll})
 except Exception as ex:check('exception',False,repr(ex));finish()
h=unreal.register_slate_post_tick_callback(tick)
