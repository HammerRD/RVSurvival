"""Native path/perception/limb proof. Placements isolate scenarios; movement is native AI."""
import unreal,time,json,traceback
from pathlib import Path
out=Path('D:/GitHub/RVSurvival/RVSurvival/Docs/Gate9Results');started=time.time();results=[];events=[];index=0;samples=[]
w=next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='Gate9CombatInfectedTest' and unreal.GameplayStatics.get_player_controller(w,0) and unreal.GameplayStatics.get_player_controller(w,0).get_controlled_pawn())
pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn();inv=p.get_component_by_class(unreal.RVInventoryComponent)
enemies=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVInfected);enemy=enemies[0];ai=enemy.get_controller();brain=ai.get_editor_property('BrainComponent')
for e in enemies:e.get_controller().get_editor_property('BrainComponent').stop_logic('isolated native navigation fixture');e.get_controller().stop_movement()
v=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSystemsMotorhome)[0]
for n in ['DA_9mmHandgun','DA_9mmMagazine']:
 i=unreal.RVItemInstance();i.set_editor_property('Id',unreal.GuidLibrary.new_guid());i.set_editor_property('Definition',unreal.load_asset('/Game/Combat/Items/'+n));assert not inv.add_authority(i)
def check(n,ok,d=''):results.append({'case':n,'pass':bool(ok),'detail':str(d)});unreal.log('GATE9_NAV '+json.dumps(results[-1]))
def at(t,f):events.append((t,f))
def key(k,on):unreal.RVInteriorMotorhome.dispatch_development_key(pc,k,on)
def tap(t,k):at(t,lambda:key(k,True));at(t+.12,lambda:key(k,False))
def place(c,xyz):c.character_movement.stop_movement_immediately();c.set_actor_location(unreal.Vector(*xyz),False,True)
place(enemy,(2100,2500,90));place(p,(900,2500,90));enemy.set_actor_rotation(unreal.Rotator(yaw=180),False);pc.set_control_rotation(unreal.Rotator(yaw=90))
# Native AI path following below proves the detour without reflective NavSystem CDO queries.
at(.6,lambda:check('cover blocks native sight',p not in ai.get_component_by_class(unreal.AIPerceptionComponent).get_currently_perceived_actors(unreal.AISense_Sight)))
tap(.2,'Four');tap(.8,'R');tap(3.1,'LeftMouseButton');at(3.5,lambda:brain.restart_logic())
at(4,lambda:check('blocked shot noise produces investigation',enemy.state==unreal.RVInfectedState.INVESTIGATE,enemy.state))
at(8,lambda:check('native AI follows cover detour',enemy.get_actor_location().x<1800 and abs(enemy.get_actor_location().y-2500)>250,enemy.get_actor_location()))
def leg_fixture():
 brain.stop_logic('limb fixture');ai.stop_movement();place(enemy,(0,-6500,90));place(p,(700,-6500,90));enemy.set_actor_rotation(unreal.Rotator(yaw=0),False)
at(8.5,leg_fixture)
def aim_leg():
 point=enemy.get_editor_property('Mesh').get_socket_location('calf_l');pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p.get_actor_eyes_view_point()[0],point))
at(9.4,aim_leg);tap(9.7,'LeftMouseButton')
at(10.1,lambda:check('actual leg shot reduces native chase speed',enemy.get_editor_property('bLegInjured') and abs(enemy.character_movement.max_walk_speed-160)<1,(enemy.vitality,enemy.character_movement.max_walk_speed)))
at(10.3,lambda:brain.restart_logic());at(11.4,lambda:check('native sight reacquires after fixture',enemy.state in [unreal.RVInfectedState.CHASE,unreal.RVInfectedState.ATTACK],enemy.state))
at(11.6,lambda:place(p,(7000,-6500,90)))
at(12.8,lambda:check('lost sight investigates last known position',enemy.state==unreal.RVInfectedState.INVESTIGATE,enemy.state))
at(19.5,lambda:check('investigation expires into idle or wander',enemy.state in [unreal.RVInfectedState.IDLE,unreal.RVInfectedState.WANDER],enemy.state))
rv_initial=None
def rv_fixture():
 global rv_initial
 brain.stop_logic('RV exterior fixture');ai.stop_movement();t=v.get_actor_transform()
 # Along the outside shell from rear to front, within the authored nav ground.
 e=t.transform_location(unreal.Vector(-700,350,95));q=t.transform_location(unreal.Vector(600,350,95));place(enemy,(e.x,e.y,e.z));place(p,(q.x,q.y,q.z));rv_initial=enemy.get_actor_location();enemy.set_actor_rotation(unreal.Rotator(yaw=v.get_actor_rotation().yaw),False);pc.set_control_rotation(unreal.Rotator(yaw=v.get_actor_rotation().yaw+90))
at(20,rv_fixture);tap(21,'LeftMouseButton');at(21.5,lambda:brain.restart_logic())
at(25,lambda:check('infected pursues along parked RV exterior using native navigation',unreal.Vector.distance(enemy.get_actor_location(),rv_initial)>250,enemy.get_actor_location()))
at(26,lambda:check('RV exterior firearm action remains usable',p.get_component_by_class(unreal.RVCombatComponent).shot_sequence==3))
def finish():
 global w,pc,p,inv,enemies,enemy,ai,brain,v
 unreal.unregister_slate_post_tick_callback(handle);(out/'infected-navigation.json').write_text(json.dumps({'results':results,'samples':samples},indent=2));w=pc=p=inv=enemies=enemy=ai=brain=v=None
def tick(dt):
 global index
 try:
  t=time.time()-started
  while index<len(events) and t>=events[index][0]:events[index][1]();index+=1
  if not samples or t>samples[-1]['time']+.3:samples.append({'time':t,'state':str(enemy.state),'position':[enemy.get_actor_location().x,enemy.get_actor_location().y,enemy.get_actor_location().z],'speed':enemy.character_movement.max_walk_speed})
  if t>27:finish()
 except Exception:check('runner error',False,traceback.format_exc());finish()
events.sort(key=lambda e:e[0]);started=time.time();handle=unreal.register_slate_post_tick_callback(tick)

