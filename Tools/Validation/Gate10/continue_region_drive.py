"""Normal-input continuation after the conserved food transfer, not vehicle teleport."""
import unreal,time,json,math,gc,traceback,sys
from pathlib import Path
out=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate10Validation');start=time.time();handle=None;phase=0;held={};path_index=0;route_index=0;last=0;distance=0;previous=None;samples=[];walk_points=[];route=[];frame_times=[]

def world():return next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='WNY_PrototypeRegion' and unreal.GameplayStatics.get_game_mode(w) and unreal.GameplayStatics.get_player_controller(w,0))
def pc():return unreal.GameplayStatics.get_player_controller(world(),0)
def pawn():return pc().get_controlled_pawn()
def rv():return unreal.GameplayStatics.get_all_actors_of_class(world(),unreal.RVInteriorMotorhome)[0]
def entry():return next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world(),unreal.RVVehicleEntryPoint) if a.seat and a.seat.get_editor_property('bDriverSeat'))
def key(k,on):
 if held.get(k,False)!=on:unreal.RVInteriorMotorhome.dispatch_development_key(pc(),k,on);held[k]=on
def make_route():
 controls=[(-127000,0),(-60000,0),(-60000,-3500),(-62500,-6500),(-62500,-11000),(-60000,-11000),(-58000,-12500),(-63000,-12500),(-62500,-6500),(-60000,-3500),(-60000,0),(-80000,0),(-60000,22000),(0,45000),(75000,45000),(120000,18000),(130000,0),(140000,0),(170000,0)]
 points=[controls[0]]
 for a,b in zip(controls,controls[1:]):
  count=max(1,math.ceil(math.dist(a,b)/4000))
  points.extend((a[0]+(b[0]-a[0])*i/count,a[1]+(b[1]-a[1])*i/count) for i in range(1,count+1))
 return points
def prepare():
 global walk_points,route
 assert json.loads((out/'normal-store-conservation.json').read_text())['pass'],'Store conservation must pass before continuation.'
 v=rv();q=v.get_actor_transform().inverse_transform_location(pawn().get_actor_location());e=v.get_actor_transform().inverse_transform_location(entry().get_actor_location());side=e.y-175 if e.y<0 else e.y+175
 walk_points=[v.get_actor_transform().transform_location(unreal.Vector(q.x,side,100)),v.get_actor_transform().transform_location(unreal.Vector(e.x,side,100))]
 route=make_route();key('I',True)
def finish(result):
 global handle
 for k in list(held):key(k,False)
 unreal.unregister_slate_post_tick_callback(handle);handle=None
 ordered=sorted(frame_times)
 (out/'continued-region-drive.json').write_text(json.dumps({'result':result,'evidence':'I/W/E physical driver approach then W/A/D/S/Space normal input; no character/vehicle transform or velocity fixture','distance_km':distance/100000,'route_points':route,'samples':samples,'sampled_game_frame_ms':{'median':ordered[len(ordered)//2] if ordered else None,'p95':ordered[min(len(ordered)-1,int(len(ordered)*.95))] if ordered else None},'performance_scope':'development PIE sample, not a hardware-independent benchmark'},indent=2))
 for k in ['last_traceback','last_value','last_type','last_exc']:
  if hasattr(sys,k):setattr(sys,k,None)
 gc.collect()
def tick(dt):
 global phase,path_index,route_index,last,distance,previous
 try:
  t=time.time()-start
  if phase==0:phase=1;prepare()
  elif phase==1 and t>.4:key('I',False);phase=2
  elif phase==2:
   q=pawn().get_actor_location();goal=walk_points[path_index];dx=goal.x-q.x;dy=goal.y-q.y;d=math.hypot(dx,dy)
   pc().set_control_rotation(unreal.Rotator(yaw=math.degrees(math.atan2(dy,dx))));key('W',d>45)
   if d<=45:
    if path_index<len(walk_points)-1:path_index+=1
    else:key('W',False);pc().set_control_rotation(unreal.MathLibrary.find_look_at_rotation(pawn().get_actor_eyes_view_point()[0],entry().get_actor_location()));key('E',True);phase=3;last=t
   if t>35:finish('driver approach timeout; not accepted')
  elif phase==3 and t-last>.8:key('E',False);phase=4;last=t
  elif phase==4 and t-last>1:
   assert pawn()==rv(),'Normal E did not enter driver seat';phase=5;last=t
  elif phase==5:
   v=rv();q=v.get_actor_location();speed=v.get_velocity().length();goal=route[route_index];d=math.hypot(goal[0]-q.x,goal[1]-q.y)
   if d<450 and route_index<len(route)-1:route_index+=1;return
   desired=math.degrees(math.atan2(goal[1]-q.y,goal[0]-q.x));error=(desired-v.get_actor_rotation().yaw+180)%360-180
   target_speed=1800 if abs(error)<12 else 550
   braking=route_index==len(route)-1 and d<max(800,speed*speed/800+200)
   key('D',error>1.5 and not braking);key('A',error< -1.5 and not braking);key('W',speed<target_speed and not braking);key('S',speed>target_speed+100 or (braking and speed>30));key('SpaceBar',braking and speed<150)
   if previous is not None:distance+=q.distance(unreal.Vector(*previous))
   previous=[q.x,q.y,q.z]
   if t-last>1:
    last=t;samples.append({'t':t,'position':previous,'speed_cm_s':speed,'route_index':route_index,'heading_error':error,'roll':v.get_actor_rotation().roll});frame_times.append(unreal.GameplayStatics.get_world_delta_seconds(world())*1000)
   if braking and speed<30:finish('continued driving route reached end and stopped; visual review required')
   elif abs(v.get_actor_rotation().roll)>65:finish('overturned during driving; not accepted')
   elif t>650:finish('route timeout; not accepted')
 except Exception:
  (out/'continued-region-drive-error.txt').write_text(traceback.format_exc());finish('error; not accepted')
handle=unreal.register_slate_post_tick_callback(tick)
