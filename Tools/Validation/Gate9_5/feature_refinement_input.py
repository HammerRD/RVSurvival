"""Bounded normal-control pickup/hold/melee checks, authority tuning contract."""
import unreal,json,time,traceback
from pathlib import Path
out=Path('D:/GitHub/RVSurvival/RVSurvival/Docs/Gate9_5Results');results=[];events=[];started=time.time();index=0
w=next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='Gate9_5CombatRefinementTest' and unreal.GameplayStatics.get_player_controller(w,0) and unreal.GameplayStatics.get_player_controller(w,0).get_controlled_pawn())
pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn();inv=p.get_component_by_class(unreal.RVInventoryComponent);combat=p.get_component_by_class(unreal.RVCombatComponent);gs=unreal.GameplayStatics.get_game_state(w);needs=pc.player_state.get_component_by_class(unreal.RVNeedsComponent)
def check(n,ok,d=''):results.append({'case':n,'pass':bool(ok),'detail':str(d)});unreal.log('GATE9_5 '+json.dumps(results[-1]))
def at(t,f):events.append((t,f))
def key(n,on):unreal.RVInteriorMotorhome.dispatch_development_key(pc,n,on)
def tap(t,n):at(t,lambda:key(n,True));at(t+.08,lambda:key(n,False))
def aim(a):
 pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p.get_actor_location()+unreal.Vector(0,0,68),a.get_actor_location()))
p.set_actor_location(unreal.Vector(8000,0,90.15),False,False)
def add(path):
 i=unreal.RVItemInstance();i.set_editor_property('Id',unreal.GuidLibrary.new_guid());i.set_editor_property('Definition',unreal.load_asset(path));i.set_editor_property('Quantity',1);check('fixture admission',not inv.add_authority(i))
# Isolated fixture actors ensure exact trace geometry; gameplay actions use normal keys.
pickup=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVWorldItem)[0];pickup.set_actor_location(unreal.Vector(8150,0,120),False,False);item=unreal.RVItemInstance();item.set_editor_property('Id',unreal.GuidLibrary.new_guid());item.set_editor_property('Definition',unreal.load_asset('/Game/Combat/Gate9_5/Items/DA_45ACPMagazine'));pickup.set_editor_property('Item',item);pickup.get_component_by_class(unreal.StaticMeshComponent).set_static_mesh(item.definition.world_mesh)
check('ordinary item configured immediate',item.definition.pickup_seconds==0)
aim(pickup);at(.15,lambda:aim(pickup));at(.25,lambda:check('pickup trace prompt visible',bool(str(p.get_component_by_class(unreal.RVInteractionComponent).get_prompt())),str(p.get_component_by_class(unreal.RVInteractionComponent).get_prompt())+' pawn='+str(p.get_actor_location())+' pickup='+str(pickup.get_actor_location())));tap(.3,'E');at(.65,lambda:check('80ms tap picks up once',len(inv.get_items())==2 and not unreal.SystemLibrary.is_valid(pickup),str(len(inv.get_items()))+' '+inv.feedback))
add('/Game/Combat/Gate9_5/Items/DA_PrototypeCrowbar')
# Controlled actor is stationary so range and wall tests cannot be confounded by AI pathing.
target=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVInfected)[0];target.set_actor_location(unreal.Vector(8600,0,96),False,False);target.character_movement.disable_movement()
if target.get_controller():target.get_controller().un_possess()
at(.8,lambda:target.set_actor_location(unreal.Vector(8090,0,96),False,False));at(.85,lambda:aim(target));before=target.vitality;fatigue=needs.state.fatigue
tap(1,'LeftMouseButton');at(1.3,lambda:check('unarmed proximity hits with low damage',0<before-target.vitality<=6,str(target.vitality)));at(1.35,lambda:check('effort increases existing fatigue',needs.state.fatigue>fatigue));at(1.4,lambda:check('unarmed sequence authoritative',combat.melee_sequence==1))
tap(1.5,'LeftMouseButton');at(1.8,lambda:check('cooldown rejects repeated attack',combat.melee_sequence==1))
tap(2.5,'Five');at(2.8,lambda:check('normal 5 equips melee owned item',unreal.GuidLibrary.is_valid_guid(combat.equipped_weapon)))
tap(3,'LeftMouseButton');at(3.3,lambda:check('armed melee damages infected',target.vitality<before-6,str(target.vitality)))
def distant():target.set_actor_location(unreal.Vector(8600,0,96),False,False);aim(target)
at(4,distant);at(4.1,lambda:globals().__setitem__('before_miss',target.vitality));tap(4.3,'LeftMouseButton');at(4.7,lambda:check('distant target not hit',target.vitality==before_miss))
def wall_case():
 target.set_actor_location(unreal.Vector(8120,0,96),False,False);aim(target)
 global wall,before_wall
 wall=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.StaticMeshActor) if a.get_actor_label()=='Gate9_Cover_0');wall.static_mesh_component.set_mobility(unreal.ComponentMobility.MOVABLE);wall.set_actor_location(unreal.Vector(8060,0,120),False,False);wall.static_mesh_component.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Cube'));wall.set_actor_scale3d(unreal.Vector(.15,2,2));wall.static_mesh_component.set_collision_profile_name('BlockAll');wall.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS);before_wall=target.vitality
at(5.2,wall_case);tap(5.5,'LeftMouseButton');at(5.9,lambda:check('wall blocks melee damage',target.vitality==before_wall))
def timed_setup():
 global station,count_before
 wall.set_actor_location(unreal.Vector(9000,0,120),False,False)
 target.set_actor_location(unreal.Vector(8600,0,96),False,False)
 station=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVTestInteractable) if a.get_actor_label()=='Gate9_5TimedCounter');station.set_actor_location(unreal.Vector(8150,0,120),False,False);aim(station);count_before=station.get_editor_property('InteractionCount')
def trace_diagnostic():
 start=p.get_actor_location()+unreal.Vector(0,0,68);end=start+unreal.MathLibrary.get_forward_vector(pc.get_control_rotation())*300
 hit=unreal.SystemLibrary.line_trace_single(w,start,end,unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,False,[p],unreal.DrawDebugTrace.NONE,True)
 unreal.log('TIMED_TRACE '+p.get_component_by_class(unreal.RVInteractionComponent).debug_trace_description()+' bounds='+str(station.get_actor_bounds(False))+' enabled='+str(station.get_actor_enable_collision())+' mesh='+str(station.get_component_by_class(unreal.StaticMeshComponent).get_collision_enabled()))
at(9,timed_setup);at(9.15,trace_diagnostic);at(9.2,lambda:check('timed counter prompt visible',bool(str(p.get_component_by_class(unreal.RVInteractionComponent).get_prompt())),str(p.get_component_by_class(unreal.RVInteractionComponent).get_prompt())+' pawn='+str(p.get_actor_location())+' target='+str(station.get_actor_location())+' rotation='+str(pc.get_control_rotation())+' mode='+str(p.character_movement.movement_mode)));tap(9.3,'E');at(9.7,lambda:check('timed counter tap does not complete',station.get_editor_property('InteractionCount')==count_before))
at(10.1,lambda:key('E',True));at(10.8,lambda:check('timed counter hold completes once',station.get_editor_property('InteractionCount')==count_before+1));at(11.3,lambda:check('continued hold does not repeat',station.get_editor_property('InteractionCount')==count_before+1));at(11.4,lambda:key('E',False))
station=None
def finish():
 global w,pc,p,inv,combat,gs,needs,pickup,target,wall,station
 unreal.unregister_slate_post_tick_callback(handle);(out/'feature-refinement-input.json').write_text(json.dumps({'results':results,'passed':sum(r['pass'] for r in results),'total':len(results)},indent=2));w=pc=p=inv=combat=gs=needs=pickup=target=wall=station=None
wall=None
def tick(dt):
 global index
 try:
  while index<len(events) and time.time()-started>=events[index][0]:events[index][1]();index+=1
  if time.time()-started>12:finish()
 except Exception:check('runner error',False,traceback.format_exc());finish()
handle=unreal.register_slate_post_tick_callback(tick)


