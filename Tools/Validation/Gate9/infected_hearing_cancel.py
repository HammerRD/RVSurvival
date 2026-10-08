"""Native hearing acquisition and melee windup cancellation in an isolated PIE fixture."""
import unreal,json,time,traceback
from pathlib import Path
out=Path('D:/GitHub/RVSurvival/RVSurvival/Docs/Gate9Results');results=[];events=[];started=time.time();index=0;escaped=False
w=next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='Gate9CombatInfectedTest' and unreal.GameplayStatics.get_player_controller(w,0) and unreal.GameplayStatics.get_player_controller(w,0).get_controlled_pawn())
pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn();inv=p.get_component_by_class(unreal.RVInventoryComponent);combat=p.get_component_by_class(unreal.RVCombatComponent);health=p.get_editor_property('PlayerState').get_editor_property('Health')
enemy=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVInfected)[0];ai=enemy.get_controller();brain=ai.get_editor_property('BrainComponent');brain.stop_logic('hearing placement fixture');ai.stop_movement();enemy.set_actor_location(unreal.Vector(0,-6500,90),False,True);enemy.set_actor_rotation(unreal.Rotator(yaw=180),False);p.set_actor_location(unreal.Vector(900,-6500,90),False,True);pc.set_control_rotation(unreal.Rotator(yaw=90))
for name in ['DA_9mmHandgun','DA_9mmMagazine']:
 i=unreal.RVItemInstance();i.set_editor_property('Id',unreal.GuidLibrary.new_guid());i.set_editor_property('Definition',unreal.load_asset('/Game/Combat/Items/'+name));assert not inv.add_authority(i)
def check(name,ok,detail=''):results.append({'case':name,'pass':bool(ok),'detail':str(detail)})
def at(t,fn):events.append((t,fn))
def key(k,on):unreal.RVInteriorMotorhome.dispatch_development_key(pc,k,on)
def tap(t,k):at(t,lambda:key(k,True));at(t+.12,lambda:key(k,False))
at(.7,lambda:check('fixture player initially outside sight cone',p not in ai.get_component_by_class(unreal.AIPerceptionComponent).get_currently_perceived_actors(unreal.AISense_Sight)))
tap(.2,'Four');tap(.8,'R');tap(3.1,'LeftMouseButton')
at(3.35,lambda:check('gunshot registers native hearing stimulus',p in ai.get_component_by_class(unreal.AIPerceptionComponent).get_currently_perceived_actors(unreal.AISense_Hearing)))
at(3.5,lambda:brain.restart_logic());at(4.2,lambda:check('hearing leads to investigate or chase',enemy.state in [unreal.RVInfectedState.INVESTIGATE,unreal.RVInfectedState.CHASE,unreal.RVInfectedState.ATTACK],enemy.state))
at(10,lambda:check('windup was reached then victim escaped',escaped))
at(10.1,lambda:check('out-of-range windup causes no late medical injury',len(health.injuries)==0,len(health.injuries)))
def finish():
 global w,pc,p,inv,combat,health,enemy,ai,brain
 unreal.unregister_slate_post_tick_callback(handle);(out/'infected-hearing-cancel.json').write_text(json.dumps({'results':results,'passed':sum(r['pass'] for r in results),'total':len(results)},indent=2));w=pc=p=inv=combat=health=enemy=ai=brain=None
def tick(dt):
 global index,escaped
 try:
  while index<len(events) and time.time()-started>=events[index][0]:events[index][1]();index+=1
  if not escaped and enemy.attack_sequence>0:
   escaped=True;p.character_movement.stop_movement_immediately();p.set_actor_location(unreal.Vector(7000,-6500,90),False,True)
  if time.time()-started>11:finish()
 except Exception:check('runner error',False,traceback.format_exc());finish()
events.sort(key=lambda e:e[0]);handle=unreal.register_slate_post_tick_callback(tick)
