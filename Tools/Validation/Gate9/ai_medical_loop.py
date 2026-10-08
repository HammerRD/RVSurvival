"""Native perception/navigation and weapon-to-medical loop in a scoped PIE fixture."""
import unreal,json,time,traceback
from pathlib import Path
out=Path('D:/GitHub/RVSurvival/RVSurvival/Docs/Gate9Results');results=[];events=[];started=time.time();index=0;samples=[]
w=next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='Gate9CombatInfectedTest' and unreal.GameplayStatics.get_player_controller(w,0) and unreal.GameplayStatics.get_player_controller(w,0).get_controlled_pawn())
pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn();inv=p.get_component_by_class(unreal.RVInventoryComponent);combat=p.get_component_by_class(unreal.RVCombatComponent);ps=p.get_editor_property('PlayerState');health=ps.get_editor_property('Health')
enemy=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVInfected)[0]
p.set_actor_location(unreal.Vector(0,-2500,90),False,False);enemy.set_actor_location(unreal.Vector(900,-2500,90),False,False);enemy.set_actor_rotation(unreal.Rotator(yaw=180),False)
def check(name,ok,detail=''):
 row={'case':name,'pass':bool(ok),'detail':str(detail)};results.append(row);unreal.log('GATE9_AI '+json.dumps(row))
def at(t,fn):events.append((t,fn))
def key(name,on):unreal.RVInteriorMotorhome.dispatch_development_key(pc,name,on)
def tap(t,name):at(t,lambda:key(name,True));at(t+.12,lambda:key(name,False))
def add(path):
 i=unreal.RVItemInstance();i.set_editor_property('Id',unreal.GuidLibrary.new_guid());i.set_editor_property('Definition',unreal.load_asset(path));assert not inv.add_authority(i)
add('/Game/Combat/Items/DA_9mmHandgun');add('/Game/Combat/Items/DA_9mmMagazine')
initial=enemy.get_actor_location();initial_vitality=enemy.vitality
at(1,lambda:check('infected has native AIController',isinstance(enemy.get_controller(),unreal.RVInfectedController)))
at(1.2,lambda:check('native sight acquires/chases',enemy.state in [unreal.RVInfectedState.CHASE,unreal.RVInfectedState.ATTACK],enemy.state))
at(2,lambda:check('native NavMesh path changes position',unreal.Vector.distance(enemy.get_actor_location(),initial)>100,enemy.get_actor_location()))
tap(.3,'Four');tap(.7,'R')
at(5,lambda:check('infected attack creates medical wound',len(health.injuries)>0,[str(i.region) for i in health.injuries]))
at(5.2,lambda:check('bite retains contamination and bleeding',any(i.infection_risk>0 and i.bleeding_per_minute>0 for i in health.injuries)))
def aim():
 point=enemy.get_actor_location()+unreal.Vector(0,0,25);eye=p.get_actor_eyes_view_point()[0];pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(eye,point))
for t in [5.6,6.1,6.6,7.1]:at(t-.2,aim);tap(t,'LeftMouseButton')
at(8,lambda:check('firearm damages/kills infected through actual trace',enemy.vitality<initial_vitality,enemy.vitality))
at(8.2,lambda:check('dead state replicated source entered once',enemy.state==unreal.RVInfectedState.DEAD and enemy.death_sequence==1,(enemy.state,enemy.death_sequence)))
attack_count=None;injury_count=None
def remember():
 global attack_count,injury_count
 attack_count=enemy.attack_sequence;injury_count=len(health.injuries)
at(8.4,remember)
at(11,lambda:check('dead infected cannot continue attacks',enemy.attack_sequence==attack_count and len(health.injuries)==injury_count))
def finish():
 global w,pc,p,inv,combat,ps,health,enemy
 unreal.unregister_slate_post_tick_callback(handle)
 (out/'ai-medical-loop.json').write_text(json.dumps({'results':results,'samples':samples,'passed':sum(r['pass'] for r in results),'total':len(results)},indent=2));w=pc=p=inv=combat=ps=health=enemy=None
def tick(dt):
 global index
 try:
  if len(samples)<40 and (not samples or time.time()-started>samples[-1]['time']+.3):samples.append({'time':time.time()-started,'enemy_position':[enemy.get_actor_location().x,enemy.get_actor_location().y,enemy.get_actor_location().z],'state':str(enemy.state),'vitality':enemy.vitality,'attacks':enemy.attack_sequence,'shot_sequence':combat.shot_sequence,'rounds':combat.get_loaded_rounds(),'player_injuries':len(health.injuries),'movement_status':str(enemy.get_controller().get_move_status())})
  while index<len(events) and time.time()-started>=events[index][0]:events[index][1]();index+=1
  if time.time()-started>12:finish()
 except Exception:check('runner error',False,traceback.format_exc());finish()
events.sort(key=lambda e:e[0]);handle=unreal.register_slate_post_tick_callback(tick)
