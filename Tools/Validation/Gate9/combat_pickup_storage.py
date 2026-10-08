"""Real E pickup and accepted inventory UI request paths preserve partial magazines."""
import unreal,json,time,traceback
from pathlib import Path
out=Path('D:/GitHub/RVSurvival/RVSurvival/Docs/Gate9Results');results=[];events=[];started=time.time();index=0
w=next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='Gate9CombatInfectedTest' and unreal.GameplayStatics.get_player_controller(w,0) and unreal.GameplayStatics.get_player_controller(w,0).get_controlled_pawn())
pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn();inv=p.get_component_by_class(unreal.RVInventoryComponent);combat=p.get_component_by_class(unreal.RVCombatComponent)
p.set_actor_location(unreal.Vector(0,-6500,90),False,True)
pickup=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVWorldItem) if a.item.definition and a.item.definition.get_editor_property('Combat').get_editor_property('bMagazine') and a.item.magazine_rounds==6)
item=pickup.item;item.set_editor_property('Condition',.67);pickup.set_editor_property('Item',item);identity=unreal.GuidLibrary.conv_guid_to_string(item.id);pickup.set_actor_location(unreal.Vector(130,-6500,110),False,True)
def check(name,ok,detail=''):results.append({'case':name,'pass':bool(ok),'detail':str(detail)})
def at(t,fn):events.append((t,fn))
def key(k,on):unreal.RVInteriorMotorhome.dispatch_development_key(pc,k,on)
def hold(t):at(t,lambda:key('E',True));at(t+.75,lambda:key('E',False))
def owned():return next((i for i in inv.get_items() if unreal.GuidLibrary.conv_guid_to_string(i.id)==identity),None)
def aim(a):pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p.get_actor_eyes_view_point()[0],a.get_actor_location()))
at(.2,lambda:aim(pickup));hold(.8)
at(2,lambda:check('normal E picks up physical partial magazine',owned() is not None))
at(2.1,lambda:check('pickup preserves six rounds and condition',owned() is not None and owned().magazine_rounds==6 and abs(owned().condition-.67)<.001))
at(2.4,lambda:inv.request_drop(owned().id,1))
at(3.3,lambda:check('drop removes owned record without consuming rounds',owned() is None))
def aim_drop():
 global dropped
 dropped=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVWorldItem) if unreal.GuidLibrary.conv_guid_to_string(a.item.id)==identity);aim(dropped)
dropped=None
at(3.5,aim_drop);hold(4)
at(5.3,lambda:check('repick preserves GUID, rounds and condition',owned() is not None and owned().magazine_rounds==6 and abs(owned().condition-.67)<.001))
container=None
def create_container():
 global container
 container=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVStoragePoint)[0];container.detach_from_actor(unreal.DetachmentRule.KEEP_WORLD,unreal.DetachmentRule.KEEP_WORLD,unreal.DetachmentRule.KEEP_WORLD);container.set_actor_location(unreal.Vector(120,-6650,110),False,True);aim(container)
at(5.6,create_container);at(5.9,lambda:aim(container));at(6.1,lambda:aim(container));hold(6.3)
at(7.4,lambda:check('normal E opens reusable shared storage',inv.open_container==container.container))
at(7.6,lambda:inv.request_transfer(owned().id,1,True))
at(8.5,lambda:check('partial magazine transfers to container with state',owned() is None and any(unreal.GuidLibrary.conv_guid_to_string(i.id)==identity and i.magazine_rounds==6 and abs(i.condition-.67)<.001 for i in container.container.get_items())))
at(8.7,lambda:inv.request_transfer(item.id,1,False))
at(9.6,lambda:check('container return preserves same identity and rounds',owned() is not None and owned().magazine_rounds==6))
at(9.8,lambda:inv.request_close_container())
at(10.5,lambda:check('close restores normal walking with no open container',inv.open_container is None and p.character_movement.movement_mode==unreal.MovementMode.MOVE_WALKING))
def finish():
 global w,pc,p,inv,combat,pickup,dropped,container,item
 unreal.unregister_slate_post_tick_callback(handle);(out/'combat-pickup-storage.json').write_text(json.dumps({'results':results,'passed':sum(r['pass'] for r in results),'total':len(results)},indent=2));w=pc=p=inv=combat=pickup=dropped=container=item=None
def tick(dt):
 global index
 try:
  while index<len(events) and time.time()-started>=events[index][0]:events[index][1]();index+=1
  if time.time()-started>11:finish()
 except Exception:check('runner error',False,traceback.format_exc());finish()
events.sort(key=lambda e:e[0]);handle=unreal.register_slate_post_tick_callback(tick)


