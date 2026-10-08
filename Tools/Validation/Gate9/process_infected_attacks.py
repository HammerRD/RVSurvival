"""Separate-process native infected attacks, death, and equipped disconnect/rejoin."""
import unreal,time,json,os,traceback
from pathlib import Path
B=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate9Validation');session=json.loads((B/'session.json').read_text());config=session['config'];start=session['start']
w=next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='Gate9CombatInfectedTest' and unreal.GameplayStatics.get_player_controller(w,0) and unreal.GameplayStatics.get_player_controller(w,0).get_controlled_pawn())
authority=unreal.GameplayStatics.get_game_mode(w) is not None;pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn();other=next(c for c in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSurvivorCharacter) if c!=p)
hp=p if authority else other;cp=other if authority else p;enemies=sorted(unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVInfected),key=lambda a:a.get_name());mine=enemies[0] if authority else enemies[1]
results=[];events=[];index=0;active=True
def check(n,ok,d=''):results.append({'case':n,'pass':bool(ok),'detail':str(d)});unreal.log('GATE9_ATTACK '+json.dumps(results[-1]))
def at(t,f):events.append((t,f))
def key(k,on):unreal.RVInteriorMotorhome.dispatch_development_key(pc,k,on)
def tap(t,k):at(t,lambda:key(k,True));at(t+.15,lambda:key(k,False))
def health(c):return c.get_editor_property('PlayerState').get_editor_property('Health')
def inv(c):return c.get_component_by_class(unreal.RVInventoryComponent)
def setup():
 if authority:
  for e in enemies:e.get_controller().get_editor_property('BrainComponent').stop_logic('isolated multiplayer bite fixture');e.get_controller().stop_movement()
  for c,e,y in [(hp,enemies[0],-3500),(cp,enemies[1],-6000)]:
   c.set_actor_location(unreal.Vector(0,y,90),False,True);e.set_actor_location(unreal.Vector(800,y,90),False,True);e.set_actor_rotation(unreal.Rotator(yaw=180),False)
   for n in ['DA_9mmHandgun','DA_9mmMagazine']:
    i=unreal.RVItemInstance();i.set_editor_property('Id',unreal.GuidLibrary.new_guid());i.set_editor_property('Definition',unreal.load_asset('/Game/Combat/Items/'+n));assert not inv(c).add_authority(i)
 pc.set_control_rotation(unreal.Rotator(yaw=90))
at(0,setup);tap(.7,'Four');tap(1.2,'R')
at(2,lambda:[e.get_controller().get_editor_property('BrainComponent').restart_logic() for e in enemies[:2]] if authority else None)
def bite_check():
 for c,e,label in [(hp,enemies[0],'host'),(cp,enemies[1],'client')]:
  injuries=health(c).injuries
  check(label+' native infected bite medical state converges',len(injuries)>0 and any(i.infection_risk>0 and i.bleeding_per_minute>0 for i in injuries),(e.attack_sequence,len(injuries)))
at(7,bite_check)
def cycle_check():
 for c,e,label in [(hp,enemies[0],'host'),(cp,enemies[1],'client')]:
  check(label+' repeated cooldown cycles bounded to one wound per completion',e.attack_sequence>=2 and 1<=len(health(c).injuries)<=e.attack_sequence,(e.attack_sequence,len(health(c).injuries)))
at(8,cycle_check)
def aim():pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p.get_actor_eyes_view_point()[0],mine.get_actor_location()+unreal.Vector(0,0,25)))
for t in [8.5,9.2,9.9]:at(t-.3,aim);tap(t,'LeftMouseButton')
at(11,lambda:check('both infected deaths replicate once',all(e.state==unreal.RVInfectedState.DEAD and e.death_sequence==1 for e in enemies[:2]),[(str(e.state),e.vitality) for e in enemies[:2]]))
def finish_client():
 global active
 if authority:return
 check('client remains equipped before disconnect',unreal.GuidLibrary.is_valid_guid(p.get_component_by_class(unreal.RVCombatComponent).get_editor_property('EquippedWeapon')))
 (B/(config['name']+'_client.json')).write_text(json.dumps({'pid':os.getpid(),'results':results},indent=2));active=False;unreal.unregister_slate_post_tick_callback(handle)
 # Only scalar clock/handle and engine functions survive the old world. Reacquire
 # the new local controller in the callback; never retain a PIE UObject for travel.
 controller=pc;execute=unreal.SystemLibrary.execute_console_command;register=unreal.register_slate_post_tick_callback;unregister=unreal.unregister_slate_post_tick_callback;clock=time.time;due=clock()+2;slot=[];iterate=unreal.ObjectIterator;world_class=unreal.World;get_controller=unreal.GameplayStatics.get_player_controller
 def rejoin(dt):
  if clock()<due:return
  unregister(slot[0])
  for current in iterate(world_class):
   local=get_controller(current,0)
   if local and local.is_local_controller():execute(local,'open 127.0.0.1:17777',local);return
 from runner_runtime import release_runners
 release_runners();execute(controller,'disconnect',controller);slot.append(register(rejoin))
at(12,finish_client)
at(14,lambda:check('equipped client disconnect removes survivor',len(unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSurvivorCharacter))==1) if authority else None)
def rejoined():
 if not authority:return
 survivors=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSurvivorCharacter)
 newcomers=[c for c in survivors if c!=p]
 check('native reconnect admits one fresh nonpersistent inventory',len(newcomers)==1 and len(inv(newcomers[0]).get_items())==0,len(survivors))
 check('reconnect does not duplicate host magazines',len(inv(p).get_items())==2 and sum(i.magazine_rounds for i in inv(p).get_items() if i.get_editor_property('bMagazineInitialized'))==12)
at(20,rejoined)
def finish():
 global active
 (B/(config['name']+'_server.json')).write_text(json.dumps({'pid':os.getpid(),'results':results},indent=2));active=False;unreal.unregister_slate_post_tick_callback(handle)
at(21,lambda:finish() if authority else None)
def tick(dt):
 global index
 if not active:return
 try:
  t=time.time()-start
  while index<len(events) and t>=events[index][0]:
   f=events[index][1];index+=1;terminating=f==finish_client and not authority;f()
   if terminating:return
   if not active:return
 except Exception:check('runner error',False,traceback.format_exc());finish() if authority else finish_client()
events.sort(key=lambda e:e[0]);handle=unreal.register_slate_post_tick_callback(tick)
if config.get('network'):
 for n,x in [('PktLagMin',100),('PktLagMax',100),('PktLoss',2)]:unreal.SystemLibrary.execute_console_command(pc,'NetEmulation.'+n+' '+str(x),pc)


