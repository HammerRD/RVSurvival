"""Regraded-world route drive with normal input only: physical walk to the driver seat, E, W/A/D/S/Space, E exit and re-entry at the garage. No placement, velocity or transform fixtures."""
import unreal,time,json,math,gc,traceback,sys
from pathlib import Path
out=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate10Validation');docs=Path('D:/GitHub/RVSurvival/RVSurvival/Docs/Gate10Results')
start=time.time();handle=None;phase=0;held={};route_index=0;last=0;phase_at=0;distance=0;previous=None;samples=[];route=[];events=[];frame_times=[];slow_since=None
extremes={'max_abs_roll':0,'max_abs_pitch':0,'max_temperature_c':None,'min_speed_while_driving':None}
sites={'Pine Creek Fuel':(-130000,4900),'Erie Road Service':(-60000,-5500),'Erie garage parking':(-60000,-11000),'Hawthorne Farm':(0,46000),'Maple Run Campground':(75000,46000),'Rowland Crossroads':(140000,5000)}
closest={k:None for k in sites}
# Same controls as continue_region_drive.py; the garage parking stop is where the previous attempt stalled.
controls=[(-127000,0),(-60000,0),(-60000,-3500),(-62500,-6500),(-62500,-11000),(-60000,-11000),(-58000,-12500),(-63000,-12500),(-62500,-6500),(-60000,-3500),(-60000,0),(-80000,0),(-60000,22000),(0,45000),(75000,45000),(120000,18000),(130000,0),(140000,0),(170000,0)]
garage_stop=(-60000,-11000)
def world():return next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='WNY_PrototypeRegion' and unreal.GameplayStatics.get_game_mode(w) and unreal.GameplayStatics.get_player_controller(w,0))
def pc():return unreal.GameplayStatics.get_player_controller(world(),0)
def pawn():return pc().get_controlled_pawn()
def rv():return unreal.GameplayStatics.get_all_actors_of_class(world(),unreal.RVInteriorMotorhome)[0]
def entry():return next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world(),unreal.RVVehicleEntryPoint) if a.seat and a.seat.get_editor_property('bDriverSeat'))
def temperature():
 c=rv().get_component_by_class(unreal.RVCoolingComponent);return None if c is None else c.get_editor_property('cooling').get_editor_property('temperature_c')
def key(k,on):
 if held.get(k,False)!=on:unreal.RVInteriorMotorhome.dispatch_development_key(pc(),k,on);held[k]=on
def make_route(origin):
 points=[];controls_=[origin]+controls
 for a,b in zip(controls_,controls_[1:]):
  count=max(1,math.ceil(math.dist(a,b)/4000));points.extend((a[0]+(b[0]-a[0])*i/count,a[1]+(b[1]-a[1])*i/count) for i in range(1,count+1))
 return points
def ground(q):
 hit=unreal.SystemLibrary.line_trace_single(world(),unreal.Vector(q.x,q.y,q.z+500),unreal.Vector(q.x,q.y,q.z-3000),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,False,[rv()],unreal.DrawDebugTrace.NONE,True)
 t=hit.to_tuple() if hit else None
 if not t or not t[0]:return None
 return {'z':round(t[4].z,1),'actor':t[9].get_name() if t[9] else None}
walk_log=[];walk_best=None;walk_plan=[];walk_step=0;door_opened=False;reentry_planned=False
def to_world(x,y,z=100):return rv().get_actor_transform().transform_location(unreal.Vector(x,y,z))
def plan_exterior_path(from_inside):
 """Side door (if inside) -> around the cab front -> beside the driver entry, in RV local space."""
 t=rv().get_actor_transform();e=t.inverse_transform_location(entry().get_actor_location())
 origin,extent=rv().get_actor_bounds(True);corners=[t.inverse_transform_location(origin+unreal.Vector(sx*extent.x,sy*extent.y,0)) for sx in (-1,1) for sy in (-1,1)]
 xmax=max(c.x for c in corners);ymin=min(c.y for c in corners);ymax=max(c.y for c in corners)
 driver_y=ymin-175 if e.y<(ymin+ymax)/2 else ymax+175;plan=[]
 if from_inside:
  door=unreal.GameplayStatics.get_all_actors_of_class(world(),unreal.RVInteractiveDoor)[0];d=t.inverse_transform_location(door.get_editor_property('DoorCollision').get_world_location())
  door_y=ymax+200 if d.y>(ymin+ymax)/2 else ymin-200;plan.append((d.x,door_y))
  if (door_y>0)!=(driver_y>0):plan+= [(xmax+300,door_y),(xmax+300,driver_y)]
 plan.append((e.x,driver_y));return plan
def approach_entry(t,label):
 """Physical W walk along the exterior plan, then look at the driver entry and press E. Returns True when E is pressed."""
 global walk_step,walk_best
 p=pawn().get_actor_location();e=entry().get_actor_location()
 interaction=pawn().get_component_by_class(unreal.RVInteractionComponent);prompt=str(interaction.get_prompt())
 if walk_step<len(walk_plan):
  g=to_world(*walk_plan[walk_step]);d=math.hypot(g.x-p.x,g.y-p.y);pc().set_control_rotation(unreal.Rotator(yaw=math.degrees(math.atan2(g.y-p.y,g.x-p.x))));key('W',d>45)
  if d<=45:walk_step+=1
 else:
  pc().set_control_rotation(unreal.MathLibrary.find_look_at_rotation(pawn().get_actor_eyes_view_point()[0],e));d=math.hypot(e.x-p.x,e.y-p.y);key('W',d>120 and 'Enter' not in prompt)
 if not walk_log or t-walk_log[-1]['t']>1:walk_log.append({'stage':label,'t':round(t,2),'step':walk_step,'pawn':[round(p.x),round(p.y),round(p.z)],'entry':[round(e.x),round(e.y),round(e.z)],'distance':round(d),'prompt':prompt,'trace':str(interaction.debug_trace_description())})
 if walk_step>=len(walk_plan) and 'Enter' in prompt:events.append({'event':'E pressed','stage':label,'pawn':[round(p.x),round(p.y),round(p.z)],'prompt':prompt,'trace':str(interaction.debug_trace_description())});key('E',True);return True
 return False
def turn_deg(i):
 if i<=0 or i>=len(route)-1:return 0
 a=math.atan2(route[i][1]-route[i-1][1],route[i][0]-route[i-1][0]);b=math.atan2(route[i+1][1]-route[i][1],route[i+1][0]-route[i][0])
 return abs((math.degrees(b-a)+180)%360-180)
def corner_speed(q):
 """Route-follower lookahead only: slow early enough for the next sharp vertices (harness driving, not a vehicle rule)."""
 limit=1800;along=math.hypot(route[route_index][0]-q.x,route[route_index][1]-q.y)
 for i in range(route_index,min(len(route)-1,route_index+4)):
  if i>route_index:along+=math.dist(route[i-1],route[i])
  angle=turn_deg(i);v=450 if angle>90 else 650 if angle>45 else 1000 if angle>20 else 1800
  limit=min(limit,math.sqrt(v*v+2*350*max(0,along-300)))
 return limit
def finish(result):
 global handle
 for k in list(held):key(k,False)
 unreal.unregister_slate_post_tick_callback(handle);handle=None
 ordered=sorted(frame_times)
 receipt={'result':result,'evidence':'physical W walk to driver entry, E enter, W/A/D/S/SpaceBar driving, E exit/re-entry at garage; no character/vehicle transform or velocity fixture','distance_km':round(distance/100000,4),
  'events':events,'walk_log':walk_log,'extremes':extremes,'closest_approach_m':{k:None if v is None else round(v/100,1) for k,v in closest.items()},'route_points':route,'samples':samples,
  'sampled_game_frame_ms':{'median':ordered[len(ordered)//2] if ordered else None,'p95':ordered[min(len(ordered)-1,int(len(ordered)*.95))] if ordered else None}}
 (out/'regraded-route-drive.json').write_text(json.dumps(receipt,indent=2));docs.joinpath('regraded-route-drive.json').write_text(json.dumps(receipt,indent=2))
 for k in ['last_traceback','last_value','last_type','last_exc']:
  if hasattr(sys,k):setattr(sys,k,None)
 gc.collect();shutdown()
def shutdown():
 # After the receipt and with no UObject wrappers held: stop PIE, then quit the editor.
 state={'at':time.time(),'step':0,'h':None}
 def step(dt):
  if state['step']==0 and time.time()-state['at']>3:state['step']=1;unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
  elif state['step']==1 and time.time()-state['at']>10:state['step']=2;unreal.unregister_slate_post_tick_callback(state['h']);gc.collect();unreal.SystemLibrary.quit_editor()
 state['h']=unreal.register_slate_post_tick_callback(step)
def log(name,**data):
 q=rv().get_actor_location();events.append({'t':round(time.time()-start,2),'event':name,'rv':[round(q.x),round(q.y),round(q.z)],**data})
def tick(dt):
 global phase,route_index,last,phase_at,distance,previous,slow_since,route,walk_plan,walk_step,door_opened,reentry_planned
 try:
  t=time.time()-start
  if phase==0:
   unreal.SystemLibrary.execute_console_command(pc(),'t.MaxFPS 60',pc());q=rv().get_actor_location();route=make_route((q.x,q.y));phase=1;phase_at=t
  elif phase==1:
   # Walk the aisle to the driver entry with W only, then E.
   if not door_opened:
    door=unreal.GameplayStatics.get_all_actors_of_class(world(),unreal.RVInteractiveDoor)[0];pc().set_control_rotation(unreal.MathLibrary.find_look_at_rotation(pawn().get_actor_eyes_view_point()[0],door.get_editor_property('DoorCollision').get_world_location()));door=None
    if t-phase_at<.3:return
    key('E',True);door_opened=t;return
   if door_opened and not walk_plan:
    if t-door_opened<.2:return
    key('E',False)
    if t-door_opened<1:return
    walk_plan=plan_exterior_path(True);walk_step=0;events.append({'event':'exterior path','plan':walk_plan})
   if approach_entry(t,'initial'):phase=2;phase_at=t
   elif t-phase_at>30:finish('harness failure: driver-seat walk timeout; not a vehicle result')
  elif phase==2 and t-phase_at>1.2:key('E',False);phase=3;phase_at=t
  elif phase==3 and t-phase_at>1:
   if pawn()!=rv():
    finish('normal E did not enter driver seat');return
   log('entered driver seat');phase=4;phase_at=t
  elif phase==4:
   v=rv();q=v.get_actor_location();r=v.get_actor_rotation();speed=v.get_velocity().length();goal=route[route_index];d=math.hypot(goal[0]-q.x,goal[1]-q.y)
   for k,(sx,sy) in sites.items():
    s=math.hypot(sx-q.x,sy-q.y);closest[k]=s if closest[k] is None else min(closest[k],s)
   stop_here=math.dist(goal,garage_stop)<1 and not any(e['event']=='garage exit' for e in events)
   if d<450 and route_index<len(route)-1 and not stop_here:route_index+=1;return
   desired=math.degrees(math.atan2(goal[1]-q.y,goal[0]-q.x));error=(desired-r.yaw+180)%360-180
   target_speed=1800 if abs(error)<12 else 550
   if route_index>0 and math.dist(route[route_index-1],garage_stop)<9000 or math.dist(goal,garage_stop)<9000:target_speed=min(target_speed,700)
   target_speed=min(target_speed,corner_speed(q))
   braking=(route_index==len(route)-1 or stop_here) and d<max(800,speed*speed/800+200)
   key('D',error>1.5 and not braking);key('A',error< -1.5 and not braking);key('W',speed<target_speed and not braking);key('S',speed>target_speed+100 or (braking and speed>30));key('SpaceBar',braking and speed<150)
   if previous is not None:distance+=q.distance(unreal.Vector(*previous))
   previous=[q.x,q.y,q.z]
   extremes['max_abs_roll']=max(extremes['max_abs_roll'],abs(r.roll));extremes['max_abs_pitch']=max(extremes['max_abs_pitch'],abs(r.pitch))
   if not braking:
    slow_since=None if speed>=30 else (slow_since if slow_since is not None else t)
   if t-last>1:
    last=t;temp=temperature();extremes['max_temperature_c']=temp if extremes['max_temperature_c'] is None else max(extremes['max_temperature_c'],temp or 0)
    samples.append({'t':round(t,2),'position':[round(c,1) for c in previous],'speed_cm_s':round(speed,1),'route_index':route_index,'heading_error':round(error,2),'roll':round(r.roll,2),'pitch':round(r.pitch,2),'temperature_c':temp,'ground':ground(q)})
    frame_times.append(unreal.GameplayStatics.get_world_delta_seconds(world())*1000)
   if braking and speed<30 and stop_here:key('S',False);key('SpaceBar',False);log('garage stop',ground=ground(q),temperature_c=temperature());phase=5;phase_at=t
   elif braking and speed<30:log('route end stop',ground=ground(q),temperature_c=temperature());finish('route completed and stopped at the end; visual review required')
   elif abs(r.roll)>65:log('overturned',roll=r.roll);finish('overturned during driving; not accepted')
   elif slow_since is not None and t-slow_since>20:log('stall',ground=ground(q),temperature_c=temperature(),route_index=route_index);finish('stalled below 30 cm/s for 20 s while throttling; not accepted')
   elif t>900:finish('route timeout; not accepted')
  elif phase==5 and t-phase_at>1.5:pc().set_control_rotation(pc().get_control_rotation());key('E',True);phase=6;phase_at=t
  elif phase==6 and t-phase_at>1.2:key('E',False);phase=7;phase_at=t
  elif phase==7 and t-phase_at>1.5:
   if pawn()==rv():finish('normal E did not exit the driver seat at the garage');return
   q=pawn().get_actor_location();log('garage exit',character=[round(q.x),round(q.y),round(q.z)],character_ground=ground(q));phase=8;phase_at=t
  elif phase==8:
   # Re-enter with the same physical walk and E.
   if not reentry_planned:reentry_planned=True;walk_plan=plan_exterior_path(False);walk_step=0;events.append({'event':'re-entry path','plan':walk_plan})
   if approach_entry(t,'garage re-entry'):phase=9;phase_at=t
   elif t-phase_at>30:finish('harness failure: garage re-entry walk timeout after successful exit')
  elif phase==9 and t-phase_at>1.2:key('E',False);phase=10;phase_at=t
  elif phase==10 and t-phase_at>1:
   if pawn()!=rv():finish('normal E did not re-enter driver seat at the garage');return
   log('garage re-entry');route_index+=1;phase=4;phase_at=t
 except Exception:
  (out/'regraded-route-drive-error.txt').write_text(traceback.format_exc());finish('harness error; not accepted')
handle=unreal.register_slate_post_tick_callback(tick)
