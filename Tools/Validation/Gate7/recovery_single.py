"""Physics-settled rollover fixtures; recovery intent uses the mapped F8 action."""
import unreal,json,time,math
from pathlib import Path
B=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate7Validation')
w=next(a for a in unreal.ObjectIterator(unreal.World) if a.get_name()=='Gate7MechanicalTest' and 'UEDPIE_' in a.get_path_name())
pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn()
v=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVMechanicalMotorhome)[0]
r=v.get_editor_property('Recovery');mesh=v.get_component_by_class(unreal.SkeletalMeshComponent)
results=[];events=[];samples=[];start=time.time();held=None;before=None;force_until=0;blocker=None
def check(n,b,d=''):
 results.append({'case':n,'pass':bool(b),'detail':str(d)});unreal.log('RECOVERY '+n+' '+str(bool(b)))
def press():
 global held
 unreal.RVInteriorMotorhome.dispatch_development_key(pc,'F8',True);held=time.time()+.2
def state():
 return {'position':str(v.get_actor_location()),'rotation':str(v.get_actor_rotation()),'speed':v.get_velocity().length(),'ready':r.get_editor_property('bConfirmedOverturned'),'revision':r.get_editor_property('RecoveryRevision'),'feedback':pc.get_editor_property('RecoveryFeedback')}
def fixture(roll):
 v.set_actor_location(unreal.Vector(6000,6000,145),False,True)
 p.set_actor_location(unreal.Vector(6500,6000,100),False,True)
 check('debug_roll_'+str(roll),r.debug_overturn(roll))
 pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p.get_actor_location()+unreal.Vector(0,0,64),v.get_actor_location()+unreal.Vector(0,0,150)))
def photo(name):
 unreal.SystemLibrary.execute_console_command(pc,'shot showui filename=D:/GitHub/RVSurvival/RVSurvival/Saved/Gate7Recovery/'+name+'.png -nosuffix',pc)
def force_motion():
 global force_until
 force_until=time.time()+2
def block():
 global blocker
 q=v.get_actor_location();blocker=r.debug_create_surface(unreal.Vector(q.x,q.y,450),unreal.Rotator(),unreal.Vector(1000,1000,200));assert blocker
def unblock():
 global blocker
 blocker.destroy_actor();blocker=None
def debug_recover():unreal.SystemLibrary.execute_console_command(pc,'RVRecover',pc)
def request(label):
 global before
 check(label+'_settled_ready',r.get_editor_property('bConfirmedOverturned'),state());before=v.get_actor_location();press()
def recovered(label):
 check(label+'_upright',v.get_actor_up_vector().z>.98,state())
 check(label+'_near_original',math.hypot(before.x-v.get_actor_location().x,before.y-v.get_actor_location().y)<450,state())
 check(label+'_repeat_unavailable',not r.get_editor_property('bConfirmedOverturned'));press()
def repeated(label,revision):check(label+'_upright_repeat_rejected',r.get_editor_property('RecoveryRevision')==revision,state())
def finish():
 unreal.unregister_slate_post_tick_callback(h)
 if held:unreal.RVInteriorMotorhome.dispatch_development_key(pc,'F8',False)
 (B/'recovery-single.json').write_text(json.dumps({'results':results,'samples':samples},indent=2),encoding='utf-8')
v.get_editor_property('CoolingSystem').debug_set_time_scale(0)
v.get_editor_property('Electrical').debug_set_time_scale(0)
for i,roll in enumerate([90,-90,180]):
 t=i*20
 events.extend([(t,lambda roll=roll:fixture(roll)),(t+12,lambda label=str(roll):request(label)),(t+15,lambda label=str(roll):recovered(label)),(t+17,lambda label=str(roll),revision=i+1:repeated(label,revision))])
events.extend([(11,lambda:photo('overturned-prompt')),(16,lambda:photo('recovered'))])
events.extend([(60,lambda:fixture(25)),(64,press),(65,lambda:check('minor_lean_rejected',r.get_editor_property('RecoveryRevision')==3 and not r.get_editor_property('bConfirmedOverturned'))),(66,lambda:fixture(90)),(78,force_motion),(79,press),(82,lambda:check('moving_recovery_rejected',r.get_editor_property('RecoveryRevision')==3)),(84,block),(85,press),(86,lambda:check('obstructed_elevated_destination_rejected',r.get_editor_property('RecoveryRevision')==3,pc.get_editor_property('RecoveryFeedback'))),(87,unblock),(88,debug_recover),(91,lambda:check('development_command_safe_recovery',v.get_actor_up_vector().z>.98 and r.get_editor_property('RecoveryRevision')==4)),(93,debug_recover),(94,lambda:check('development_command_upright_rejected',r.get_editor_property('RecoveryRevision')==4)),(95,finish)])
events.sort(key=lambda e:e[0])
def tick(dt):
 global held
 try:
  if held and time.time()>held:unreal.RVInteriorMotorhome.dispatch_development_key(pc,'F8',False);held=None
  if time.time()<force_until:mesh.set_physics_linear_velocity(unreal.Vector(120,0,0),False)
  samples.append(state())
  if events and time.time()-start>=events[0][0]:
   _,fn=events.pop(0);fn()
 except Exception as e:check('harness_exception',False,repr(e));finish()
h=unreal.register_slate_post_tick_callback(tick)

