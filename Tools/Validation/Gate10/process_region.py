"""Real replicated finite-loot contention/streaming; relocation is explicit fixture."""
import unreal,time,json,gc,traceback,sys
from pathlib import Path
out=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate10Validation');session=json.loads((out/'process-session.json').read_text());start=session['start'];case=session['config'];handle=None;done=set();rows=[];target_id='';claimed_id='';remaining=[];initial=[];role='';claimed_guid=None;claimed_quantity=0
def world():
 return next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='WNY_PrototypeRegion' and unreal.GameplayStatics.get_player_controller(w,0) and unreal.GameplayStatics.get_game_state(w))
def pc():return unreal.GameplayStatics.get_player_controller(world(),0)
def pawn():return pc().get_controlled_pawn()
def guid(g):return unreal.GuidLibrary.conv_guid_to_string(g)
def items(c):return [{'id':guid(i.id),'quantity':i.quantity,'condition':i.condition,'definition':i.definition.get_path_name()} for i in c.get_items()]
def target():return next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world(),unreal.RVScavengeContainer) if 'Pine Creek packaged' in str(a.container.display_name))
def check(name,ok,detail=''):rows.append({'case':name,'pass':bool(ok),'detail':detail})
def key(k,on):unreal.RVInteriorMotorhome.dispatch_development_key(pc(),k,on)
def all_players():return [p for p in unreal.GameplayStatics.get_all_actors_of_class(world(),unreal.RVSurvivorCharacter) if p.player_state]
def move_players(x,y):
 for index,p in enumerate(all_players()):p.set_actor_location(unreal.Vector(x+index*160,y,130),False,True);p.character_movement.stop_movement_immediately()
def arrival():
 global role
 role='server' if unreal.GameplayStatics.get_game_mode(world()) else 'client'
 v=unreal.GameplayStatics.get_all_actors_of_class(world(),unreal.RVInteriorMotorhome)[0];q=v.get_actor_transform().inverse_transform_location(pawn().get_actor_location())
 check('saved_region_mobile_base_arrival',abs(q.x)<550 and abs(q.y)<180 and 100<q.z<300,str(q))
 check('own_survivor_and_inventory',isinstance(pawn(),unreal.RVSurvivorCharacter) and pawn().get_component_by_class(unreal.RVInventoryComponent)!=None)
def approach():
 global initial,target_id,claimed_guid,claimed_quantity
 c=target();target_id=guid(c.container_id);initial=items(c.container);claimed_guid=c.container.get_items()[0].id;claimed_quantity=c.container.get_items()[0].quantity
 if role=='server':
  q=c.get_actor_location()
  for index,p in enumerate(all_players()):p.set_actor_location(q+unreal.Vector(-70+index*140,-165,95),False,True);p.character_movement.stop_movement_immediately()
 check('finite_supplies_replicated',len(initial)>0,initial)
def aim():pc().set_control_rotation(unreal.MathLibrary.find_look_at_rotation(pawn().get_actor_eyes_view_point()[0],target().get_actor_location()))
def claim():
 global claimed_id
 i=pawn().get_component_by_class(unreal.RVInventoryComponent);c=target().container
 check('normal_E_opens_streamed_container',i.open_container==c,i.feedback)
 claimed_id=guid(claimed_guid);i.request_transfer(claimed_guid,claimed_quantity,False)
def conserve():
 global remaining
 i=pawn().get_component_by_class(unreal.RVInventoryComponent);remaining=items(target().container)
 check('shared_container_post_contention',not any(x['id']==claimed_id for x in remaining),remaining)
 owned=[x for x in items(i) if x['id']==claimed_id]
 (out/(case['name']+'-'+role+'-ownership.json')).write_text(json.dumps({'id':session['id'],'owned':owned,'remaining':remaining,'claimed':claimed_id}))
 if role=='server':
  owners=[]
  for p in all_players():owners.extend(x for x in items(p.get_component_by_class(unreal.RVInventoryComponent)) if x['id']==claimed_id)
  check('server_exactly_one_contention_winner',len(owners)==1,owners)
 i.request_close_container()
def host_profile():
 if role=='server' and case.get('difficulty',False):
  gs=unreal.GameplayStatics.get_game_state(world());pc().request_difficulty('Relaxed','',1,gs.difficulty_revision)
def host_population():
 if role=='server' and case.get('difficulty',False):
  gs=unreal.GameplayStatics.get_game_state(world());pc().request_difficulty('','Population',.25,gs.difficulty_revision)
def client_override():
 if role=='client' and case.get('difficulty',False):
  gs=unreal.GameplayStatics.get_game_state(world());pc().request_difficulty('Harsh','',1,gs.difficulty_revision)
def difficulty_check():
 if not case.get('difficulty',False):return
 gs=unreal.GameplayStatics.get_game_state(world());rules={str(r.id):r.multiplier for r in gs.difficulty_rules}
 check('host_rules_replicate_client_override_rejected',str(gs.difficulty_preset)=='Custom' and abs(rules['Loot']-1.5)<.01 and abs(rules['Population']-.25)<.01,{'preset':str(gs.difficulty_preset),'rules':{k:rules[k] for k in ['Loot','Population']}})
 if role=='server':check('population_multiplier_bounds_new_group',len(unreal.GameplayStatics.get_all_actors_of_class(world(),unreal.RVInfected))<=1)
def unload():
 if role=='server':move_players(150000,0)
def far():
 check('actual_partition_unloads_target',all(guid(a.container_id)!=target_id for a in unreal.GameplayStatics.get_all_actors_of_class(world(),unreal.RVScavengeContainer)))
 zones=unreal.GameplayStatics.get_all_actors_of_class(world(),unreal.RVRegionEncounterZone)
 quiet=[str(z.zone_id) for z in zones if z.get_editor_property('bEvaluated') and z.outcome==unreal.RVEncounterOutcome.QUIET]
 check('quiet_travel_between_bounded_events',len(quiet)>0,quiet)
def back():
 if role=='server':move_players(-130000,5500)
def revisit():
 c=target();check('actual_streamed_contents_preserved',items(c.container)==remaining,items(c.container));check('searched_flag_survives_streaming',c.get_editor_property('bSearched'))
 gs=unreal.GameplayStatics.get_game_state(world());check('region_shared_difficulty_received',any(str(r.id)=='Loot' and not r.preparation_only for r in gs.difficulty_rules))
 infected=unreal.GameplayStatics.get_all_actors_of_class(world(),unreal.RVInfected);check('bounded_infected_population',len(infected)<=12,len(infected))
def finish(error=''):
 global handle
 key('E',False);unreal.unregister_slate_post_tick_callback(handle);handle=None
 (out/(case['name']+'-'+(role or 'unknown')+'.json')).write_text(json.dumps({'session':session['id'],'error':error,'evidence':'two-process normal E + accepted server inventory transaction; server relocation fixture for cell traversal, not driven-loop proof','results':rows},indent=2))
 for k in ['last_traceback','last_value','last_type','last_exc']:
  if hasattr(sys,k):setattr(sys,k,None)
 gc.collect()
def tick(dt):
 try:
  t=time.time()-start
  events=[(0,'arrival',arrival),(.6,'host_profile',host_profile),(1.4,'host_population',host_population),(2,'initial_gas_move',lambda:move_players(-130000,5500) if role=='server' else None),(6,'client_override',client_override),(10,'approach',approach),(12,'difficulty_check',difficulty_check),(13,'aim',aim),(14,'Edown',lambda:key('E',True)),(14.5,'Eup',lambda:key('E',False)),(17,'claim',claim),(21,'conserve',conserve),(23,'away',unload),(38,'far',far),(40,'back',back),(55,'revisit',revisit),(58,'finish',finish)]
  for at,name,fn in events:
   if t>=at and name not in done:done.add(name);fn();break
 except Exception:finish(traceback.format_exc())
handle=unreal.register_slate_post_tick_callback(tick)
