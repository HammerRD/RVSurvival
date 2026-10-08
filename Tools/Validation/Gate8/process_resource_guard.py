"""One resource guard in the accepted Gate 6 resource fixture; no broad rerun."""
import unreal,json,time,os
from pathlib import Path
B=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate8MechanicalRegression');s=json.loads((B/'session.json').read_text());start=s['start']
w=next(a for a in unreal.ObjectIterator(unreal.World) if a.get_name()=='Gate6FuelElectricalTest' and unreal.GameplayStatics.get_player_controller(a,0) and unreal.GameplayStatics.get_player_controller(a,0).get_controlled_pawn())
pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn();authority=unreal.GameplayStatics.get_game_mode(w) is not None;role='server' if authority else 'client';other=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSurvivorCharacter) if a!=p);client=other if authority else p
health=client.get_editor_property('PlayerState').get_editor_property('Health');v=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSystemsMotorhome)[0];bus=v.get_editor_property('Electrical');panel=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVResourcePoint) if not a.get_editor_property('bFuelFill'));power=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVInteriorStation) if str(a.get_editor_property('StationName'))=='Power')
rows=[];events=[];before=None;revision=None;held={};frame=0
def check(n,b,d=''):rows.append({'case':n,'pass':bool(b),'detail':str(d)});unreal.log('RESOURCE_GUARD '+role+' '+n+' '+str(b))
def setup():
 for k,val in [('PktLagMin',100),('PktLagMax',100),('PktLoss',2)]:unreal.SystemLibrary.execute_console_command(pc,'NetEmulation.'+k+' '+str(val),pc)
 if authority:
  unreal.SystemLibrary.execute_console_command(pc,'rv.Resources.AllowDebug 1',pc);v.get_editor_property('HouseBattery').debug_set_energy(1000);bus.debug_set_time_scale(0)
  for a,x in [(p,20),(other,110)]:a.set_actor_location(v.get_actor_transform().transform_location(unreal.Vector(x,0,185)),False,True)
def press(k,sec=.2):unreal.RVInteriorMotorhome.dispatch_development_key(pc,k,True);held[k]=(time.time()+sec,frame+3)
def inspect():
 pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p.get_actor_location()+unreal.Vector(0,0,64),power.get_actor_location()));press('E',1)
def prepared():
 global before
 check('normal_E_resource_panel_registered',pc.get_editor_property('ResourcePoint')==panel,{'feedback':str(pc.get_editor_property('ResourceFeedback')),'position':str(p.get_actor_location()),'panel':str(panel.get_actor_location())});before=bus.is_load_powered('InteriorLights')
def change():
 if not authority:pc.request_resource_control('InteriorLights',not before,bus.get_editor_property('ControlRevision'))
def positive():
 global revision
 check('healthy_owned_resource_request_changes_load',bus.is_load_powered('InteriorLights')!=before,pc.get_editor_property('ResourceFeedback'));revision=bus.get_editor_property('ControlRevision')
 if authority:health.debug_set_vitals(20,20)
def downed():
 if not authority:pc.request_resource_control('InteriorLights',before,bus.get_editor_property('ControlRevision'))
def rejected():
 check('downed_owned_resource_request_rejected',not health.can_act() and bus.is_load_powered('InteriorLights')!=before and bus.get_editor_property('ControlRevision')==revision)
 if not authority:check('downed_resource_owner_feedback','out of reach' in str(pc.get_editor_property('ResourceFeedback')) and pc.get_editor_property('ResourcePoint') is None,pc.get_editor_property('ResourceFeedback'))
def finish():
 for k in list(held):unreal.RVInteriorMotorhome.dispatch_development_key(pc,k,False)
 unreal.unregister_slate_post_tick_callback(handle);(B/(s['config']['name']+'_'+role+'.json')).write_text(json.dumps({'pid':os.getpid(),'role':role,'results':rows,'evidence_kind':'accepted Gate6 approach fixture; normal E; owned resource request API with healthy positive control and downed repeat'},indent=2))
events=[(0,setup),(3,inspect),(6,prepared),(6.2,change),(9,positive),(12,downed),(15,rejected),(17,finish)]
def tick(dt):
 global frame
 frame+=1
 try:
  for k,(deadline,f) in list(held.items()):
   if time.time()>=deadline and frame>=f:unreal.RVInteriorMotorhome.dispatch_development_key(pc,k,False);del held[k]
  if events and time.time()-start>=events[0][0]:_,fn=events.pop(0);fn()
 except Exception as e:check('harness_exception',False,repr(e));events.clear();finish()
handle=unreal.register_slate_post_tick_callback(tick)
