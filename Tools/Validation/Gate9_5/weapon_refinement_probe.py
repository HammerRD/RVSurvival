"""Bounded normal Enhanced Input attack/cycle plus rendered pitch-matrix inspection."""
import unreal,json,time,math
from pathlib import Path
r=Path('D:/GitHub/RVSurvival/RVSurvival');out=r/'Saved/Gate9_5Validation';visual=out/'RefinementVisuals';visual.mkdir(exist_ok=True)
w=next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='Gate9_5CombatRefinementTest' and unreal.GameplayStatics.get_player_controller(w,0) and unreal.GameplayStatics.get_player_controller(w,0).get_controlled_pawn())
pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn();combat=p.get_component_by_class(unreal.RVCombatComponent);inv=p.get_component_by_class(unreal.RVInventoryComponent);rows=[];events=[];samples=[];start=time.time();held={};stage='setup';revision=None;loaded_id=None;shot=None;sequence=None
p.set_actor_location(unreal.Vector(-200,-2500,100),False,True);pc.set_control_rotation(unreal.Rotator())
for name in ['DA_M1911_45ACP','DA_45ACPMagazine','DA_PrototypeCrowbar']:
 item=unreal.RVItemInstance();item.set_editor_property('Id',unreal.GuidLibrary.new_guid());item.set_editor_property('Definition',unreal.load_asset('/Game/Combat/Gate9_5/Items/'+name));assert not inv.add_authority(item)
unreal.SystemLibrary.execute_console_command(pc,'t.MaxFPS 60',pc)
def at(t,fn):events.append((t,fn))
def press(key):unreal.RVInteriorMotorhome.dispatch_development_key(pc,key,True);held[key]=time.time()+.08
def hold(key,on):unreal.RVInteriorMotorhome.dispatch_development_key(pc,key,on)
def check(name,value,detail=''):rows.append({'case':name,'pass':bool(value),'detail':str(detail)})
def capture(name):unreal.SystemLibrary.execute_console_command(pc,'shot showui filename='+str(visual/(name+'.png')).replace('\\','/')+' -nosuffix',pc)
def pitch(value,name):
 global stage
 stage=name;pc.set_control_rotation(unreal.Rotator(pitch=value))
def ammo_snapshot():
 global loaded_id,shot
 loaded_id=[i.id for i in inv.get_items() if unreal.GuidLibrary.is_valid_guid(i.loaded_in_weapon)];shot=combat.shot_sequence
 check('primary_fire',combat.get_loaded_rounds()==6 and shot==1,combat.get_loaded_rounds())
def preserved():
 current=[i.id for i in inv.get_items() if unreal.GuidLibrary.is_valid_guid(i.loaded_in_weapon)]
 check('cycle_preserves_partial_magazine',combat.get_loaded_rounds()==6 and len(current)==len(loaded_id) and all(unreal.GuidLibrary.equal_equal_guid_guid(a,b) for a,b in zip(current,loaded_id)),combat.get_loaded_rounds())
 check('single_equipment_visual',len([x for x in unreal.ObjectIterator(unreal.StaticMeshComponent) if x.get_owner()==p and x.get_name()=='EquippedFirearmVisual' and x.is_visible()])==1)
def finish():
 for k in held:hold(k,False)
 hold('RightMouseButton',False);unreal.unregister_slate_post_tick_callback(handle)
 (out/'weapon-refinement-input.json').write_text(json.dumps({'results':rows,'samples':samples,'rendered_pitch_matrix':[-60,-30,0,30,60]},indent=2))
at(.4,lambda:press('Four'));at(.9,lambda:press('R'));at(3.3,lambda:press('LeftMouseButton'));at(3.7,ammo_snapshot)
for index,value in enumerate([-60,-30,0,30,60]):
 t=4+index*1.3;at(t,lambda v=value: pitch(v,'ready_'+str(v)));at(t+.8,lambda v=value:capture('handgun_ready_'+str(v)))
at(11,lambda:hold('RightMouseButton',True))
for index,value in enumerate([-60,-30,0,30,60]):
 t=11.2+index*1.3;at(t,lambda v=value:pitch(v,'ads_'+str(v)));at(t+.8,lambda v=value:capture('handgun_ads_'+str(v)))
at(18,lambda:hold('RightMouseButton',False));at(18.2,lambda:pitch(0,'ready_return'));at(19,capture if False else lambda:capture('handgun_ready_return'))
at(19.5,lambda:press('MouseScrollUp'));at(20.3,lambda:check('wheel_next_melee',any(unreal.GuidLibrary.equal_equal_guid_guid(i.id,combat.equipped_weapon) and i.definition.get_editor_property('Combat').get_editor_property('bMelee') for i in inv.get_items())))
at(20.4,lambda:capture('crowbar_ready'))
for i in range(3):
 t=21+i*1.5;at(t,lambda:press('LeftMouseButton'));at(t+.18,lambda i=i:capture('crowbar_wind_'+str(i)));at(t+.42,lambda i=i:capture('crowbar_strike_'+str(i)))
at(25.7,lambda:check('primary_three_melee_variants',combat.melee_sequence==3,combat.melee_sequence));at(26,lambda:press('MouseScrollDown'));at(26.7,preserved)
for i in range(12):at(27+i*.12,lambda:press('MouseScrollUp'))
at(29,lambda:check('rapid_cycle_returns_firearm',combat.get_loaded_rounds()==6,combat.get_loaded_rounds()))
at(29.5,lambda:press('Four'));at(30,lambda:press('LeftMouseButton'));at(30.7,lambda:check('unarmed_primary_shove',combat.melee_sequence==4,combat.melee_sequence));at(31.2,lambda:check('camera_restored',abs(p.get_component_by_class(unreal.CameraComponent).field_of_view-90)<.1));at(32,finish);events.sort(key=lambda x:x[0])
def tick(dt):
 try:
  now=time.time()
  for k,due in list(held.items()):
   if now>=due:hold(k,False);del held[k]
  while events and now-start>=events[0][0]:_,fn=events.pop(0);fn()
  mesh=p.get_editor_property('Mesh');anim=mesh.get_anim_instance()
  samples.append({'t':round(now-start,2),'stage':stage,'support_error_cm':(mesh.get_socket_transform('hand_r').transform_location(anim.get_editor_property('WeaponLeftHandTarget'))-mesh.get_socket_location('hand_l')).length(),'right_alpha':anim.get_editor_property('WeaponGripIKAlpha'),'left_alpha':anim.get_editor_property('WeaponSupportIKAlpha')})
 except Exception as err:check('harness_exception',False,repr(err));events.clear();finish()
handle=unreal.register_slate_post_tick_callback(tick)
