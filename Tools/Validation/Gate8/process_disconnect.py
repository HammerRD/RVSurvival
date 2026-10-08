"""Owned RPC medical diagnostics in separate PIE processes, not manual UI evidence."""
import unreal,json,time,os
from pathlib import Path
B=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate8Validation')
session=json.loads((B/'session.json').read_text());config=session['config'];start=session['start']
w=next(a for a in unreal.ObjectIterator(unreal.World) if a.get_name()=='Gate8MedicalTest' and unreal.GameplayStatics.get_player_controller(a,0) and unreal.GameplayStatics.get_player_controller(a,0).get_controlled_pawn())
authority=unreal.GameplayStatics.get_game_mode(w) is not None;role='server' if authority else 'client'
pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn()
other=next(c for c in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSurvivorCharacter) if c!=p)
is_healer=authority==(config['healer']=='host');healer=p if is_healer else other;patient=other if is_healer else p
hs=healer.get_editor_property('PlayerState');ps=patient.get_editor_property('PlayerState')
health=hs.get_editor_property('Health');ph=ps.get_editor_property('Health');inv=healer.get_component_by_class(unreal.RVInventoryComponent)
results=[];events=[]
def check(name,value,detail=''):results.append({'case':name,'pass':bool(value),'detail':str(detail)})
def supply(name):return next(i for i in inv.get_items() if str(i.definition.get_editor_property('DisplayName'))==name)
def wound():return next(i for i in ph.get_editor_property('Injuries') if i.kind==unreal.RVInjuryKind.WOUND)
def setup():
 unreal.SystemLibrary.execute_console_command(pc,'t.MaxFPS 60',pc)
 if config.get('network'):
  for key,val in [('PktLagMin',100),('PktLagMax',100),('PktLoss',2)]:unreal.SystemLibrary.execute_console_command(pc,'NetEmulation.'+key+' '+str(val),pc)
 if not authority:return
 for c,x in [(healer,100),(patient,190)]:c.set_actor_location(unreal.Vector(x,-500,95),False,True)
 ph.debug_apply_injury(unreal.RVInjuryKind.WOUND,unreal.RVBodyRegion.TORSO,2)
 ph.debug_apply_injury(unreal.RVInjuryKind.FRACTURE,unreal.RVBodyRegion.LEFT_LEG,2)
 ph.debug_set_vitals(20,20)
 for name in ['PressureDressing','FirstAidKit']:
  item=unreal.RVItemInstance();item.set_editor_property('Id',unreal.GuidLibrary.new_guid());item.set_editor_property('Definition',unreal.load_asset('/Game/Medical/DA_'+name));item.set_editor_property('Quantity',2);item.set_editor_property('Condition',.71);inv.add_authority(item)
def initial():
 check('patient_downed_replicates',not ph.can_act())
 check('healer_independent_active',health.can_act())
 if is_healer:health.request_treatment(ps,wound().id,supply('FirstAidKit').id,0)
def blocked():
 check('bleeding_revive_rejected',supply('FirstAidKit').quantity==2 and not ph.can_act())
 if is_healer:health.request_treatment(ps,wound().id,supply('PressureDressing').id,wound().revision)
def bandaged():
 check('teammate_bleeding_stopped',wound().bleeding_per_minute==0)
 check('dressing_consumed_once',supply('PressureDressing').quantity==1)
 check('patient_still_downed',not ph.can_act())
 if is_healer:
  for _ in range(2):health.request_treatment(ps,wound().id,supply('FirstAidKit').id,wound().revision)
def revived():
 check('revive_active_converges',ph.can_act())
 check('concurrent_request_single_consumption',supply('FirstAidKit').quantity==1)
 check('revive_retains_injuries',len(ph.get_editor_property('Injuries'))==2)
 attrs=ps.get_editor_property('MedicalAttributes')
 blood=attrs.get_editor_property('Blood').get_editor_property('CurrentValue')
 check('revive_partial_vitals',29<=blood<40,blood)
 check('healer_unaffected_blood',hs.get_editor_property('MedicalAttributes').get_editor_property('Blood').get_editor_property('CurrentValue')>99)
 check('condition_preserved',all(abs(i.condition-.71)<.0001 for i in inv.get_items()))
 if is_healer:health.request_treatment(ps,wound().id,supply('FirstAidKit').id,wound().revision)
def finish():
 check('awake_revive_rejected',supply('FirstAidKit').quantity==1)
 unreal.unregister_slate_post_tick_callback(handle)
 (B/(config['name']+'_'+role+'.json')).write_text(json.dumps({'pid':os.getpid(),'role':role,'kind':'owned RPC diagnostics, no UI acceptance','results':results},indent=2))
def begin_disconnect_case():
 if is_healer:health.request_treatment(ps,wound().id,supply('PressureDressing').id,wound().revision)
def leave_client():
 if authority:return
 check('client_exits_during_hold',unreal.GuidLibrary.is_valid_guid(health.get_editor_property('ActiveTreatment')))
 unreal.unregister_slate_post_tick_callback(handle)
 (B/(config['name']+'_client.json')).write_text(json.dumps({'pid':os.getpid(),'role':'client','results':results,'intentional_disconnect':True},indent=2))
 unreal.SystemLibrary.execute_console_command(pc,'quit',pc)
def server_verify():
 if not authority:return
 check('server_survived_disconnect',pc.get_controlled_pawn() is not None)
 if is_healer:
  check('patient_disconnect_releases_hold',not unreal.GuidLibrary.is_valid_guid(health.get_editor_property('ActiveTreatment')))
  check('patient_disconnect_retains_supply',supply('PressureDressing').quantity==2)
 else:
  check('healer_disconnect_no_late_treatment',wound().bleeding_per_minute==3)
  check('downed_patient_retained',not ph.can_act())
 unreal.unregister_slate_post_tick_callback(handle)
 (B/(config['name']+'_server.json')).write_text(json.dumps({'pid':os.getpid(),'role':'server','results':results},indent=2))
events=[(1,setup),(6,begin_disconnect_case),(8,leave_client),(20,server_verify)]
def tick(dt):
 try:
  if events and time.time()-start>=events[0][0]:_,fn=events.pop(0);fn()
 except Exception as e:
  results.append({'case':'harness_exception','pass':False,'detail':repr(e)})
  unreal.unregister_slate_post_tick_callback(handle);events.clear()
  (B/(config['name']+'_'+role+'.json')).write_text(json.dumps({'pid':os.getpid(),'results':results},indent=2))
handle=unreal.register_slate_post_tick_callback(tick)

