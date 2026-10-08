"""Bounded runtime checks of the new downed guards with healthy positive controls.
Authority placement/injury and prepared panel-context fixtures; native P/B/H controls.
Retained diagnostic: service positive/negative passes; resource positive control
is inconclusive. Recovery evidence belongs to the earlier preserved full receipt.
"""
import unreal,json,time,os
from pathlib import Path
B=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate8MechanicalRegression')
s=json.loads((B/'session.json').read_text());start=s['start']
w=next(a for a in unreal.ObjectIterator(unreal.World) if a.get_name()=='Gate7MechanicalTest' and unreal.GameplayStatics.get_player_controller(a,0) and unreal.GameplayStatics.get_player_controller(a,0).get_controlled_pawn())
pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn();authority=unreal.GameplayStatics.get_game_mode(w) is not None;role='server' if authority else 'client'
other=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSurvivorCharacter) if a!=p)
client=other if authority else p;health=client.get_editor_property('PlayerState').get_editor_property('Health')
v=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVMechanicalMotorhome)[0];service=v.get_editor_property('EngineService');hood=v.get_editor_property('EngineHood');bus=v.get_editor_property('Electrical');recovery=v.get_editor_property('Recovery')
power=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVInteriorStation) if str(a.get_editor_property('StationName'))=='Power')
panel=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVResourcePoint) if not a.get_editor_property('bFuelFill'))
events=[];held={};rows=[];revision=None;baseline=None;frame=0;lights_before=None
def check(n,ok,d=''):rows.append({'case':n,'pass':bool(ok),'detail':str(d)});unreal.log('CLOSURE_GUARD '+role+' '+n+' '+str(bool(ok)))
def press(k,sec=.2):
 unreal.RVInteriorMotorhome.dispatch_development_key(pc,k,True);held[k]=(time.time()+sec,frame+3)
def aim(a):pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p.get_actor_location()+unreal.Vector(0,0,64),a.get_actor_location()))
def setup():
 for k,val in [('PktLagMin',100),('PktLagMax',100),('PktLoss',2)]:unreal.SystemLibrary.execute_console_command(pc,'NetEmulation.'+k+' '+str(val),pc)
 if authority:
  unreal.SystemLibrary.execute_console_command(pc,'rv.Resources.AllowDebug 1',pc)
  v.get_editor_property('CoolingSystem').debug_set_time_scale(0);v.get_editor_property('CoolingSystem').debug_set_state(.2,5,25,1);bus.debug_set_time_scale(0)
  for a,y in [(p,-75),(other,75)]:
   a.set_actor_location(v.get_actor_transform().transform_location(unreal.Vector(553,y,100)),False,True)
   # Isolate guard coverage from the already-passed E acquisition path.
   controller=a.get_controller();controller.set_editor_property('MechanicalPoint',service);controller.force_net_update()
def inspect():aim(service);press('E',.85)
def service_ready():check('healthy_prepared_service_context',pc.get_editor_property('MechanicalPoint')==service)
def openhood():
 if not authority:press('P')
def service_before():
 global revision
 check('healthy_client_native_P_opens_hood',hood.get_editor_property('bOpen'));revision=service.get_editor_property('Revision')
 if authority:health.debug_set_vitals(20,20)
def down_service():
 if not authority:press('P');press('B')
def service_after():check('downed_service_rejects_no_reservation_or_hood_change',not health.can_act() and hood.get_editor_property('bOpen') and service.get_editor_property('RepairPlayer') is None and service.get_editor_property('Revision')==revision)
def restore():
 if authority:health.debug_clear_injuries();health.debug_set_vitals(100,100)
def place_power():
 if authority:
  q=v.get_actor_transform().inverse_transform_location(panel.get_actor_location())
  v.get_editor_property('HouseBattery').debug_set_energy(1000)
  for a,dx in [(p,-45),(other,45)]:
   a.set_actor_location(v.get_actor_transform().transform_location(unreal.Vector(q.x+dx,0,185)),False,True)
   controller=a.get_controller();controller.set_editor_property('ResourcePoint',panel);controller.force_net_update()
def open_power():aim(power);press('E',.85)
def power_ready():
 global lights_before
 check('healthy_prepared_panel_context',pc.get_editor_property('ResourcePoint')==panel);lights_before=bus.is_load_powered('InteriorLights')
def healthy_generator():
 if not authority:press('H')
def power_before():
 global revision
 check('healthy_client_native_H_toggles_lights',bus.is_load_powered('InteriorLights')!=lights_before);revision=bus.get_editor_property('ControlRevision')
 if authority:health.debug_set_vitals(20,20)
def down_power():
 if not authority:press('H')
def power_after():
 check('downed_resource_control_rejected_state_revision_unchanged',not health.can_act() and bus.is_load_powered('InteriorLights')!=lights_before and bus.get_editor_property('ControlRevision')==revision)
 if not authority:check('downed_resource_feedback',pc.get_editor_property('ResourcePoint') is None and 'out of reach' in str(pc.get_editor_property('ResourceFeedback')),pc.get_editor_property('ResourceFeedback'))
def roll():
 if authority:
  v.set_actor_location(unreal.Vector(6000,6000,145),False,True);recovery.debug_overturn(90);bus.debug_advance(.001,False,0,0)
  for a,y in [(p,6300),(other,6500)]:a.set_actor_location(unreal.Vector(6000,y,100),False,True)
def recovery_before():
 global baseline
 check('roll_confirmed_before_downed_request',recovery.get_editor_property('bConfirmedOverturned'));baseline=recovery.get_editor_property('RecoveryRevision')
 if authority:health.debug_set_vitals(20,20)
def request_recovery():
 if not authority:press('F8')
def rejected():
 check('downed_F8_rejected_revision_unchanged',not health.can_act() and recovery.get_editor_property('RecoveryRevision')==baseline and v.get_actor_up_vector().z<.5)
 if not authority:check('downed_F8_feedback','Teammate assistance required' in str(pc.get_editor_property('RecoveryFeedback')),pc.get_editor_property('RecoveryFeedback'))
def accepted():check('healthy_same_client_F8_recovers',health.can_act() and recovery.get_editor_property('RecoveryRevision')==baseline+1 and v.get_actor_up_vector().z>.98)
def finish():
 for k in list(held):unreal.RVInteriorMotorhome.dispatch_development_key(pc,k,False)
 unreal.unregister_slate_post_tick_callback(handle);(B/(s['config']['name']+'_'+role+'.json')).write_text(json.dumps({'pid':os.getpid(),'role':role,'results':rows,'evidence_kind':'native Enhanced Input with authority fault/placement fixtures; representative downed guards'},indent=2))
events=[(0,setup),(3,service_ready),(3.2,openhood),(6,service_before),(8,down_service),(10,service_after),(11,restore),(12,place_power),(15,power_ready),(15.2,healthy_generator),(18,power_before),(20,down_power),(23,power_after),(25,finish)]
def tick(dt):
 global frame
 frame+=1
 try:
  for k,(deadline,f) in list(held.items()):
   if time.time()>=deadline and frame>=f:unreal.RVInteriorMotorhome.dispatch_development_key(pc,k,False);del held[k]
  if events and time.time()-start>=events[0][0]:_,fn=events.pop(0);fn()
 except Exception as e:check('harness_exception',False,repr(e));events.clear();finish()
handle=unreal.register_slate_post_tick_callback(tick)
