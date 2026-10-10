"""Normal driver E/accelerator/brake paths on saved roads; no velocity fixture."""
import unreal,time,json,traceback,gc
from pathlib import Path
out=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate10Validation');started=time.time();handle=None;done=set();samples=[];initial=None
def world():return next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='WNY_PrototypeRegion' and unreal.GameplayStatics.get_game_mode(w) and unreal.GameplayStatics.get_player_controller(w,0))
def pc():return unreal.GameplayStatics.get_player_controller(world(),0)
def rv():return unreal.GameplayStatics.get_all_actors_of_class(world(),unreal.RVInteriorMotorhome)[0]
def key(k,on):unreal.RVInteriorMotorhome.dispatch_development_key(pc(),k,on)
def setup():
 v=rv();p=pc().get_controlled_pawn();entry=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world(),unreal.RVVehicleEntryPoint) if a.seat and a.seat.get_editor_property('bDriverSeat'))
 q=v.get_actor_transform().inverse_transform_location(entry.get_actor_location());p.set_actor_location(v.get_actor_transform().transform_location(unreal.Vector(q.x,q.y-125 if q.y<0 else q.y+125,100)),False,True)
 p.character_movement.stop_movement_immediately();pc().set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p.get_actor_eyes_view_point()[0],entry.get_actor_location()))
 inv=p.get_component_by_class(unreal.RVInventoryComponent);inv.request_close_container()
 unreal.SystemLibrary.execute_console_command(pc(),'t.MaxFPS 60',pc())
def capture(name):
 global initial
 v=rv();q=v.get_actor_location();speed=v.get_velocity().length();p=pc().get_controlled_pawn()
 if initial is None:initial=[q.x,q.y,q.z]
 samples.append({'stage':name,'vehicle_position':[q.x,q.y,q.z],'speed_cm_s':speed,'driver_possession':p==v,'vehicle_rotation':str(v.get_actor_rotation()),'travel_cm':unreal.Vector(q.x-initial[0],q.y-initial[1],0).length()})
 unreal.SystemLibrary.execute_console_command(pc(),'shot showui filename='+str(out/('manual-drive-'+name+'.png')).replace('\\','/')+' -nosuffix',pc())
def finish():
 global handle
 for k in ['E','W','S','SpaceBar']:key(k,False)
 key('SpaceBar',True)
 unreal.unregister_slate_post_tick_callback(handle);handle=None
 (out/'manual-drive-probe.json').write_text(json.dumps({'evidence':'normal E seat interaction/W throttle/S brake; development placement beside driver entry only; no forced velocity','samples':samples},indent=2));gc.collect()
def tick(dt):
 try:
  t=time.time()-started
  actions=[(0,'setup',setup),(1,'enter_down',lambda:key('E',True)),(1.8,'enter_up',lambda:key('E',False)),(3,'start',lambda:capture('parked')),(3.2,'throttle',lambda:key('W',True)),(8,'low',lambda:capture('low-speed')),(15,'road',lambda:capture('road-speed')),(22,'high',lambda:capture('highway')),(23,'throttle_off',lambda:key('W',False)),(23.1,'brake',lambda:key('S',True)),(29,'brake_off',lambda:key('S',False)),(29.1,'park',lambda:key('SpaceBar',True)),(32,'stopped',lambda:capture('stopped')),(33,'finish',finish)]
  for at,name,fn in actions:
   if t>=at and name not in done:done.add(name);fn();break
 except Exception:
  (out/'manual-drive-probe-error.txt').write_text(traceback.format_exc());finish()
handle=unreal.register_slate_post_tick_callback(tick)
