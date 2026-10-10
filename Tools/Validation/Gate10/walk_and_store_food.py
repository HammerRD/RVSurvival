"""Walk to perpendicular exterior-compartment access, then normal UI selection."""
import unreal,time,math,json,gc,traceback,sys
from pathlib import Path
out=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate10Validation');start=time.time();last=start;phase=0;event=0;handle=None;before=[]
def pc():return next(unreal.GameplayStatics.get_player_controller(w,0) for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='WNY_PrototypeRegion' and unreal.GameplayStatics.get_game_mode(w) and unreal.GameplayStatics.get_player_controller(w,0))
def p():return pc().get_controlled_pawn()
def inv():return p().get_component_by_class(unreal.RVInventoryComponent)
def cargo():return unreal.GameplayStatics.get_all_actors_of_class(p(),unreal.RVExteriorStoragePoint)[0]
def items(c):return [{'id':unreal.GuidLibrary.conv_guid_to_string(i.id),'definition':i.definition.get_path_name(),'quantity':i.quantity,'condition':i.condition} for i in c.get_items()]
def key(k,on):unreal.RVInteriorMotorhome.dispatch_development_key(pc(),k,on)
def finish():
 global handle
 a=items(inv());b=items(cargo().container);food=next(x for x in before if '/DA_Food.' in x['definition'])
 (out/'normal-store-conservation.json').write_text(json.dumps({'pass':food in b and all(x['id']!=food['id'] for x in a),'evidence':'W perpendicular approach/E/Down/T normal inputs; no direct transfer fixture','before':before,'player_after':a,'cargo_after':b,'feedback':inv().feedback},indent=2))
 key('W',False);unreal.unregister_slate_post_tick_callback(handle);handle=None;gc.collect()
def tick(dt):
 global phase,last,event,handle,before
 try:
  now=time.time()
  if phase==0:before=items(inv());key('I',True);phase=1;last=now
  elif phase==1 and now-last>.5:key('I',False);phase=2
  elif phase==2:
   v=unreal.GameplayStatics.get_all_actors_of_class(p(),unreal.RVInteriorMotorhome)[0];q=v.get_actor_transform().inverse_transform_location(cargo().get_actor_location());target=v.get_actor_transform().transform_location(unreal.Vector(q.x,q.y-190,q.z));pos=p().get_actor_location();dx=target.x-pos.x;dy=target.y-pos.y;distance=math.hypot(dx,dy)
   pc().set_control_rotation(unreal.Rotator(yaw=math.degrees(math.atan2(dy,dx))));key('W',distance>30)
   if distance<30:key('W',False);pc().set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p().get_actor_eyes_view_point()[0],cargo().get_actor_location()));key('E',True);phase=3;last=now
  elif phase==3 and now-last>.5:key('E',False);phase=4;last=now
  elif phase==4 and now-last>1:
   assert inv().open_container==cargo().container,'normal E cargo unavailable';phase=5;last=now
  elif phase==5 and now-last>.6:
   seq=[('Down',True),('Down',False)]*4+[('T',True),('T',False)]
   key(*seq[event]);event+=1;last=now
   if event==len(seq):phase=6
  elif phase==6 and now-last>1:finish()
  if handle and now-start>30:raise RuntimeError('walking/storage timeout')
 except Exception:
  (out/'walk-store-error.txt').write_text(traceback.format_exc());key('W',False);unreal.unregister_slate_post_tick_callback(handle);handle=None
  for k in ['last_traceback','last_value','last_type','last_exc']:
   if hasattr(sys,k):setattr(sys,k,None)
  gc.collect()
handle=unreal.register_slate_post_tick_callback(tick)
