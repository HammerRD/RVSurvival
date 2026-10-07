"""Real native disconnect/reconnect during repair. No persistent UObject wrappers.
Each callback reacquires the pawn's actual world; only primitive receipts survive travel.
"""
import unreal,time,json,os
from pathlib import Path
B=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate7Validation')
session=json.loads((B/'session.json').read_text());start=session['start'];config=session['config']
rows=[];phase=0;due=start;held=None;authority=None;cycle=0;old_pawn='';stock_ids=[];initial_revision=0

def check(n,ok,d=''):rows.append({'case':n,'pass':bool(ok),'detail':str(d)});unreal.log('GATE7_DISCONNECT '+json.dumps(rows[-1]))
def current():
 for candidate in unreal.ObjectIterator(unreal.World):
  pc=unreal.GameplayStatics.get_player_controller(candidate,0)
  if not pc:continue
  p=pc.get_controlled_pawn()
  if not p or not unreal.SystemLibrary.is_valid(p):continue
  w=p.get_outer().get_outer()
  if isinstance(w,unreal.World):return w,pc,p
 raise StopIteration
def context():
 w,pc,p=current()
 if w.get_name()!='Gate7MechanicalTest':raise StopIteration
 v=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVMechanicalMotorhome)[0]
 point=v.get_editor_property('EngineService');hood=v.get_editor_property('EngineHood')
 if point is None or hood is None or point.get_editor_property('Vehicle')!=v:raise StopIteration
 return w,pc,p,v,v.get_editor_property('CoolingSystem'),point
def seed(inv,cat,q):
 r=unreal.RVItemInstance();r.set_editor_property('Id',unreal.GuidLibrary.new_guid());r.set_editor_property('Definition',unreal.load_asset('/Game/Mechanical/DA_'+cat));r.set_editor_property('Quantity',q);r.set_editor_property('Condition',.71);inv.add_authority(r)
def key(k,seconds=.2):
 global held
 w,pc,p=current();unreal.RVInteriorMotorhome.dispatch_development_key(pc,k,True);held=(k,time.time()+seconds)
def aim():
 w,pc,p,v,c,point=context();pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p.get_actor_location()+unreal.Vector(0,0,64),point.get_actor_location()))
def travel(command):
 # Engine queues native travel; function-local wrappers leave scope first.
 w,pc,p=current();unreal.SystemLibrary.execute_console_command(pc,command,pc)
def stock(w):return next(a.get_editor_property('Container') for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVExteriorStoragePoint) if str(a.get_editor_property('DoorPartName'))=='Art_RV_Van_Compartment_02')
def prepare_remote():
 global old_pawn
 w,pc,p,v,c,point=context();remote=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSurvivorCharacter) if a!=p)
 old_pawn=remote.get_name();remote.set_actor_location(v.get_actor_transform().transform_location(unreal.Vector(550,75,100)),False,True)
 inv=remote.get_component_by_class(unreal.RVInventoryComponent);seed(inv,'MechanicTools',1);seed(inv,'RadiatorPatch',3)
def finish():
 unreal.unregister_slate_post_tick_callback(h)
 (B/(config['name']+'_'+('server' if authority else 'client')+'.json')).write_text(json.dumps({'pid':os.getpid(),'results':rows,'cycles':cycle},indent=2),encoding='utf-8')
def server_step(now):
 global phase,due,cycle,stock_ids,initial_revision
 w,pc,p,v,c,point=context();chars=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSurvivorCharacter)
 if phase==0:
  unreal.SystemLibrary.execute_console_command(pc,'t.MaxFPS 60',pc);c.debug_set_time_scale(0);c.debug_set_state(.2,9,20,1)
  p.set_actor_location(v.get_actor_transform().transform_location(unreal.Vector(550,-75,100)),False,True)
  seed(p.get_component_by_class(unreal.RVInventoryComponent),'MechanicTools',1);seed(p.get_component_by_class(unreal.RVInventoryComponent),'RadiatorPatch',2)
  seed(stock(w),'CoolantPartial',1);stock_ids=[unreal.GuidLibrary.conv_guid_to_string(i.id) for i in stock(w).get_items()]
  prepare_remote();phase=1;due=now+1
 elif phase==1 and now>due:aim();phase=2;due=now+.5
 elif phase==2 and now>due:key('E',.85);phase=3;due=now+1.5
 elif phase==3 and now>due:key('P');phase=4
 elif phase==4 and len(chars)==1:
  phase=9;due=now+.5
 elif phase==9 and now>due:
  check('disconnect_'+str(cycle)+'_clears_reservation',not point.get_editor_property('RepairPlayer'))
  check('disconnect_'+str(cycle)+'_shared_stock_intact',stock_ids==[unreal.GuidLibrary.conv_guid_to_string(i.id) for i in stock(w).get_items()])
  phase=5;due=now+8.5
 elif phase==5 and now>due:
  check('disconnect_'+str(cycle)+'_no_late_completion',not c.get_editor_property('Cooling').get_editor_property('bTemporaryPatch') and c.get_editor_property('Cooling').radiator_condition<.3)
  phase=6
 elif phase==6 and len(chars)==2:
  remote=next(a for a in chars if a!=p)
  if remote.get_name()==old_pawn:return
  check('reconnect_'+str(cycle)+'_new_pawn',True,remote.get_name());prepare_remote();phase=7
 elif phase==7 and c.get_editor_property('Cooling').get_editor_property('bTemporaryPatch'):
  remote=next(a for a in chars if a!=p);inv=remote.get_component_by_class(unreal.RVInventoryComponent)
  check('reconnect_'+str(cycle)+'_repair_exact_consumption',sum(i.quantity for i in inv.get_items() if str(i.definition.get_editor_property('CatalogId'))=='RadiatorPatch')==2 and not point.get_editor_property('RepairPlayer'))
  phase=8;due=now+3
 elif phase==8 and now>due:
  cycle+=1
  if cycle<2:c.debug_set_state(.2,9,20,1);phase=4
  else:
   check('host_survival_and_shared_stock_valid',pc.player_state.get_editor_property('Needs').get_editor_property('State').nutrition>0 and stock_ids==[unreal.GuidLibrary.conv_guid_to_string(i.id) for i in stock(w).get_items()]);finish();return
def client_step(now):
 global phase,due,cycle
 if phase==0:
  w,pc,p,v,c,point=context();unreal.SystemLibrary.execute_console_command(pc,'t.MaxFPS 60',pc)
  if (p.get_actor_location()-point.get_actor_location()).length()>250:return
  phase=1;due=now+4
 elif phase==1 and now>due:aim();phase=2;due=now+.5
 elif phase==2 and now>due:key('E',.85);phase=3;due=now+1.5
 elif phase==3 and now>due:
  w,pc,p,v,c,point=context()
  if c.get_editor_property('Cooling').get_editor_property('bTemporaryPatch'):return
  key('B');phase=4;due=now+1
 elif phase==4 and now>due:
  w,pc,p,v,c,point=context();check('client_'+str(cycle)+'_repair_started_before_disconnect',point.get_editor_property('RepairPlayer')==pc.player_state);travel('disconnect');phase=5;due=now+11
 elif phase==5 and now>due:
  w,pc,p=current();check('client_'+str(cycle)+'_fallback_world_after_disconnect',w.get_name()!='Gate7MechanicalTest',w.get_name());travel('reconnect');phase=6
 elif phase==6:
  w,pc,p,v,c,point=context()
  if not p.get_editor_property('PlayerState') or not p.get_component_by_class(unreal.RVInventoryComponent).get_items():return
  check('client_'+str(cycle)+'_rejoined_same_process',unreal.GameplayStatics.get_game_mode(w) is None)
  aim();phase=7;due=now+.5
 elif phase==7 and now>due:key('E',.85);phase=8;due=now+1.5
 elif phase==8 and now>due:key('B');phase=9;due=now+9
 elif phase==9 and now>due:
  w,pc,p,v,c,point=context();check('client_'+str(cycle)+'_repair_replication_after_rejoin',c.get_editor_property('Cooling').get_editor_property('bTemporaryPatch') and not point.get_editor_property('RepairPlayer'))
  cycle+=1
  if cycle<2:phase=3;due=now+2
  else:finish();return
def tick(dt):
 global authority,held
 try:
  now=time.time()
  if now<start:return
  if held and now>held[1]:
   w,pc,p=current();unreal.RVInteriorMotorhome.dispatch_development_key(pc,held[0],False);held=None
  if authority is None:
   w,pc,p=current();authority=unreal.GameplayStatics.get_game_mode(w) is not None
  if now-start>120:raise TimeoutError('disconnect cycle timeout')
  if authority:server_step(now)
  else:client_step(now)
 except StopIteration:return
 except Exception as e:check('harness_exception',False,repr(e));finish()
h=unreal.register_slate_post_tick_callback(tick)
