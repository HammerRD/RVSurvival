"""Single-player streamed-state diagnostic with real E/UI transaction paths.
Development relocation accelerates cell traversal; not a driving-loop substitute.
All world/actor wrappers are reacquired in function scope and released each tick.
"""
import unreal,time,json,traceback,gc,sys,math
from pathlib import Path
out=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate10Validation');started=time.time();handle=None;done=set();rows=[];initial=[];remaining=[];target_id='';transferred_id=''
def world():return next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='WNY_PrototypeRegion' and unreal.GameplayStatics.get_game_mode(w) and unreal.GameplayStatics.get_player_controller(w,0))
def pawn():return unreal.GameplayStatics.get_player_controller(world(),0).get_controlled_pawn()
def key(k,on):unreal.RVInteriorMotorhome.dispatch_development_key(unreal.GameplayStatics.get_player_controller(world(),0),k,on)
def guid(g):return g.to_string()
def target():return next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world(),unreal.RVScavengeContainer) if guid(a.container_id)==target_id)
def items(c):return [{'id':guid(i.id),'definition':i.definition.get_path_name(),'quantity':i.quantity,'condition':i.condition} for i in c.get_items()]
def check(name,passed,detail=''):rows.append({'case':name,'pass':bool(passed),'detail':detail})
def relocate(x,y,z):
 p=pawn();p.set_actor_location(unreal.Vector(x,y,z),False,True);p.character_movement.stop_movement_immediately();unreal.GameplayStatics.get_player_controller(world(),0).set_control_rotation(unreal.Rotator(yaw=-90))
def approach():
 global target_id,initial
 w=world();candidates=[a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVScavengeContainer) if 'Pine Creek packaged' in str(a.container.display_name)]
 assert len(candidates)==1;container=candidates[0];target_id=guid(container.container_id);initial=items(container.container)
 q=container.get_actor_location();relocate(q.x,q.y-170,q.z+40)
 pc=unreal.GameplayStatics.get_player_controller(w,0);pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(pawn().get_actor_eyes_view_point()[0],q))
 check('initial_finite_supplies',len(initial)>0,initial)
def transfer():
 global remaining,transferred_id
 p=pawn();inv=p.get_component_by_class(unreal.RVInventoryComponent);c=target().container
 check('normal_E_opens_real_container',inv.open_container==c and target().get_editor_property('bSearched'),p.get_component_by_class(unreal.RVInteractionComponent).debug_trace_description())
 if inv.open_container!=c:return
 record=c.get_items()[0];transferred_id=guid(record.id);inv.request_transfer(record.id,record.quantity,False)
 remaining=items(c);check('normal_transaction_conserves_item',any(i['id']==transferred_id for i in items(inv)) and not any(i['id']==transferred_id for i in remaining))
 inv.request_transfer(record.id,record.quantity,False)
 check('stale_repeated_transfer_rejected',sum(i['id']==transferred_id for i in items(inv))==1)
 inv.request_close_container()
def survey():
 w=world();p=pawn();nav=unreal.NavigationSystemV1.project_point_to_navigation(w,p.get_actor_location(),None,None,unreal.Vector(300,300,2500))
 zones=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVRegionEncounterZone);infected=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVInfected)
 check('native_navigation_projects_at_gas',nav is not None,str(nav))
 check('encounter_active_population_bounded',len(infected)<=12,{'infected':len(infected),'zones':[{'id':guid(z.zone_id),'evaluated':z.get_editor_property('bEvaluated'),'outcome':str(z.outcome)} for z in zones]})
def far_check():
 loaded=[guid(a.container_id) for a in unreal.GameplayStatics.get_all_actors_of_class(world(),unreal.RVScavengeContainer)]
 check('actual_partition_unloaded_searched_container',target_id not in loaded,loaded)
def revisit():
 try:c=target();restored=items(c.container);check('actual_streamed_revisit_preserves_state',restored==remaining,{'before':remaining,'after':restored});check('actual_streamed_searched_flag_retained',c.get_editor_property('bSearched'))
 except StopIteration:check('actual_streamed_revisit_preserves_state',False,'not reloaded')
def finish():
 global handle
 for k in ['E','W','S']:key(k,False)
 unreal.unregister_slate_post_tick_callback(handle);handle=None
 (out/'single-player-stream-diagnostic.json').write_text(json.dumps({'evidence':'real E input and existing UI transaction; development relocation for streaming, not driving-loop validation','results':rows},indent=2));gc.collect()
def tick(dt):
 try:
  t=time.time()-started
  events=[(1,'gas',lambda:relocate(-130000,5500,130)),(8,'approach',approach),(9,'e_down',lambda:key('E',True)),(9.15,'e_up',lambda:key('E',False)),(11,'transfer',transfer),(13,'survey',survey),(15,'away',lambda:relocate(150000,0,130)),(28,'far',far_check),(30,'back',lambda:relocate(-130000,5500,130)),(43,'revisit',revisit),(45,'finish',finish)]
  for at,name,fn in events:
   if t>=at and name not in done:done.add(name);fn();break
 except Exception:
  (out/'stream-diagnostic-error.txt').write_text(traceback.format_exc())
  for k in ['last_traceback','last_value','last_type','last_exc']:
   if hasattr(sys,k):setattr(sys,k,None)
  finish()
handle=unreal.register_slate_post_tick_callback(tick)
