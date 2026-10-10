import unreal,time,json,math,gc,traceback
from pathlib import Path
out=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate10Validation');started=time.time();handle=None;stage=0;index=0;held={};rows=[];last=0;cargo_name=''
route=[(-130000,6250),(-130000,5000),(-131500,3500),(-130212,2850)]
def w():return next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='WNY_PrototypeRegion' and unreal.GameplayStatics.get_game_mode(w) and unreal.GameplayStatics.get_player_controller(w,0))
def pc():return unreal.GameplayStatics.get_player_controller(w(),0)
def p():return pc().get_controlled_pawn()
def inv():return p().get_component_by_class(unreal.RVInventoryComponent)
def key(k,on):
 if held.get(k,False)!=on:unreal.RVInteriorMotorhome.dispatch_development_key(pc(),k,on);held[k]=on
def sample(label):
 rows.append({'stage':label,'position':str(p().get_actor_location()),'items':[{'id':unreal.GuidLibrary.conv_guid_to_string(i.id),'quantity':i.quantity,'condition':i.condition} for i in inv().get_items()],'container':str(inv().open_container.display_name) if inv().open_container else '', 'feedback':inv().feedback})
def cargo():return next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w(),unreal.RVExteriorStoragePoint) if a.get_name()==cargo_name)
def finish(result):
 global handle
 for k in list(held):key(k,False)
 unreal.unregister_slate_post_tick_callback(handle);handle=None
 (out/'normal-return-storage.json').write_text(json.dumps({'result':result,'evidence':'normal Tab/T/I/W/E controls from actual driven gas visit; no player relocation','samples':rows},indent=2));gc.collect()
def tick(dt):
 global stage,index,last,cargo_name
 try:
  t=time.time()-started
  events={0:(0,'Tab',True),1:(.15,'Tab',False),2:(.4,'T',True),3:(.55,'T',False),5:(1.3,'I',True),6:(1.45,'I',False)}
  if stage in events:
   at,k,on=events[stage]
   if t>=at:key(k,on);stage+=1
  elif stage==4 and t>1:sample('food transferred with Tab/T');assert len(inv().get_items())>0;stage=5
  elif stage==7:
   q=p().get_actor_location();x,y=route[index];d=math.hypot(x-q.x,y-q.y);pc().set_control_rotation(unreal.Rotator(yaw=math.degrees(math.atan2(y-q.y,x-q.x))));key('W',d>70)
   if d<=70:
    if index<len(route)-1:index+=1
    else:
     key('W',False);c=min(unreal.GameplayStatics.get_all_actors_of_class(w(),unreal.RVExteriorStoragePoint),key=lambda a:a.get_actor_location().distance(p().get_actor_location()));cargo_name=c.get_name();stage=8
   if t>65:finish('return walking timeout; not accepted')
  elif stage==8:
   q=p().get_actor_location();c=cargo();a=c.get_actor_location();d=math.hypot(a.x-q.x,a.y-q.y);pc().set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p().get_actor_eyes_view_point()[0],a));key('W',d>180)
   if d<=180:key('W',False);key('E',True);stage=9;last=t
   elif t>75:finish('cargo approach timeout; not accepted')
  elif stage==9 and t-last>.15:key('E',False);stage=10
  elif stage==10 and t-last>1:
   sample('cargo opened');assert inv().open_container==cargo().container;key('T',True);stage=11
  elif stage==11 and t-last>1.15:key('T',False);stage=12
  elif stage==12 and t-last>2:sample('stored');finish('normal driven-scavenge-return-store controls executed; inspect conservation')
 except Exception:(out/'normal-return-storage-error.txt').write_text(traceback.format_exc());finish('error; not accepted')
handle=unreal.register_slate_post_tick_callback(tick)
