import unreal,time,json,gc,traceback
from pathlib import Path
out=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate10Validation');start=time.time();handle=None;done=set();before=[]
def pc():
 return next(unreal.GameplayStatics.get_player_controller(w,0) for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='WNY_PrototypeRegion' and unreal.GameplayStatics.get_game_mode(w) and unreal.GameplayStatics.get_player_controller(w,0))
def inv():return pc().get_controlled_pawn().get_component_by_class(unreal.RVInventoryComponent)
def items(c):return [{'id':unreal.GuidLibrary.conv_guid_to_string(i.id),'definition':i.definition.get_path_name(),'quantity':i.quantity,'condition':i.condition} for i in c.get_items()]
def key(k,on):unreal.RVInteriorMotorhome.dispatch_development_key(pc(),k,on)
def tick(dt):
 global handle,before
 try:
  t=time.time()-start
  events=[(0,'Tab',True),(.15,'Tab',False),(.3,'Down',True),(.4,'Down',False),(.5,'Down',True),(.6,'Down',False),(.7,'Down',True),(.8,'Down',False),(.9,'Down',True),(1,'Down',False),(1.2,'T',True),(1.35,'T',False)]
  if not before:before=items(inv())
  for idx,(at,k,on) in enumerate(events):
   if t>=at and idx not in done:done.add(idx);key(k,on);break
  if t>3:
   i=inv();a=items(i);b=items(i.open_container);food=next(x for x in before if '/DA_Food.' in x['definition'])
   passed=food in b and all(x['id']!=food['id'] for x in a)
   (out/'normal-store-conservation.json').write_text(json.dumps({'pass':passed,'evidence':'normal Tab/Down/T selection; original GUID/quantity/condition conserved','before':before,'player_after':a,'cargo_after':b,'feedback':i.feedback},indent=2))
   unreal.unregister_slate_post_tick_callback(handle);handle=None;gc.collect()
 except Exception:
  (out/'normal-store-error.txt').write_text(traceback.format_exc());unreal.unregister_slate_post_tick_callback(handle);handle=None;gc.collect()
handle=unreal.register_slate_post_tick_callback(tick)
