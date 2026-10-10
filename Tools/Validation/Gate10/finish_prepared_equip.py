"""Prepare the player using actual side-door traversal and authored world pickups."""
import unreal,time,json,math,gc,traceback
from pathlib import Path
out=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate10Validation');started=time.time();handle=None;phase=5;index=0;held={};last=0;rows=[];outside=None;current=''
def w():return next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='WNY_PrototypeRegion' and unreal.GameplayStatics.get_game_mode(w) and unreal.GameplayStatics.get_player_controller(w,0))
def pc():return unreal.GameplayStatics.get_player_controller(w(),0)
def p():return pc().get_controlled_pawn()
def rv():return unreal.GameplayStatics.get_all_actors_of_class(w(),unreal.RVInteriorMotorhome)[0]
def key(k,on):
 if held.get(k,False)!=on:unreal.RVInteriorMotorhome.dispatch_development_key(pc(),k,on);held[k]=on
def walk(x,y,range_cm=45):
 q=p().get_actor_location();d=math.hypot(x-q.x,y-q.y);pc().set_control_rotation(unreal.Rotator(yaw=math.degrees(math.atan2(y-q.y,x-q.x))));key('W',d>range_cm);return d<=range_cm
def sample(label):
 inv=p().get_component_by_class(unreal.RVInventoryComponent);rows.append({'stage':label,'position':str(p().get_actor_location()),'items':[{'id':unreal.GuidLibrary.conv_guid_to_string(i.id),'definition':i.definition.get_path_name(),'quantity':i.quantity,'rounds':i.magazine_rounds} for i in inv.get_items()]})
def finish(result):
 global handle
 for k in list(held):key(k,False)
 unreal.unregister_slate_post_tick_callback(handle);handle=None
 (out/'normal-starting-supplies.json').write_text(json.dumps({'result':result,'evidence':'E side door/W physical walking/E pickup/4 equip/R reload; no inventory grant or location fixture','samples':rows},indent=2));gc.collect()
def tick(dt):
 global phase,index,last,outside,current
 try:
  t=time.time()-started
  if phase==5 and t<.1:key('Four',True)
  elif phase==0:
   door=unreal.GameplayStatics.get_all_actors_of_class(w(),unreal.RVInteractiveDoor)[0];a=door.get_editor_property('DoorCollision').get_world_location();q=rv().get_actor_transform().inverse_transform_location(a);outside=rv().get_actor_transform().transform_location(unreal.Vector(q.x,q.y+300,q.z));pc().set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p().get_actor_eyes_view_point()[0],a));key('E',True);phase=1;last=t
  elif phase==1 and t-last>.15:key('E',False);phase=2
  elif phase==2 and t-last>1:
   if walk(outside.x,outside.y):sample('physical door exit');phase=3
  elif phase==3:
   pickups=[a for a in unreal.GameplayStatics.get_all_actors_of_class(w(),unreal.RVWorldItem) if a.item.definition and a.get_actor_location().distance(rv().get_actor_location())<3000]
   if not pickups:sample('all starting pickups');key('Four',True);phase=5;last=t;return
   a=min(pickups,key=lambda a:a.get_actor_location().distance(p().get_actor_location()));q=a.get_actor_location()
   if walk(q.x,q.y-130):current=a.item.definition.get_path_name();origin,extent,radius=unreal.SystemLibrary.get_component_bounds(a.get_component_by_class(unreal.StaticMeshComponent));pc().set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p().get_actor_eyes_view_point()[0],origin));key('E',True);phase=4;last=t
  elif phase==4 and t-last>.15:key('E',False);phase=8
  elif phase==8 and t-last>.6:sample('pickup '+current);phase=3
  elif phase==5 and t-last>.15:key('Four',False);phase=6
  elif phase==6 and t-last>.5:key('R',True);phase=7
  elif phase==7 and t-last>.7:key('R',False);phase=9
  elif phase==9 and t-last>4:sample('prepared');finish('starting pickup and firearm input completed; inspect presentation/ammo')
  if handle and t>50:finish('timeout; no pass')
 except Exception:(out/'normal-starting-supplies-error.txt').write_text(traceback.format_exc());finish('error; not accepted')
handle=unreal.register_slate_post_tick_callback(tick)


