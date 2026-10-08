"""Rendered pose atlas and owner-view diagnostic, not gameplay/net acceptance."""
import unreal,time,json,os
from pathlib import Path
B=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate8_5Validation');start=time.time()
w=next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='Gate8_5CharacterTest' and unreal.GameplayStatics.get_player_controller(w,0) and unreal.GameplayStatics.get_player_controller(w,0).get_controlled_pawn())
pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn();mesh=p.get_editor_property('Mesh');visual=p.get_component_by_class(unreal.RVCharacterPresentationComponent)
rows=[];actors=[];events=[];held={}
def check(n,b,d=''):rows.append({'case':n,'pass':bool(b),'detail':str(d)})
def cmd(s):unreal.SystemLibrary.execute_console_command(pc,s,pc)
def shot(n):cmd('shot showui filename='+str(B/(n+'.png')).replace('\\','/')+' -nosuffix')
def setup():
 cmd('t.MaxFPS 60');cmd('t.IdleWhenNotForeground 0')
 check('configured_runtime_skeletal_mesh',visual.has_configured_visuals() and mesh.skeletal_mesh.get_name()=='SKM_Manny_Simple',mesh.get_name())
 check('native_animation_instance',isinstance(mesh.get_anim_instance(),unreal.RVHumanoidAnimInstance))
 for name,bone,region in [('head','head',unreal.RVBodyRegion.HEAD),('torso','spine_03',unreal.RVBodyRegion.TORSO),('left_arm','hand_l',unreal.RVBodyRegion.LEFT_ARM),('right_arm','hand_r',unreal.RVBodyRegion.RIGHT_ARM),('left_leg','foot_l',unreal.RVBodyRegion.LEFT_LEG),('right_leg','foot_r',unreal.RVBodyRegion.RIGHT_LEG)]:
  found=visual.resolve_body_region(bone);check('body_region_'+name,found==region,str(found))
 check('seven_future_attachment_anchors',all(visual.get_equipment_anchor(n) is not None for n in ['Backpack','LongGun','HandgunHolster','Tool','CarriedItem','Flashlight','MedicalBag']))
 p.set_actor_location(unreal.Vector(1800,-800,95),False,True);pc.set_control_rotation(unreal.Rotator())
 body=unreal.load_asset('/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple')
 for i,name in enumerate(['Idle','Driver','Passenger','Bed','Downed','Ladder','Treatment','DownedSeated']):
  actor=unreal.RVCharacterContentLibrary.spawn_pose_fixture(p,unreal.Vector(2050,-800+i*200,0))
  component=actor.get_component_by_class(unreal.SkeletalMeshComponent);component.set_skeletal_mesh(body);component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION);component.set_relative_rotation(unreal.Rotator(yaw=90),False,False)
  clip=unreal.load_asset('/Game/Characters/Mannequins/Anims/Unarmed/MM_Idle' if name=='Idle' else '/Game/Characters/RV/Animations/A_Prototype'+name)
  component.play_animation(clip,True);actors.append((name,actor))
def observe(i):
 name,actor=actors[i];p.set_actor_location(actor.get_actor_location()+unreal.Vector(-250,0,95),False,True)
 target=actor.get_actor_location()+unreal.Vector(0,0,75 if name not in ['Bed','Downed'] else 5)
 pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p.get_actor_location()+unreal.Vector(0,0,64),target))
def owner():pc.set_control_rotation(unreal.Rotator(pitch=-75))
def walk():unreal.RVInteriorMotorhome.dispatch_development_key(pc,'W',True)
def stopwalk():unreal.RVInteriorMotorhome.dispatch_development_key(pc,'W',False)
def finish():
 stopwalk();unreal.unregister_slate_post_tick_callback(handle)
 (B/'visual-development.json').write_text(json.dumps({'pid':os.getpid(),'results':rows,'evidence_kind':'native PIE owner view and transient pose atlas; no gameplay pose acceptance'},indent=2))
events=[(0,setup),(2,owner),(3,lambda:shot('owner-look-down')),(4,walk),(5,lambda:shot('owner-walking')),(5.5,stopwalk)]
for i in range(8):events.extend([(7+i*3,lambda i=i:observe(i)),(8.5+i*3,lambda i=i:shot('atlas-'+actors[i][0]))])
events.append((33,finish))
def tick(dt):
 try:
  if events and time.time()-start>=events[0][0]:_,fn=events.pop(0);fn()
 except Exception as e:check('harness_exception',False,repr(e));events.clear();finish()
handle=unreal.register_slate_post_tick_callback(tick)


