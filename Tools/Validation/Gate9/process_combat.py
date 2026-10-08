"""Separate-process combat/medical intents; normal input except explicit invalid-request probes."""
import unreal,json,time,os,traceback
from pathlib import Path
B=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate9Validation');session=json.loads((B/'session.json').read_text());config=session['config'];start=session['start']
w=next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='Gate9CombatInfectedTest' and unreal.GameplayStatics.get_player_controller(w,0) and unreal.GameplayStatics.get_player_controller(w,0).get_controlled_pawn())
authority=unreal.GameplayStatics.get_game_mode(w) is not None;role='server' if authority else 'client';pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn()
other=next(c for c in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSurvivorCharacter) if c!=p);hp=p if authority else other;cp=other if authority else p
results=[];events=[];held=set();idx=0;active=True;enemies=sorted(unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVInfected),key=lambda a:a.get_name())
def combat(c):return c.get_component_by_class(unreal.RVCombatComponent)
def inventory(c):return c.get_component_by_class(unreal.RVInventoryComponent)
def health(c):return c.get_editor_property('PlayerState').get_editor_property('Health')
def items(c):return inventory(c).get_items()
def weapon(c):return next(i for i in items(c) if i.definition.get_editor_property('Combat').get_editor_property('bFirearm'))
def mags(c):return [i for i in items(c) if i.definition.get_editor_property('Combat').get_editor_property('bMagazine')]
def guid(g):return unreal.GuidLibrary.conv_guid_to_string(g)
def check(name,ok,detail=''):results.append({'case':name,'pass':bool(ok),'detail':str(detail)})
def at(t,fn):events.append((t,fn))
def key(k,on):
 unreal.RVInteriorMotorhome.dispatch_development_key(pc,k,on)
 if on:held.add(k)
 else:held.discard(k)
def tap(t,k,who='both'):
 at(t,lambda:key(k,True) if who=='both' or (who=='host')==authority else None);at(t+.12,lambda:key(k,False) if who=='both' or (who=='host')==authority else None)
def add(c,path,quantity=1):
 i=unreal.RVItemInstance();i.set_editor_property('Id',unreal.GuidLibrary.new_guid());i.set_editor_property('Definition',unreal.load_asset(path));i.set_editor_property('Quantity',quantity);i.set_editor_property('Condition',.81)
 error=inventory(c).add_authority(i);check('authority fixture admission',not error,error)
def setup():
 unreal.SystemLibrary.execute_console_command(pc,'t.MaxFPS 60',pc)
 if config.get('network'):
  for k,v in [('PktLagMin',100),('PktLagMax',100),('PktLoss',2)]:unreal.SystemLibrary.execute_console_command(pc,'NetEmulation.'+k+' '+str(v),pc)
 p.character_movement.stop_movement_immediately();p.set_actor_location(unreal.Vector(0,-2500 if authority else -2900,90),False,True);pc.set_control_rotation(unreal.Rotator())
 if authority:
  cp.set_actor_location(unreal.Vector(0,-2900,90),False,True)
  for c in [hp,cp]:
   add(c,'/Game/Combat/Items/DA_9mmHandgun')
   for _ in range(3):add(c,'/Game/Combat/Items/DA_9mmMagazine')
  add(hp,'/Game/Medical/DA_PressureDressing',3);add(hp,'/Game/Medical/DA_FirstAidKit',2)
at(0,setup);tap(1,'Four');tap(2,'R')
at(5,lambda:check('host/client real magazine loads and replicates',all(combat(c).get_loaded_rounds()==15 for c in [hp,cp])))
tap(6,'LeftMouseButton','host');tap(7,'LeftMouseButton','client')
at(8,lambda:check('host and client fire through owned authority',all(combat(c).shot_sequence==1 and combat(c).get_loaded_rounds()==14 for c in [hp,cp])))
tap(9,'LeftMouseButton');at(10,lambda:check('simultaneous independent fire consumes one each',all(combat(c).shot_sequence==2 and combat(c).get_loaded_rounds()==13 for c in [hp,cp])))
tap(11,'R');at(14.5,lambda:check('partial magazine reload conserves both inventories',all(combat(c).get_loaded_rounds()==15 and sum(m.magazine_rounds for m in mags(c))==43 for c in [hp,cp])))
def invalid():
 own=weapon(p);foreign=weapon(other);C=combat(p);check('owned invalid-request probes actually queued',C.debug_request_fire(own.id,0,50000) and C.debug_request_fire(foreign.id,own.combat_revision,50001) and C.debug_request_reload(mags(other)[0].id,own.combat_revision))
at(15.5,invalid);at(17,lambda:check('stale and foreign weapon/magazine intents do not mutate ammo',all(sum(m.magazine_rounds for m in mags(c))==43 and combat(c).shot_sequence==2 for c in [hp,cp])))
tap(18,'LeftMouseButton');at(19,lambda:check('invalid sequence cannot poison subsequent normal fire',all(combat(c).shot_sequence==3 and sum(m.magazine_rounds for m in mags(c))==42 for c in [hp,cp])))
def targets():
 if not authority:return
 for a,y in zip(enemies[:2],[-2500,-2900]):
  a.get_controller().get_editor_property('BrainComponent').stop_logic('stationary regional damage fixture');a.get_controller().stop_movement();a.set_actor_location(unreal.Vector(900,y,90),False,True);a.set_actor_rotation(unreal.Rotator(yaw=180),False)
at(20,targets)
def aim(point):pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p.get_actor_eyes_view_point()[0],point))
def enemy_point(a,region):
 mapping=a.get_editor_property('Profile').get_editor_property('BodyMapping');bone=next(r.anchor_bone for r in mapping.body_regions if r.region==region)
 return a.mesh.get_socket_location(bone)+unreal.Vector(0,0,5)
at(21,lambda:aim(enemy_point(enemies[0],unreal.RVBodyRegion.HEAD)) if authority else None);tap(21.5,'LeftMouseButton','host')
at(23,lambda:check('head hit stops infected and death converges',enemies[0].state==unreal.RVInfectedState.DEAD and enemies[0].death_sequence==1,(enemies[0].vitality,enemies[0].state)))
for t in [24.5,25.3,26.1]:
 at(t-.3,lambda:aim(enemies[1].get_actor_location()+unreal.Vector(0,0,25)) if not authority else None);tap(t,'LeftMouseButton','client')
at(28,lambda:check('client trace damage and infected death converge',enemies[1].state==unreal.RVInfectedState.DEAD and enemies[1].death_sequence==1,(enemies[1].vitality,enemies[1].state)))
def nearby():
 if authority:cp.set_actor_location(unreal.Vector(170,-2500,90),False,True)
 else:p.character_movement.stop_movement_immediately();p.set_actor_location(unreal.Vector(170,-2500,90),False,True)
at(29,nearby)
def player_region(region):return cp.get_component_by_class(unreal.RVCharacterPresentationComponent).get_body_region_transform(region).translation+unreal.Vector(0,0,5)
for t,r in [(31,unreal.RVBodyRegion.HEAD),(32,unreal.RVBodyRegion.TORSO),(33,unreal.RVBodyRegion.TORSO)]:
 at(t-.3,lambda r=r:aim(player_region(r)) if authority else None);tap(t,'LeftMouseButton','host')
at(34.5,lambda:check('friendly fire creates logical head/torso wounds',any(i.region==unreal.RVBodyRegion.HEAD for i in health(cp).injuries) and len(health(cp).injuries)==3,[str(i.region) for i in health(cp).injuries]))
at(34.7,lambda:check('combat feeds existing downed state',not health(cp).can_act() and health(hp).can_act()))
client_rounds=0
def remember():
 global client_rounds
 client_rounds=sum(m.magazine_rounds for m in mags(cp))
at(35,remember);tap(35.5,'LeftMouseButton','client');at(36.5,lambda:check('downed normal fire is rejected without round loss',sum(m.magazine_rounds for m in mags(cp))==client_rounds))
def supply(name):return next(i for i in items(hp) if i.definition.get_name()==name)
def dressing():
 if not authority:return
 wound=next((i for i in health(cp).injuries if i.bleeding_per_minute>0),None)
 if wound:health(hp).request_treatment(cp.get_editor_property('PlayerState'),wound.id,supply('DA_PressureDressing').id,wound.revision)
for t in [37,47,57]:at(t,dressing)
at(66,lambda:check('accepted dressings stabilize combat wounds',len(health(cp).injuries)==3 and all(i.bleeding_per_minute==0 for i in health(cp).injuries)))
def revive():
 if authority:health(hp).request_treatment(cp.get_editor_property('PlayerState'),health(cp).injuries[0].id,supply('DA_FirstAidKit').id,health(cp).injuries[0].revision)
at(68,revive);at(82,lambda:check('accepted revive restores active and retains wounds',health(cp).can_act() and len(health(cp).injuries)==3))
def snapshot():
 return {name:[{'id':guid(i.id),'definition':i.definition.get_name(),'quantity':i.quantity,'condition':i.condition,'rounds':i.magazine_rounds,'revision':i.combat_revision,'loaded_in':guid(i.loaded_in_weapon)} for i in items(c)] for name,c in [('host',hp),('client',cp)]}
def finish():
 global active,w,pc,p,other,hp,cp,enemies
 active=False
 for k in list(held):key(k,False)
 unreal.unregister_slate_post_tick_callback(handle)
 data={'role':role,'process_id':os.getpid(),'network':config.get('network',False),'results':results,'inventories':snapshot(),'passed':sum(r['pass'] for r in results),'total':len(results),'medical_feedback':health(hp).feedback,'client_wounds':[(str(i.region),i.bleeding_per_minute,i.revision) for i in health(cp).injuries]}
 (B/(config['name']+'_'+role+'.json')).write_text(json.dumps(data,indent=2));w=pc=p=other=hp=cp=None;enemies=[]
at(85,finish);events.sort(key=lambda e:e[0])
def tick(dt):
 global idx
 if not active:return
 try:
  while idx<len(events) and time.time()-start>=events[idx][0]:
   fn=events[idx][1];idx+=1;fn()
   if not active:return
 except Exception:check('runner error',False,traceback.format_exc());finish()
handle=unreal.register_slate_post_tick_callback(tick)

