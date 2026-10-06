"""Reconnect harness deliberately keeps only primitive state between native world changes."""
import unreal,json,time,os
B='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate5Validation/'
started=time.time();phase=0;phase_at=started;rows=[];before={};fallback_world=None
def check(name,ok,detail=''):rows.append({'case':name,'pass':bool(ok),'detail':str(detail)});unreal.log('GATE5_RECONNECT '+json.dumps(rows[-1]))
def owned_world(required=True):
 # World iteration may include cached/old map objects. LocalPlayer controller lookup
 # can return the current controller for them; resolve the pawn's actual owning world.
 for candidate in unreal.ObjectIterator(unreal.World):
  pc=unreal.GameplayStatics.get_player_controller(candidate,0)
  if not pc:continue
  pawn=pc.get_controlled_pawn()
  if not pawn or not unreal.SystemLibrary.is_valid(pawn):continue
  actual=pawn.get_outer().get_outer()
  if isinstance(actual,unreal.World) and (not required or actual.get_name()=='Gate5SurvivalTest'):
   return actual
 raise StopIteration
def snapshot():
 w=owned_world();pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn();ps=pc.get_editor_property('PlayerState')
 if ps is None:raise StopIteration
 n=ps.get_editor_property('Needs');s=n.get_editor_property('State')
 c=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVStoragePoint) if str(a.get_editor_property('Container').get_editor_property('DisplayName'))=='External storage').get_editor_property('Container')
 return {'world':w.get_path_name(),'controller':pc.get_path_name(),'pawn':p.get_name(),'nutrition':s.nutrition,'hydration':s.hydration,'fatigue':s.fatigue,'rest':str(s.rest_mode),'quantity':sum(x.quantity for x in p.get_component_by_class(unreal.RVInventoryComponent).get_items()),'container_quantity':sum(x.quantity for x in c.get_items()),'authority':unreal.GameplayStatics.get_game_mode(w) is not None}
def action(name):
 w=owned_world(name not in ['reconnect']);pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn();ps=pc.get_editor_property('PlayerState')
 if ps is None:raise StopIteration
 n=ps.get_editor_property('Needs')
 if name in ['disconnect','reconnect']:
  # Engine command queues native travel; function-local UObject wrappers leave scope before it executes.
  previous_world=w.get_name();unreal.SystemLibrary.execute_console_command(pc,name,pc);return previous_world
 if name in ['hold_bed','hold_storage']:
  if name=='hold_bed':a=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVRestPoint) if str(a.get_editor_property('DisplayName'))=='Rear bed')
  else:a=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVStoragePoint) if str(a.get_editor_property('Container').get_editor_property('DisplayName'))=='External storage')
  pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p.get_actor_location()+unreal.Vector(0,0,64),a.get_actor_location()));unreal.SystemLibrary.execute_console_command(pc,'Input.+key E',pc)
 if name=='release':unreal.SystemLibrary.execute_console_command(pc,'Input.-key E',pc)
 if name=='sleep':n.request_rest_mode(unreal.RVRestMode.SLEEPING)
 if name=='foreign':
  other=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSurvivorCharacter) if a!=p);n.request_consume(other.get_component_by_class(unreal.RVInventoryComponent).get_items()[0].id)
 if name=='withdraw':
  c=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVStoragePoint) if str(a.get_editor_property('Container').get_editor_property('DisplayName'))=='External storage').get_editor_property('Container')
  p.get_component_by_class(unreal.RVInventoryComponent).request_transfer(next(x for x in c.get_items() if str(x.definition.get_editor_property('CatalogId'))=='Food').id,1,False)
 if name=='consume':
  item=p.get_component_by_class(unreal.RVInventoryComponent).get_items()[0];check('rejoined_item_state_preserved',abs(item.condition-.54)<.001 and item.custom_state[0].value=='ReconnectTest');n.request_consume(item.id)
def finish():
 unreal.unregister_slate_post_tick_callback(h);json.dump({'pid':os.getpid(),'results':rows,'before':before},open(B+'reconnect_client.json','w'),indent=2)
def tick(dt):
 global phase,phase_at,before,fallback_world
 try:
  now=time.time();elapsed=now-phase_at
  if phase==0:
   s=snapshot()
   if s['authority']:return
   phase=1;phase_at=now
  elif phase==1 and elapsed>2:action('hold_bed');phase=2;phase_at=now
  elif phase==2 and elapsed>1:action('release');action('sleep');phase=3;phase_at=now
  elif phase==3 and elapsed>1:
   before=snapshot();check('sleeping_before_disconnect','SLEEPING' in before['rest']);action('disconnect');phase=4;phase_at=now
  elif phase==4 and elapsed>5:fallback_world=action('reconnect');check('native_disconnect_loaded_fallback',fallback_world=='Gate1Test',fallback_world);phase=5;phase_at=now
  elif phase==5:
   s=snapshot()
   if s['authority']:return
   check('same_process_rejoined_after_native_travel',fallback_world=='Gate1Test' and not s['authority'],s);phase=6;phase_at=now
  elif phase==6 and elapsed>2:action('foreign');action('hold_storage');phase=7;phase_at=now
  elif phase==7 and elapsed>1:action('release');phase=8;phase_at=now
  elif phase==8 and elapsed>1:action('withdraw');phase=9;phase_at=now
  elif phase==9 and elapsed>1:action('consume');phase=10;phase_at=now
  elif phase==10 and elapsed>1:
   s=snapshot();check('rejoined_consume_authoritative',abs(s['nutrition']-55)<.01 and s['quantity']==0 and s['container_quantity']==2,s);finish();return
  if now-started>80:check('reconnect_timeout',False);finish()
 except StopIteration:return
 except Exception as e:check('runner_exception',False,repr(e));finish()
h=unreal.register_slate_post_tick_callback(tick)
