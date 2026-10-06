import unreal,json,math
B='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate5FrontAudit/'
w=next(w for w in unreal.ObjectIterator(unreal.World) if 'UEDPIE_' in w.get_path_name() and w.get_name()=='Gate5SurvivalTest')
pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn()
v=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVInteriorMotorhome)[0]
cap=p.get_component_by_class(unreal.CapsuleComponent);frame=p.get_component_by_class(unreal.RVPassengerReferenceFrameComponent)
t=0;idx=0;events=[];results=[];samples=[];active_case=None;route_target=None;trace_results=[];route_waypoint=0
def local(a):q=v.get_actor_transform().inverse_transform_location(a);return [q.x,q.y,q.z]
def check(n,ok,d=''):r={'case':n,'pass':bool(ok),'detail':str(d)};results.append(r);unreal.log('FRONT_AUDIT '+json.dumps(r))
def key(k,on):unreal.SystemLibrary.execute_console_command(pc,'Input.'+('+' if on else '-')+'key '+k,pc)
def setup(n,start,target,jump=False):
 global active_case
 key('W',False);key('SpaceBar',False);p.get_component_by_class(unreal.CharacterMovementComponent).stop_movement_immediately();active_case=n
 p.set_actor_location(v.get_actor_transform().transform_location(unreal.Vector(start[0],start[1],100)),False,True)
 yaw=math.degrees(math.atan2(target[1]-start[1],target[0]-start[0]))+v.get_actor_rotation().yaw
 pc.set_control_rotation(unreal.Rotator(yaw=yaw))
def blocked(n,axis,value,greater):
 key('W',False);key('SpaceBar',False);q=local(p.get_actor_location())
 ok=q[axis]>value if greater else q[axis]<value
 if n.startswith('front_corner'):ok=all(not (220<r['position'][0]<407 and abs(r['position'][1])<106) and not(-364<r['position'][0]<=230 and abs(r['position'][1])<120) for r in samples if r['case']==n)
 check(n,ok and frame.get_editor_property('ReferenceFrame') is None,{'position':q,'capsule_radius':cap.get_unscaled_capsule_radius()})
def screenshot(n,pitch=0):
 r=pc.get_control_rotation();r.pitch=pitch;pc.set_control_rotation(r)
 unreal.SystemLibrary.execute_console_command(pc,'shot filename='+B+n+'.png -nosuffix',pc)
def at(t,f):events.append((t,f))
cases=[
 ('front_center',(500,0),(300,0),0,435,True),
 ('front_left',(500,-75),(300,-75),0,435,True),
 ('front_right',(500,75),(300,75),0,435,True),
 ('front_center_jump',(500,0),(300,0),0,435,True),
 ('cab_right',(310,300),(310,0),1,135,True),
 ('cab_left',(310,-300),(310,0),1,-135,False),
 ('front_wheel_right',(296,300),(296,0),1,135,True),
 ('front_wheel_left',(296,-300),(296,0),1,-135,False),
 ('front_corner_right',(500,140),(300,80),1,130,True),
 ('front_corner_left',(500,-140),(300,-80),1,-130,False),
 ('side_right_middle',(-25,300),(-25,0),1,150,True),
 ('side_left_middle',(-25,-300),(-25,0),1,-150,False),
 ('rear_wheel_right',(-115,300),(-115,0),1,150,True),
 ('rear_wheel_left',(-115,-300),(-115,0),1,-150,False),
 ('rear_right',(-315,300),(-315,0),1,150,True),
 ('rear_left',(-315,-300),(-315,0),1,-150,False),
 ('rear_center',(-500,0),(-300,0),0,-390,False),
 ('rear_corner_right',(-500,100),(-300,60),0,-390,False),
 ('rear_corner_left',(-500,-100),(-300,-60),0,-390,False)]
for i,(n,start,target,axis,val,gt) in enumerate(cases):
 a=i*4
 at(a,lambda n=n,start=start,target=target:setup(n,start,target))
 at(a+.3,lambda:key('W',True))
 if n.endswith('jump'):
  at(a+.6,lambda:key('SpaceBar',True));at(a+.85,lambda:key('SpaceBar',False))
 at(a+2.5,lambda n=n,axis=axis,val=val,gt=gt:blocked(n,axis,val,gt))
 if n in ['front_center','front_left','front_right','cab_left','rear_center']:at(a+2.8,lambda n=n:screenshot(n))
def finish():
 key('W',False);key('SpaceBar',False);unreal.unregister_slate_post_tick_callback(h)
 json.dump({'results':results,'structural_traces':trace_results,'samples':samples,'trace_api':str(unreal.SystemLibrary.line_trace_single.__doc__),'sweep_api':str(unreal.SystemLibrary.sphere_trace_single.__doc__)},open(B+'exterior.json','w'),indent=2)

def trace(a,b):
 hit=unreal.SystemLibrary.line_trace_single(w,v.get_actor_transform().transform_location(unreal.Vector(*a)),v.get_actor_transform().transform_location(unreal.Vector(*b)),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,False,[p],unreal.DrawDebugTrace.NONE,True)
 return {'blocking':True} if hit is not None else None
def survey():
 checks=[
 ('bumper',(500,0,40),(350,0,40),'FrontFascia'),
 ('grille',(500,0,100),(350,0,100),'FrontFascia'),
 ('fascia_upper',(500,0,150),(350,0,150),'FrontFascia'),
 ('hood',(320,0,240),(320,0,100),'HoodTop'),
 ('engine_side_right',(310,220,90),(310,0,90),'CabExteriorRight'),
 ('engine_side_left',(310,-220,90),(310,0,90),'CabExteriorLeft'),
 ('firewall',(280,0,115),(160,0,115),'FrontWall'),
 ('rear',( -480,0,135),(-250,0,135),'RearWall'),
 ('house_left',(-100,-220,135),(-100,0,135),'LeftWall'),
 ('house_right',(-100,220,135),(-100,0,135),'RightWallRear'),
 ('windshield_cab_boundary',(450,0,220),(150,0,220),'FrontWall'),
 ('under_front_body',(500,0,20),(300,0,20),'FrontFascia')]
 for n,a,b,expected in checks:
  hit=trace(a,b);trace_results.append({'case':n,'hit':hit})
  check('structural_'+n,hit is not None,hit)
 check('unchanged_capsule',cap.get_unscaled_capsule_radius()==34)
 # Report the deliberately open mechanical underside separately; do not pretend it is a closed hull.
 trace_results.append({'case':'engine_underside_inspection','hit':trace((320,0,-10),(320,0,120))})
def route_start():
 global active_case,route_target,route_waypoint
 setup('continuous_walkaround',(470,0),(470,260))
 active_case='continuous_walkaround';route_target=(470,260);route_waypoint=0
def route_done():
 global route_target
 key('W',False);route_target=None
 check('complete_continuous_walkaround',route_waypoint==5,{'waypoints_completed':route_waypoint,'position':local(p.get_actor_location())})
at(76,survey);at(77,route_start);at(92,route_done);at(93,finish)

def tick(dt):
 global t,idx,route_target,route_waypoint
 t+=dt
 try:
  while idx<len(events) and t>=events[idx][0]:f=events[idx][1];idx+=1;f()
  if route_target is not None:
   q=local(p.get_actor_location());dx=route_target[0]-q[0];dy=route_target[1]-q[1]
   if math.hypot(dx,dy)<12:
    route_waypoint+=1;targets=[(-440,260),(-440,-260),(470,-260),(470,0)]
    if route_waypoint<=4:route_target=targets[route_waypoint-1]
    else:route_target=None;key('W',False)
   else:
    pc.set_control_rotation(unreal.Rotator(yaw=math.degrees(math.atan2(dy,dx))+v.get_actor_rotation().yaw));key('W',True)
  if idx<len(events):
   cm=pc.get_player_view_point()[0] if hasattr(pc,'get_player_view_point') else p.get_actor_location()+unreal.Vector(0,0,64)
   samples.append({'t':t,'case':active_case,'position':local(p.get_actor_location()),'eye':local(cm)})
 except Exception as e:check('exception',False,repr(e));finish()
h=unreal.register_slate_post_tick_callback(tick)
