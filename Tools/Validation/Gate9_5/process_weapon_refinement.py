"""Only changed weapon/input/presentation states, separate-process normal input."""
import unreal,json,time,os
from pathlib import Path
B=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate9_5Validation');session=json.loads((B/'session.json').read_text());config=session['config'];start=session['start']
w=next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='Gate9_5CombatRefinementTest' and unreal.GameplayStatics.get_player_controller(w,0) and unreal.GameplayStatics.get_player_controller(w,0).get_controlled_pawn())
pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn();authority=unreal.GameplayStatics.get_game_mode(w) is not None;role='server' if authority else 'client';other=next(c for c in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSurvivorCharacter) if c!=p)
hp=p if authority else other;cp=other if authority else p;enemies=sorted(unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVInfected),key=lambda a:a.get_name());rows=[];events=[];held={};initial=None;ammo_ids=None;before=[];camera=None;active=True
def combat(c):return c.get_component_by_class(unreal.RVCombatComponent)
def inventory(c):return c.get_component_by_class(unreal.RVInventoryComponent)
def check(name,value,detail=''):rows.append({'case':name,'pass':bool(value),'detail':str(detail)})
def at(t,fn):events.append((t,fn))
def key(k,on):unreal.RVInteriorMotorhome.dispatch_development_key(pc,k,on)
def tap(k):key(k,True);held[k]=time.time()+.1
def setup():
 unreal.SystemLibrary.execute_console_command(pc,'t.MaxFPS 60',pc)
 if config.get('network'):
  for name,value in [('PktLagMin',100),('PktLagMax',100),('PktLoss',2)]:unreal.SystemLibrary.execute_console_command(pc,'NetEmulation.'+name+' '+str(value),pc)
 p.set_actor_location(unreal.Vector(0,-2500 if authority else -2900,90),False,True);pc.set_control_rotation(unreal.Rotator())
 if authority:
  cp.set_actor_location(unreal.Vector(0,-2900,90),False,True)
  for c in [hp,cp]:
   for name in ['DA_M1911_45ACP','DA_45ACPMagazine','DA_PrototypeCrowbar']:
    item=unreal.RVItemInstance();item.set_editor_property('Id',unreal.GuidLibrary.new_guid());item.set_editor_property('Definition',unreal.load_asset('/Game/Combat/Gate9_5/Items/'+name));assert not inventory(c).add_authority(item)
  for e in enemies:
   e.get_controller().get_editor_property('BrainComponent').stop_logic('weapon fixture');e.get_controller().stop_movement();e.set_actor_location(unreal.Vector(8000,4000,90),False,True)
def record_ammo():
 global ammo_ids
 ammo_ids=[[i.id for i in inventory(c).get_items() if unreal.GuidLibrary.is_valid_guid(i.loaded_in_weapon)] for c in [hp,cp]]
 check('both_primary_fire_one_round',all(combat(c).shot_sequence==1 and combat(c).get_loaded_rounds()==6 for c in [hp,cp]))
def check_ammo():
 current=[[i.id for i in inventory(c).get_items() if unreal.GuidLibrary.is_valid_guid(i.loaded_in_weapon)] for c in [hp,cp]]
 check('both_partial_magazine_identity_preserved',all(combat(c).get_loaded_rounds()==6 for c in [hp,cp]) and all(len(a)==len(b) and all(unreal.GuidLibrary.equal_equal_guid_guid(x,y) for x,y in zip(a,b)) for a,b in zip(ammo_ids,current)))
def position_targets():
 if authority:
  for e,c in zip(enemies[:2],[hp,cp]):e.set_actor_location(c.get_actor_location()+unreal.Vector(125,0,0),False,True)
def aim_target():
 e=enemies[0 if authority else 1];mapping=e.get_editor_property('Profile').get_editor_property('BodyMapping');bone=next(b.anchor_bone for b in mapping.body_regions if b.region==unreal.RVBodyRegion.TORSO)
 pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p.get_actor_eyes_view_point()[0],e.mesh.get_socket_location(bone)))
def melee_start():
 global before
 before=[e.vitality for e in enemies[:2]]
def melee_end():
 check('both_contextual_three_swings',all(combat(c).melee_sequence==3 for c in [hp,cp]),[combat(c).melee_sequence for c in [hp,cp]])
 check('authoritative_damage_replicates',all(e.vitality<value for e,value in zip(enemies[:2],before)),[(e.vitality,value) for e,value in zip(enemies[:2],before)])
def snapshot(name):
 if not camera:return
 unreal.SystemLibrary.execute_console_command(pc,'shot showui filename='+str(B/(config['name']+'_'+role+'_'+name+'.png')).replace('\\','/')+' -nosuffix',pc)
def observe():
 global camera
 target=other.mesh.get_socket_location('pelvis')+unreal.Vector(0,0,30);location=target+unreal.Vector(160,70,10)
 if camera is None:camera=unreal.RVCharacterContentLibrary.spawn_observation_camera(p,location,unreal.MathLibrary.find_look_at_rotation(location,target))
 pc.set_view_target_with_blend(camera,0)
def restore():pc.set_view_target_with_blend(pc.get_controlled_pawn(),0)
def check_variant(number):
 a=other.mesh.get_anim_instance().get_current_active_montage();check('remote_variant_'+str(number),a is not None and a.get_name()=='AM_Crowbar'+['Diagonal','Horizontal','Downward'][number],str(a.get_name()) if a else 'no montage')
def camera_check():check('switch_restores_camera',abs(p.get_component_by_class(unreal.CameraComponent).field_of_view-90)<.1)
def finish():
 global active
 active=False
 for k in held:key(k,False)
 unreal.unregister_slate_post_tick_callback(handle);(B/(config['name']+'_'+role+'.json')).write_text(json.dumps({'role':role,'network':config.get('network'),'results':rows,'scope':'changed combat/input/animation only'},indent=2));events.clear()
at(0,setup);at(1,lambda:tap('Four'));at(1.6,lambda:tap('R'));at(4.5,lambda:tap('LeftMouseButton'));at(5.5,record_ammo)
at(6,lambda:key('RightMouseButton',True));at(6.2,lambda:pc.set_control_rotation(unreal.Rotator(pitch=30)));at(7.5,observe);at(7.8,lambda:snapshot('remote_handgun_ads'));at(8.1,restore)
at(8.2,lambda:tap('MouseScrollUp'));at(9,lambda:key('RightMouseButton',False));at(9.5,camera_check);at(9.6,position_targets);at(10.5,aim_target);at(10.8,melee_start)
for i in range(3):
 t=11+i*1.5;at(t,lambda:tap('LeftMouseButton'));at(t+.35,lambda i=i:check_variant(i));at(t+.3,observe);at(t+.45,lambda i=i:snapshot('remote_crowbar_'+str(i)));at(t+.7,restore)
at(16,melee_end);at(16.2,lambda:tap('MouseScrollDown'));at(17,check_ammo)
for i in range(12):at(18+i*.15,lambda:tap('MouseScrollUp'))
at(21,check_ammo);at(21.1,lambda:check('one_equipment_visual',len([v for v in unreal.ObjectIterator(unreal.StaticMeshComponent) if v.get_owner()==p and v.get_name()=='EquippedFirearmVisual' and v.is_visible()])==1))
at(22,lambda:tap('Four'));at(22.5,lambda:tap('LeftMouseButton'));at(23.5,lambda:check('both_primary_unarmed_shove',all(combat(c).melee_sequence==4 for c in [hp,cp])));at(24,finish);events.sort(key=lambda x:x[0])
def tick(dt):
 if not active:return
 try:
  for k,due in list(held.items()):
   if time.time()>=due:key(k,False);del held[k]
  while events and time.time()-start>=events[0][0]:_,fn=events.pop(0);fn()
 except Exception as err:check('harness_exception',False,repr(err));events.clear();finish()
handle=unreal.register_slate_post_tick_callback(tick)
