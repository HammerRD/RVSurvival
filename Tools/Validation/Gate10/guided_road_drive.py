"""Development input driver: normal E/W/A/D/S, no physics/velocity fixture."""
import unreal,time,json,math,gc,traceback
from pathlib import Path
out=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate10Validation');started=time.time();handle=None;held={};stage=0;index=0;samples=[];last=0
route=[(-155000,0),(-136000,0),(-132000,0),(-130500,2500)]
def w():return next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='WNY_PrototypeRegion' and unreal.GameplayStatics.get_game_mode(w) and unreal.GameplayStatics.get_player_controller(w,0))
def pc():return unreal.GameplayStatics.get_player_controller(w(),0)
def rv():return unreal.GameplayStatics.get_all_actors_of_class(w(),unreal.RVInteriorMotorhome)[0]
def key(k,on):
 if held.get(k,False)!=on:unreal.RVInteriorMotorhome.dispatch_development_key(pc(),k,on);held[k]=on
def setup():
 v=rv();p=pc().get_controlled_pawn();entry=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w(),unreal.RVVehicleEntryPoint) if a.seat and a.seat.get_editor_property('bDriverSeat'))
 q=v.get_actor_transform().inverse_transform_location(entry.get_actor_location());p.set_actor_location(v.get_actor_transform().transform_location(unreal.Vector(q.x,q.y-125 if q.y<0 else q.y+125,100)),False,True);p.character_movement.stop_movement_immediately();pc().set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p.get_actor_eyes_view_point()[0],entry.get_actor_location()))
 p.get_component_by_class(unreal.RVInventoryComponent).request_close_container();unreal.SystemLibrary.execute_console_command(pc(),'t.MaxFPS 60',pc())
def finish(result):
 global handle
 for k in list(held):key(k,False)
 unreal.unregister_slate_post_tick_callback(handle);handle=None
 (out/'guided-road-drive.json').write_text(json.dumps({'result':result,'evidence':'E/W/A/D/S normal Enhanced Input paths; initial placement beside driver entry only','route_cm':route,'samples':samples},indent=2));gc.collect()
def tick(dt):
 global stage,index,last
 try:
  t=time.time()-started
  if stage==0:stage=1;setup()
  elif stage==1 and t>1:stage=2;key('E',True)
  elif stage==2 and t>1.8:stage=3;key('E',False)
  elif stage==3 and t>3:
   assert pc().get_controlled_pawn()==rv(),'Normal E did not possess driver';stage=4
  elif stage==4:
   v=rv();p=v.get_actor_location();speed=v.get_velocity().length();target=route[index];dx=target[0]-p.x;dy=target[1]-p.y;distance=math.hypot(dx,dy)
   if distance<700 and index<len(route)-1:index+=1;return
   yaw=math.degrees(math.atan2(dy,dx));error=(yaw-v.get_actor_rotation().yaw+180)%360-180
   target_speed=1800 if index<2 else 700
   braking=index==len(route)-1 and distance<max(700,speed*speed/800+250)
   key('D',error>1.5 and not braking);key('A',error< -1.5 and not braking);key('W',speed<target_speed and not braking);key('S',speed>target_speed+100 or (braking and speed>30));key('SpaceBar',braking and speed<100)
   if t-last>2:last=t;samples.append({'t':round(t,2),'position':[p.x,p.y,p.z],'speed_cm_s':speed,'yaw':v.get_actor_rotation().yaw,'route_index':index,'error_deg':error})
   if braking and speed<30:finish('stopped near gas approach; visual/exit/scavenge pending')
   elif t>100:finish('timeout; not accepted')
 except Exception:
  (out/'guided-road-drive-error.txt').write_text(traceback.format_exc());finish('error; not accepted')
handle=unreal.register_slate_post_tick_callback(tick)
