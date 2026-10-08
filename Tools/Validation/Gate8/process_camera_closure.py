"""Parked client driver, supported Enhanced Input orbit injection and real UI remap window."""
import unreal,json,time,os
from pathlib import Path
B=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate8MechanicalRegression')
s=json.loads((B/'session.json').read_text());start=s['start'];w=next(a for a in unreal.ObjectIterator(unreal.World) if a.get_name()=='Gate7MechanicalTest' and unreal.GameplayStatics.get_player_controller(a,0) and unreal.GameplayStatics.get_player_controller(a,0).get_controlled_pawn())
pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn();authority=unreal.GameplayStatics.get_game_mode(w) is not None;role='server' if authority else 'client';other=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSurvivorCharacter) if a!=p)
v=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVMechanicalMotorhome)[0];seat=next(a for a in v.get_seats() if a.get_editor_property('bDriverSeat')== (not authority));entry=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVVehicleEntryPoint) if a.get_editor_property('Seat')==seat and abs(v.get_actor_transform().inverse_transform_location(a.get_actor_location()).y)>100)
arm=v.get_component_by_class(unreal.SpringArmComponent);rows=[];samples=[];held=False;events=[];before=None;after=None
def check(n,b,d=''):rows.append({'case':n,'pass':bool(b),'detail':str(d)});unreal.log('CAMERA_CLOSURE '+role+' '+n+' '+str(bool(b)))
def setup():
 for key,val in [('PktLagMin',100),('PktLagMax',100),('PktLoss',2)]:unreal.SystemLibrary.execute_console_command(pc,'NetEmulation.'+key+' '+str(val),pc)
 if authority:
  for c in [p,other]:
   driver=c==other;a=next(a for a in v.get_seats() if a.get_editor_property('bDriverSeat')==driver);ep=next(e for e in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVVehicleEntryPoint) if e.get_editor_property('Seat')==a and abs(v.get_actor_transform().inverse_transform_location(e.get_actor_location()).y)>100)
   q=v.get_actor_transform().inverse_transform_location(ep.get_actor_location());c.set_actor_location(v.get_actor_transform().transform_location(unreal.Vector(q.x,q.y+(-125 if driver else 125),100)),False,True)
def aim():pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p.get_actor_location()+unreal.Vector(0,0,p.get_editor_property('BaseEyeHeight')),entry.get_actor_location()))
def key(on):unreal.RVInteriorMotorhome.dispatch_development_key(pc,'E',on)
def seated():check('normal_E_client_driver_host_passenger',seat.get_editor_property('Occupant')==p and (authority or pc.get_controlled_pawn()==v))
def angle():r=arm.get_editor_property('RelativeRotation');return [r.pitch,r.yaw,r.roll]
def orbit_start():
 global before
 before=angle()
def inject():
 if authority:return
 sub=next(a for a in unreal.ObjectIterator(unreal.EnhancedInputLocalPlayerSubsystem) if a.get_user_settings() is not None)
 sub.inject_input_vector_for_player_mapping('OrbitHold',unreal.Vector(1,0,0),[],[])
 sub.inject_input_vector_for_player_mapping('OrbitYaw',unreal.Vector(2,0,0),[],[])
 sub.inject_input_vector_for_player_mapping('OrbitPitch',unreal.Vector(1,0,0),[],[])
def orbit_check():
 global after
 after=angle()
 if not authority:check('supported_Enhanced_Input_orbit_changes_camera',abs(after[1]-before[1])>1 and abs(after[0]-before[0])>.5,{'before':before,'after':after})
def release_check():
 if not authority:check('orbit_release_does_not_drift',abs(angle()[1]-after[1])<.01 and abs(angle()[0]-after[0])<.01,angle())
def finish():
 key(False);unreal.unregister_slate_post_tick_callback(handle)
 (B/(s['config']['name']+'_'+role+'.json')).write_text(json.dumps({'pid':os.getpid(),'role':role,'results':rows,'samples':samples,'evidence_kind':'normal E seats; official Enhanced Input mapping injection for orbit; separate real Windows UI remap observations'},indent=2))
events=[(0,setup),(2,aim),(2.3,lambda:key(True)),(3.3,lambda:key(False)),(5,seated),(6,orbit_start),(8,orbit_check),(9,release_check)]
nextsample=0
def tick(dt):
 global nextsample
 try:
  elapsed=time.time()-start
  if events and elapsed>=events[0][0]:_,fn=events.pop(0);fn()
  if 6.2<elapsed<7.5:inject()
  if elapsed>nextsample:
   nextsample=elapsed+1;samples.append({'t':elapsed,'camera':angle(),'driver':pc.get_controlled_pawn()==v})
   (B/(s['config']['name']+'_'+role+'_samples.json')).write_text(json.dumps(samples,indent=2))
  flag=B/'finish-camera.flag'
  if elapsed>210 or (flag.exists() and flag.stat().st_mtime>start):finish()
 except Exception as e:check('harness_exception',False,repr(e));events.clear();finish()
handle=unreal.register_slate_post_tick_callback(tick)
