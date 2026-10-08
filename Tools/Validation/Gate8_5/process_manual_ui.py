"""Owned RPC medical diagnostics in separate PIE processes, not manual UI evidence."""
import unreal,json,time,os
from pathlib import Path
B=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate8_5Validation')
session=json.loads((B/'session.json').read_text());config=session['config'];start=session['start']
w=next(a for a in unreal.ObjectIterator(unreal.World) if a.get_name()=='Gate8_5CharacterTest' and unreal.GameplayStatics.get_player_controller(a,0) and unreal.GameplayStatics.get_player_controller(a,0).get_controlled_pawn())
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
 for c,x in [(healer,-600),(patient,240)]:c.set_actor_location(unreal.Vector(x,-500,95),False,True)
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

initialized=False;nextsample=0;samples=[]

scene_events=[];scene_camera=None;scene_hidden=False;self_seeded=False
onfoot=[]
def native(k,on):
 if is_healer:unreal.RVInteriorMotorhome.dispatch_development_key(pc,k,on)
def scene_at(t,fn):scene_events.append((t,fn))
def owner_down():
 if is_healer:pc.set_control_rotation(unreal.Rotator(pitch=-75))
def owner_forward():
 if is_healer:pc.set_control_rotation(unreal.Rotator())
def shot(name):unreal.SystemLibrary.execute_console_command(pc,'shot showui filename='+str(B/(config['name']+'_'+role+'_'+name+'.png')).replace('\\','/')+' -nosuffix',pc)
def observe_foot(name):
 global scene_camera,scene_hidden
 movement=healer.get_component_by_class(unreal.CharacterMovementComponent);mesh=healer.get_editor_property('Mesh');anim=mesh.get_anim_instance()
 onfoot.append({'name':name,'velocity':str(movement.get_editor_property('Velocity')),'pose':anim.get_editor_property('PoseIndex'),'animation_speed':anim.get_editor_property('GroundSpeed'),'mode':str(movement.get_editor_property('MovementMode'))})
 if is_healer:return
 target=mesh.get_socket_location('pelvis')+unreal.Vector(0,0,10);location=target+unreal.Vector(-200,150,45);rotation=unreal.MathLibrary.find_look_at_rotation(location,target)
 if scene_camera is None:scene_camera=unreal.RVCharacterContentLibrary.spawn_observation_camera(healer,location,rotation)
 else:scene_camera.set_actor_location_and_rotation(location,rotation,False,True)
 if not scene_hidden:unreal.SystemLibrary.execute_console_command(pc,'showhud',pc);scene_hidden=True
 pc.set_view_target_with_blend(scene_camera,0)
def clinical_ready():
 global scene_hidden
 if authority:
  healer.set_actor_location(unreal.Vector(100,-500,95),False,True);healer.get_component_by_class(unreal.CharacterMovementComponent).stop_movement_immediately()
 if not is_healer:
  pc.set_view_target_with_blend(pc.get_controlled_pawn(),0)
  if scene_hidden:unreal.SystemLibrary.execute_console_command(pc,'showhud',pc);scene_hidden=False
 (B/(config['name']+'_'+role+'_onfoot.json')).write_text(json.dumps(onfoot,indent=2))
 unreal.log('MANUAL_MEDICAL_READY')
def self_supply():
 if not authority:return
 health.debug_apply_injury(unreal.RVInjuryKind.WOUND,unreal.RVBodyRegion.LEFT_ARM,1)
 i=unreal.RVItemInstance();i.set_editor_property('Id',unreal.GuidLibrary.new_guid());i.set_editor_property('Definition',unreal.load_asset('/Game/Medical/DA_Bandage'));i.set_editor_property('Quantity',1);i.set_editor_property('Condition',.71);inv.add_authority(i)
 unreal.log('SELF_TREATMENT_READY')
scene_at(2,owner_down);scene_at(2.2,lambda:shot('owner-down') if is_healer else None);scene_at(2.6,owner_forward)
for when,key,duration,name in [(3,'W',.6,'forward'),(4.2,'S',.5,'backward'),(5.3,'A',.5,'left_strafe'),(6.3,'D',.5,'right_strafe'),(7.1,'SpaceBar',.15,'jump')]:
 scene_at(when,lambda key=key:native(key,True));scene_at(when+duration,lambda key=key:native(key,False));scene_at(when+.25,lambda name=name:observe_foot(name));scene_at(when+.35,lambda name=name:shot(name) if not is_healer else None)
for when,name in [(1.7,'idle'),(7.8,'fall'),(8.1,'land')]:scene_at(when,lambda name=name:observe_foot(name));scene_at(when+.1,lambda name=name:shot(name) if not is_healer else None)
scene_at(8.8,clinical_ready);scene_at(55,self_supply);scene_events.sort(key=lambda e:e[0])

def tick(dt):
 global initialized,nextsample
 if not initialized and time.time()-start>=1:setup();initialized=True
 while scene_events and time.time()-start>=scene_events[0][0]:_,fn=scene_events.pop(0);fn()
 if initialized and time.time()>nextsample:
  nextsample=time.time()+.5
  widgets=[a.get_path_name() for a in unreal.ObjectIterator(unreal.RVMedicalWidget)]
  texts=[{'path':t.get_path_name(),'text':str(t.get_text())} for t in unreal.ObjectIterator(unreal.TextBlock) if 'Medical' in t.get_path_name()]
  samples.append({'time':time.time(),'patient_active':ph.can_act(),'bleeding':wound().bleeding_per_minute if ph.get_editor_property('Injuries') else None,'feedback':str(health.get_editor_property('Feedback')),'widgets':widgets,'texts':texts,'supplies':[(str(i.definition.get_editor_property('DisplayName')),i.quantity) for i in inv.get_items()]})
  (B/(config['name']+'_'+role+'_samples.json')).write_text(json.dumps(samples,indent=2))
 if time.time()-start>150 or ((B/'finish-client-ui.flag').exists() and (B/'finish-client-ui.flag').stat().st_mtime>start):
  unreal.unregister_slate_post_tick_callback(handle);(B/(config['name']+'_'+role+'.json')).write_text(json.dumps({'pid':os.getpid(),'role':role,'kind':'read-only sampler; normal OS F9 and UMG mouse controls','last_sample':samples[-1] if samples else {}},indent=2))
handle=unreal.register_slate_post_tick_callback(tick)
