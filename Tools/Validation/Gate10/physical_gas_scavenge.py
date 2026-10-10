"""Continue parked route with real E exit, walking and E/T scavenging input."""
import unreal,time,json,math,gc,traceback
from pathlib import Path
out=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate10Validation');started=time.time();handle=None;stage=0;index=0;held={};rows=[];last=0
route=[(-131500,3500),(-130000,5000),(-130000,6250),(-130400,6620)]
def w():return next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='WNY_PrototypeRegion' and unreal.GameplayStatics.get_game_mode(w) and unreal.GameplayStatics.get_player_controller(w,0))
def pc():return unreal.GameplayStatics.get_player_controller(w(),0)
def p():return pc().get_controlled_pawn()
def key(k,on):
 if held.get(k,False)!=on:unreal.RVInteriorMotorhome.dispatch_development_key(pc(),k,on);held[k]=on
def container():return next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w(),unreal.RVScavengeContainer) if 'Pine Creek packaged' in str(a.container.display_name))
def sample(label):
 pawn=p();q=pawn.get_actor_location();inv=pawn.get_component_by_class(unreal.RVInventoryComponent)
 rows.append({'stage':label,'position':[q.x,q.y,q.z],'pawn':pawn.get_class().get_name(),'movement':str(pawn.character_movement.movement_mode) if hasattr(pawn,'character_movement') else '', 'inventory':len(inv.get_items()) if inv else 0,'feedback':inv.feedback if inv else ''})
def finish(result):
 global handle
 for k in list(held):key(k,False)
 unreal.unregister_slate_post_tick_callback(handle);handle=None
 (out/'physical-gas-scavenge.json').write_text(json.dumps({'result':result,'evidence':'continued actual driven parking with normal E exit/W walking/E interaction/T transfer; no pawn relocation','samples':rows},indent=2));gc.collect()
def tick(dt):
 global stage,index,last
 try:
  t=time.time()-started
  if stage==0:stage=1;key('E',True)
  elif stage==1 and t>.15:stage=2;key('E',False)
  elif stage==2 and t>1:
   assert not isinstance(p(),unreal.RVInteriorMotorhome),'exit failed';sample('normal exit');stage=3
  elif stage==3:
   pawn=p();q=pawn.get_actor_location();target=route[index];dx=target[0]-q.x;dy=target[1]-q.y;distance=math.hypot(dx,dy)
   pc().set_control_rotation(unreal.Rotator(yaw=math.degrees(math.atan2(dy,dx))))
   key('W',distance>55)
   if t-last>3:last=t;sample('walking '+str(index))
   if distance<=55:
    if index<len(route)-1:index+=1
    else:
     key('W',False);pc().set_control_rotation(unreal.MathLibrary.find_look_at_rotation(pawn.get_actor_eyes_view_point()[0],container().get_actor_location()));key('E',True);stage=4;last=t
   if t>50:finish('walking timeout; no pass')
  elif stage==4 and t-last>.15:key('E',False);stage=5
  elif stage==5 and t-last>1:
   inv=p().get_component_by_class(unreal.RVInventoryComponent);sample('container opened');assert inv.open_container==container().container,'E did not open intended container';key('T',True);stage=6
  elif stage==6 and t-last>1.15:key('T',False);stage=7
  elif stage==7 and t-last>2:sample('after normal T');finish('normal walking entrance and container input executed; inspect inventory conservation')
 except Exception:
  (out/'physical-gas-scavenge-error.txt').write_text(traceback.format_exc());finish('error; not accepted')
handle=unreal.register_slate_post_tick_callback(tick)
