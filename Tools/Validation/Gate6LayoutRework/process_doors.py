"""Repeated real-E door visuals/collision, parked and moving, in both processes."""
from pathlib import Path
prefix=Path('D:/GitHub/RVSurvival/RVSurvival/Tools/Validation/Gate6LayoutRework/process_auxiliary.py').read_text(encoding='utf-8-sig').split('at(0,setup);')[0]
exec(compile(prefix,'auxiliary-fixture-prefix','exec'))
def key(k,on):unreal.RVInteriorMotorhome.dispatch_development_key(pc,k,on)
def art_lookup():
 parts=[v.find_visual_part(d.name) for d in v.get_editor_property('VisualParts')]
 check('all_54_registered_parts_unique',len(parts)==54 and all(parts) and len({p.get_path_name() for p in parts if p})==54)
at(0,setup);at(1,lambda:aim(de if isdriver else pe));at(1.2,lambda:key('E',True));at(2.1,lambda:key('E',False))
at(3.5,art_lookup);tap(4,'Three','walker')
def closed_push():
 if not isdriver:pc.set_control_rotation(unreal.Rotator(yaw=v.get_actor_rotation().yaw+90));key('W',True)
at(5,closed_push);at(5.7,lambda:key('W',False) if not isdriver else None)
at(6,lambda:check('closed_door_blocks_normal_W',not door.get_editor_property('bOpen') and local(wp)[1]<105,local(wp)))
at(6.1,lambda:key('S',True) if not isdriver else None);at(6.75,lambda:key('S',False) if not isdriver else None)
def state_check(expected,label):
 check(label+'_replicated_state',door.get_editor_property('bOpen')==expected)
 for prop in ['DoorMesh','GlassMesh']:
  mesh=door.get_editor_property(prop)
  original=[c for c in v.get_components_by_class(unreal.StaticMeshComponent) if c.get_editor_property('StaticMesh')==mesh]
  live=[c for c in door.get_components_by_class(unreal.StaticMeshComponent) if c.get_editor_property('StaticMesh')==mesh and c.is_visible() and not c.get_editor_property('bHiddenInGame')]
  check(label+'_one_visible_'+prop,len(live)==1 and bool(original) and all(c.get_editor_property('bHiddenInGame') for c in original),{'original_hidden':len(original),'live_visible':len(live)})
 collision=door.get_editor_property('DoorCollision')
 # Enumerate public owned components; private UPROPERTY access is protected.
 visual=next(c for c in door.get_components_by_class(unreal.StaticMeshComponent) if c.get_editor_property('StaticMesh')==door.get_editor_property('DoorMesh'))
 check(label+'_collision_matches_visual',abs(unreal.MathLibrary.normalized_delta_rotator(collision.get_world_rotation(),visual.get_world_rotation()).yaw)<.1 and collision.get_collision_response_to_channel(unreal.CollisionChannel.ECC_PAWN)==unreal.CollisionResponseType.ECR_BLOCK)
 check(label+'_walker_retains_native_frame',walking(wp) and wp.get_component_by_class(unreal.RVPassengerReferenceFrameComponent).get_editor_property('ReferenceFrame')==v,local(wp))
for n,t in enumerate([7.5,11,14.5,18,23,26.5,30,33.5]):
 at(t,lambda:aim(door) if not isdriver else None)
 at(t+.2,lambda:key('E',True) if not isdriver else None);at(t+1.1,lambda:key('E',False) if not isdriver else None)
 at(t+2,lambda n=n:state_check(n%2==0,('parked' if n<4 else 'moving')+'_'+str(n)))
 if n in [0,1,4,5]:
  at(t+2.2,lambda n=n:cmd('shot filename='+str(B/(config['name']+'_'+str(n)+'.png')).replace('\\','/')+' -nosuffix') if not isdriver else None)
at(21,lambda:key('W',True) if isdriver else None)
at(24.5,lambda:check('real_moving_door_test',v.get_velocity().length()>150,v.get_velocity().length()))
def finish():
 global active
 for k in ['E','W','S','Three']:key(k,False)
 role='server' if authority else 'client'
 (B/(config['name']+'_'+role+'.json')).write_text(json.dumps({'pid':os.getpid(),'role':role,'config':config,'results':results},indent=2),encoding='utf-8')
 active=False;unreal.unregister_slate_post_tick_callback(h)
 from runner_runtime import release_runners
 release_runners()
at(37,finish);events.sort(key=lambda e:e[0])
def tick(dt):
 global idx,input_frame,dp,wp
 if not active:return
 input_frame+=1
 if not authority:
  remote=next((c for c in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSurvivorCharacter) if c!=p),None)
  if remote:dp=p if isdriver else remote;wp=remote if isdriver else p
 t=time.time()-start
 if t<0:return
 try:
  for k,(deadline,frame) in list(pulses.items()):
   if time.time()>=deadline and input_frame>=frame:key(k,False);del pulses[k]
  while idx<len(events) and t>=events[idx][0] and not pulses:
   fn=events[idx][1];idx+=1;terminating=fn.__name__=='finish';fn()
   if terminating:return
 except Exception as e:check('exception',False,repr(e));finish()
h=unreal.register_slate_post_tick_callback(tick)
