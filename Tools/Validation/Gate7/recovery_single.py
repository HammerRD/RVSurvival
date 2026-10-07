"""Physics-settled rollover fixtures; recovery intent uses the mapped F8 action."""
import unreal,json,time,math
from pathlib import Path
B=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate7Validation')
w=next(a for a in unreal.ObjectIterator(unreal.World) if a.get_name()=='Gate7MechanicalTest' and 'UEDPIE_' in a.get_path_name())
pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn()
v=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVMechanicalMotorhome)[0]
r=v.get_editor_property('Recovery');mesh=v.get_component_by_class(unreal.SkeletalMeshComponent)
results=[];events=[];samples=[];start=time.time();held=None;before=None
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
events.append((60,finish))
def tick(dt):
 global held
 try:
  if held and time.time()>held:unreal.RVInteriorMotorhome.dispatch_development_key(pc,'F8',False);held=None
  samples.append(state())
  if events and time.time()-start>=events[0][0]:
   _,fn=events.pop(0);fn()
 except Exception as e:check('harness_exception',False,repr(e));finish()
h=unreal.register_slate_post_tick_callback(tick)

