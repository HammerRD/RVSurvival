"""Focused paired normal input, shared-rule authority and melee convergence."""
import unreal,json,time,traceback
from pathlib import Path
B=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate9_5Validation')
session=json.loads((B/'session.json').read_text());config=session['config'];start=session['start']
w=next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='Gate9_5CombatRefinementTest' and unreal.GameplayStatics.get_player_controller(w,0) and unreal.GameplayStatics.get_player_controller(w,0).get_controlled_pawn())
authority=unreal.GameplayStatics.get_game_mode(w) is not None;role='server' if authority else 'client'
pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn();other=next(c for c in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSurvivorCharacter) if c!=p)
hp=p if authority else other;cp=other if authority else p;gs=unreal.GameplayStatics.get_game_state(w)
enemies=sorted(unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVInfected),key=lambda a:a.get_name());results=[];events=[];idx=0;active=True;held=set()
def inv(c):return c.get_component_by_class(unreal.RVInventoryComponent)
def combat(c):return c.get_component_by_class(unreal.RVCombatComponent)
def check(name,ok,detail=''):results.append({'case':name,'pass':bool(ok),'detail':str(detail)})
def at(t,fn):events.append((t,fn))
def key(k,on):
 unreal.RVInteriorMotorhome.dispatch_development_key(pc,k,on)
 if on:held.add(k)
 else:held.discard(k)
def tap(t,k):at(t,lambda:key(k,True));at(t+.1,lambda:key(k,False))
def setup():
 if config.get('network'):
  for k,v in [('PktLagMin',100),('PktLagMax',100),('PktLoss',2)]:unreal.SystemLibrary.execute_console_command(pc,'NetEmulation.'+k+' '+str(v),pc)
 p.character_movement.stop_movement_immediately();p.set_actor_location(unreal.Vector(0,-2500 if authority else -2900,90),False,True);pc.set_control_rotation(unreal.Rotator())
 if authority:
  cp.set_actor_location(unreal.Vector(0,-2900,90),False,True)
  for c in [hp,cp]:
   for name in ['DA_M1911_45ACP','DA_45ACPMagazine','DA_PrototypeCrowbar']:
    item=unreal.RVItemInstance();item.set_editor_property('Id',unreal.GuidLibrary.new_guid());item.set_editor_property('Definition',unreal.load_asset('/Game/Combat/Gate9_5/Items/'+name));check('owned fixture admitted',not inv(c).add_authority(item))
  for enemy,y in zip(enemies[:2],[-2500,-2900]):
   enemy.get_controller().get_editor_property('BrainComponent').stop_logic('stationary melee fixture');enemy.get_controller().stop_movement();enemy.set_actor_location(unreal.Vector(1500,y-2000,90),False,True)
at(0,setup);tap(1,'Four');tap(2,'R')
at(5,lambda:check('both owned .45 magazines load and replicate',all(combat(c).get_loaded_rounds()==7 for c in [hp,cp])))
tap(6,'LeftMouseButton');at(7,lambda:check('paired fire consumes exactly one each',all(combat(c).shot_sequence==1 and combat(c).get_loaded_rounds()==6 for c in [hp,cp])))
at(8,lambda:pc.request_difficulty('Harsh','None',1,gs.difficulty_revision) if not authority else None)
at(9.5,lambda:check('client cannot override authoritative world rules',str(gs.difficulty_preset)=='Standard',str(gs.difficulty_preset)))
at(10,lambda:pc.request_difficulty('Relaxed','None',1,gs.difficulty_revision) if authority else None)
at(12,lambda:check('host preset converges on both processes',str(gs.difficulty_preset)=='Relaxed'))
at(13,lambda:pc.request_difficulty('None','Hunger',1.7,gs.difficulty_revision) if authority else None)
at(15,lambda:check('host Custom multiplier converges',str(gs.difficulty_preset)=='Custom' and abs(next(r.multiplier for r in gs.difficulty_rules if str(r.id)=='Hunger')-1.7)<.001))
at(16,lambda:pc.request_difficulty('Standard','None',1,gs.difficulty_revision) if authority else None)
tap(17,'Five');at(18,lambda:check('owned crowbars equip in both processes',all(unreal.GuidLibrary.is_valid_guid(combat(c).equipped_weapon) for c in [hp,cp])))
def place_melee_targets():
 if authority:
  for enemy,y in zip(enemies[:2],[-2500,-2900]):enemy.set_actor_location(unreal.Vector(120,y,90),False,True)
at(18.3,place_melee_targets)
at(18.5,lambda:pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p.get_actor_eyes_view_point()[0],enemies[0 if authority else 1].get_actor_location()+unreal.Vector(0,0,25))))
at(19,lambda:globals().__setitem__('before_melee',[e.vitality for e in enemies[:2]]));tap(19.5,'B')
def trace_fixture():
 report={'role':role,'local_player':str(p.get_actor_location()),'eyes':str(p.get_actor_eyes_view_point()),'control':str(pc.get_control_rotation()),'trace':p.get_component_by_class(unreal.RVInteractionComponent).debug_trace_description(),'targets':[{'name':e.get_name(),'location':str(e.get_actor_location())} for e in enemies[:2]],'host_eyes':str(hp.get_actor_eyes_view_point()),'client_eyes':str(cp.get_actor_eyes_view_point())}
 (B/(config['name']+'_'+role+'_trace.json')).write_text(json.dumps(report,indent=2))
at(19.2,trace_fixture)
at(21,lambda:check('both melee intents damage once and replicate',all(combat(c).melee_sequence==1 for c in [hp,cp]) and all(e.vitality<before for e,before in zip(enemies[:2],before_melee)),[(e.vitality,before) for e,before in zip(enemies[:2],before_melee)]))
at(21.2,lambda:globals().__setitem__('after_melee',[e.vitality for e in enemies[:2]]));tap(21.3,'B');tap(21.45,'B')
at(23,lambda:check('cooldown prevents double completion',all(combat(c).melee_sequence==2 for c in [hp,cp])))
def finish():
 global active,w,pc,p,other,hp,cp,gs,enemies
 for k in list(held):key(k,False)
 unreal.unregister_slate_post_tick_callback(handle);active=False
 (B/(config['name']+'_'+role+'.json')).write_text(json.dumps({'results':results,'passed':sum(r['pass'] for r in results),'total':len(results),'role':role,'network':config.get('network',False)},indent=2));w=pc=p=other=hp=cp=gs=None;enemies=[]
at(25,finish);events.sort(key=lambda e:e[0])
def tick(dt):
 global idx
 if not active:return
 try:
  while idx<len(events) and time.time()-start>=events[idx][0]:
   fn=events[idx][1];idx+=1;fn()
   if not active:return
 except Exception:check('runner error',False,traceback.format_exc());finish()
handle=unreal.register_slate_post_tick_callback(tick)
