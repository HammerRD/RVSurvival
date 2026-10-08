"""Hardware-input visual staging. No equip/fire/reload RPC or input shortcuts."""
import unreal,json,time
from pathlib import Path
root=Path('D:/GitHub/RVSurvival/RVSurvival');out=root/'Docs/Gate9Results';B=root/'Saved/Gate9Validation';(out/'Visuals').mkdir(exist_ok=True)
w=next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='Gate9CombatInfectedTest' and unreal.GameplayStatics.get_player_controller(w,0) and unreal.GameplayStatics.get_player_controller(w,0).get_controlled_pawn())
pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn();inv=p.get_component_by_class(unreal.RVInventoryComponent);combat=p.get_component_by_class(unreal.RVCombatComponent)
p.set_actor_location(unreal.Vector(-200,-2500,90),False,True);pc.set_control_rotation(unreal.Rotator())
for name in ['DA_9mmHandgun','DA_9mmMagazine','DA_9mmMagazine']:
 item=unreal.RVItemInstance();item.set_editor_property('Id',unreal.GuidLibrary.new_guid());item.set_editor_property('Definition',unreal.load_asset('/Game/Combat/Items/'+name));assert not inv.add_authority(item)
enemy=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVInfected)[0];enemy.get_controller().get_editor_property('BrainComponent').stop_logic('stationary visual fixture');enemy.get_controller().stop_movement();enemy.set_actor_location(unreal.Vector(900,-2500,90),False,True);enemy.set_actor_rotation(unreal.Rotator(yaw=180),False)
seen=set();started=time.time();camera=None
(B/'visual-ready.json').write_text(json.dumps({'ready':True,'time':started,'manual_inputs':'4 equip, R reload, mouse fire/aim'}))
def cmd(c):unreal.SystemLibrary.execute_console_command(pc,c,pc)
def snap(name):cmd('shot showui filename='+str(out/'Visuals'/('manual_'+name+'.png')).replace('\\','/')+' -nosuffix')
def tick(dt):
 global camera
 if unreal.GuidLibrary.is_valid_guid(combat.equipped_weapon) and 'equipped' not in seen:seen.add('equipped');snap('equipped')
 if combat.reload_ends>0 and 'reload' not in seen:seen.add('reload');snap('reload')
 if combat.get_loaded_rounds()==15 and 'ready' not in seen:seen.add('ready');snap('loaded_ready')
 if combat.get_editor_property('bAiming') and 'aim' not in seen:seen.add('aim');snap('aim')
 if combat.shot_sequence>0 and 'fire' not in seen:seen.add('fire');snap('fire')
 command=B/'visual-command.json'
 if command.exists():
  data=json.loads(command.read_text());name=data['name']
  if name not in seen:
   seen.add(name)
   if name=='observer':
    pos=p.get_actor_location()+unreal.Vector(170,-190,30);camera=unreal.RVCharacterContentLibrary.spawn_observation_camera(p,pos,unreal.MathLibrary.find_look_at_rotation(pos,p.get_actor_location()+unreal.Vector(35,0,25)));pc.set_view_target_with_blend(camera,0)
   elif name=='restore':pc.set_view_target_with_blend(p,0)
   elif name=='aim_hold':unreal.RVInteriorMotorhome.dispatch_development_key(pc,'RightMouseButton',True)
   elif name=='aim_release':unreal.RVInteriorMotorhome.dispatch_development_key(pc,'RightMouseButton',False)
   elif name=='snapshot':snap('observer_handgun')
 (out/'manual-visual-state.json').write_text(json.dumps({'seen':sorted(seen),'shot_sequence':combat.shot_sequence,'rounds':combat.get_loaded_rounds(),'enemy_state':str(enemy.state),'enemy_vitality':enemy.vitality,'camera':str(pc.get_view_target())},indent=2))
 if (B/'visual-stop.json').exists() or time.time()-started>300:
  unreal.RVInteriorMotorhome.dispatch_development_key(pc,'RightMouseButton',False);unreal.unregister_slate_post_tick_callback(handle)
  (out/'manual-visual-done.json').write_text(json.dumps({'seen':sorted(seen),'time':time.time()}))
handle=unreal.register_slate_post_tick_callback(tick)

