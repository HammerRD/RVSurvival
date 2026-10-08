"""Project-side Gate 9 assets; scoped references and explicit saves, no vendor writes."""
import unreal,json,gc,traceback
from pathlib import Path
root=Path('D:/GitHub/RVSurvival/RVSurvival');out=root/'Docs/Gate9Results';folder='/Game/Combat';char='/Game/Characters/RV/Gate9'

def build():
 levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);target='/Game/Maps/Gate9CombatInfectedTest'
 if not unreal.EditorAssetLibrary.does_asset_exist(target):
  assert levels.load_level('/Game/Maps/Gate8_5CharacterTest')
  assert unreal.EditorLoadingAndSavingUtils.save_map(unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world(),target)
 else:assert levels.load_level(target)
 actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);tools=unreal.AssetToolsHelpers.get_asset_tools();cube=unreal.load_asset('/Engine/BasicShapes/Cube')
 def gun_mesh():
  existing=unreal.load_asset(folder+'/SM_SM_Prototype9mm')
  if existing:return existing
  parts=[]
  for name,pos,scale in [('Slide',(4,0,3),(.22,.028,.04)),('Frame',(3,0,0),(.18,.026,.025)),('Grip',(-4,0,-5),(.045,.025,.09)),('TriggerGuard',(0,0,-2),(.04,.012,.04))]:
   a=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*pos));a.set_actor_label('TemporaryHandgun_'+name)
   a.static_mesh_component.set_static_mesh(cube);a.set_actor_scale3d(unreal.Vector(*scale));parts.append(a)
  opt=unreal.MergeStaticMeshActorsOptions();opt.set_editor_property('BasePackageName',folder+'/SM_Prototype9mm');opt.set_editor_property('destroy_source_actors',True);opt.set_editor_property('spawn_merged_actor',True)
  merged=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem).merge_static_mesh_actors(parts,opt);assert merged
  result=merged.static_mesh_component.get_editor_property('StaticMesh');assert result
  actors.destroy_actor(merged);assert unreal.EditorAssetLibrary.save_loaded_asset(result,False);return result
 gun=gun_mesh()
 collision=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
 if collision.get_simple_collision_count(gun)==0:assert collision.add_simple_collisions(gun,unreal.ScriptingCollisionShapeType.BOX)>=0
 assert unreal.EditorAssetLibrary.save_loaded_asset(gun,False)
 task=unreal.AssetImportTask();task.set_editor_property('Filename',str(root/'Saved/Gate9Validation/Prototype9mm.wav'));task.set_editor_property('DestinationPath',folder+'/Audio');task.set_editor_property('Automated',True);task.set_editor_property('Save',True)
 if not unreal.EditorAssetLibrary.does_asset_exist(folder+'/Audio/Prototype9mm'):tools.import_asset_tasks([task])
 sound=unreal.load_asset(folder+'/Audio/Prototype9mm');assert sound
 effect=unreal.load_asset(folder+'/M_PrototypeShot')
 if not effect:
  effect=tools.create_asset('M_PrototypeShot',folder,unreal.Material,unreal.MaterialFactoryNew());effect.set_editor_property('ShadingModel',unreal.MaterialShadingModel.MSM_UNLIT)
  color=unreal.MaterialEditingLibrary.create_material_expression(effect,unreal.MaterialExpressionConstant3Vector);color.set_editor_property('Constant',unreal.LinearColor(8,3,.3,1));unreal.MaterialEditingLibrary.connect_material_property(color,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR);unreal.MaterialEditingLibrary.recompile_material(effect);assert unreal.EditorAssetLibrary.save_loaded_asset(effect,False)
 mesh=unreal.load_asset('/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple');skeleton=mesh.get_editor_property('Skeleton')
 reload=unreal.load_asset(folder+'/AM_PrototypeReload')
 if not reload:
  factory=unreal.AnimMontageFactory();factory.set_editor_property('TargetSkeleton',skeleton);factory.set_editor_property('SourceAnimation',unreal.load_asset('/Game/Characters/Mannequins/Anims/Pistol/MM_Pistol_Reload'))
  reload=tools.create_asset('AM_PrototypeReload',folder,unreal.AnimMontage,factory);assert reload;assert unreal.EditorAssetLibrary.save_loaded_asset(reload,False)
 fire=unreal.load_asset(folder+'/AM_PrototypeFire') or unreal.EditorAssetLibrary.duplicate_asset('/Game/Characters/Mannequins/Anims/Pistol/MM_Pistol_Fire_Montage',folder+'/AM_PrototypeFire');assert fire
 fire.modify();tracks=list(fire.get_editor_property('SlotAnimTracks'))
 for track in tracks:track.set_editor_property('SlotName','DefaultSlot')
 fire.set_editor_property('SlotAnimTracks',tracks);assert unreal.EditorAssetLibrary.save_loaded_asset(fire,False)
 def definition(name,mag=False):
  path=folder+'/Items/'+name;d=unreal.load_asset(path)
  if not d:
   factory=unreal.DataAssetFactory();factory.set_editor_property('DataAssetClass',unreal.RVItemDefinition);d=tools.create_asset(name,folder+'/Items',unreal.RVItemDefinition,factory)
  d.modify();d.set_editor_property('CatalogId',name);d.set_editor_property('DisplayName','9mm magazine' if mag else 'Prototype 9mm handgun');d.set_editor_property('bEquippable',not mag);d.set_editor_property('bSupportsCondition',True)
  d.set_editor_property('WeightKg',.25 if mag else .8);d.set_editor_property('VolumeLitres',.15 if mag else .65);d.set_editor_property('WorldMesh',cube if mag else gun);d.set_editor_property('WorldVisualScale',unreal.Vector(.05,.025,.15) if mag else unreal.Vector(1,1,1))
  c=d.get_editor_property('Combat');c.set_editor_property('bFirearm',not mag);c.set_editor_property('bMagazine',mag);c.set_editor_property('Caliber',unreal.RVItemDefinition.find_registered_tag('Item.Ammo.9mm'))
  c.set_editor_property('ShotSound',sound);c.set_editor_property('ShotEffectMaterial',effect);c.set_editor_property('FireMontage',fire);c.set_editor_property('ReloadMontage',reload);d.set_editor_property('Combat',c)
  assert unreal.EditorAssetLibrary.save_loaded_asset(d,False);return d
 pistol=definition('DA_9mmHandgun');magazine=definition('DA_9mmMagazine',True)
 bp=unreal.load_asset(char+'/ABP_Gate9Humanoid') or unreal.EditorAssetLibrary.duplicate_asset('/Game/Characters/RV/Animations/ABP_RVHumanoid',char+'/ABP_Gate9Humanoid')
 factory=unreal.BlendSpaceFactoryNew();factory.set_editor_property('TargetSkeleton',skeleton)
 armed=unreal.load_asset(char+'/BS_PistolLocomotion') or tools.create_asset('BS_PistolLocomotion',char,unreal.BlendSpace,factory)
 clips=[];coords=[]
 for speed,gait in [(0,None),(180,'Walk'),(600,'Jog')]:
  for angle,direction in [(-180,'Bwd'),(-135,'Bwd_Left'),(-90,'Left'),(-45,'Fwd_Left'),(0,'Fwd'),(45,'Fwd_Right'),(90,'Right'),(135,'Bwd_Right'),(180,'Bwd')]:
   clips.append(unreal.load_asset('/Game/Characters/Mannequins/Anims/Pistol/'+('MF_Pistol_Idle_ADS' if gait is None else gait+'/MF_Pistol_'+gait+'_'+direction)));coords.append(unreal.Vector(speed,angle,0))
 assert unreal.RVCharacterContentLibrary.populate_locomotion(armed,clips,coords);assert unreal.EditorAssetLibrary.save_loaded_asset(armed,False)
 poses=[unreal.load_asset('/Game/Characters/RV/Animations/A_Prototype'+n) for n in ['Driver','Passenger','Bed','Downed','Ladder','Treatment']]+[unreal.load_asset('/Game/Characters/Mannequins/Anims/Unarmed/Jump/'+n) for n in ['MM_Fall_Loop','MM_Jump','MM_Land']]+[unreal.load_asset('/Game/Characters/RV/Animations/A_PrototypeDownedSeated')]
 assert unreal.RVCharacterContentLibrary.build_animation_graph(bp,unreal.load_asset('/Game/Characters/RV/Animations/BS_RVLocomotion'),poses,armed);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,False)
 profile=unreal.load_asset(char+'/DA_CombatPresentation') or unreal.EditorAssetLibrary.duplicate_asset('/Game/Characters/RV/DA_MannyPresentation',char+'/DA_CombatPresentation');profile.modify();profile.set_editor_property('AnimationClass',unreal.EditorAssetLibrary.load_blueprint_class(char+'/ABP_Gate9Humanoid'));assert unreal.EditorAssetLibrary.save_loaded_asset(profile,False)
 pawn=unreal.load_asset(char+'/BP_Gate9Survivor') or unreal.EditorAssetLibrary.duplicate_asset('/Game/Characters/RV/BP_RVHumanoid',char+'/BP_Gate9Survivor');unreal.BlueprintEditorLibrary.compile_blueprint(pawn)
 pawn.modify();cdo=unreal.get_default_object(unreal.EditorAssetLibrary.load_blueprint_class(char+'/BP_Gate9Survivor'));cdo.modify()
 v=cdo.get_editor_property('CharacterPresentation');v.modify();v.set_editor_property('Profile',profile);combat=cdo.get_editor_property('Combat');combat.modify();combat.set_editor_property('bEnabled',True);assert unreal.EditorAssetLibrary.save_loaded_asset(pawn,False)
 gm=unreal.load_asset(folder+'/BP_Gate9GameMode') or unreal.EditorAssetLibrary.duplicate_asset('/Game/Characters/RV/BP_Gate8_5GameMode',folder+'/BP_Gate9GameMode');unreal.BlueprintEditorLibrary.compile_blueprint(gm);gm.modify();cdo=unreal.get_default_object(unreal.EditorAssetLibrary.load_blueprint_class(folder+'/BP_Gate9GameMode'));cdo.modify();cdo.set_editor_property('DefaultPawnClass',unreal.EditorAssetLibrary.load_blueprint_class(char+'/BP_Gate9Survivor'));assert unreal.EditorAssetLibrary.save_loaded_asset(gm,False)
 factory=unreal.DataAssetFactory();factory.set_editor_property('DataAssetClass',unreal.RVInfectedProfile)
 infected_profile=unreal.load_asset(folder+'/DA_PrototypeInfected') or tools.create_asset('DA_PrototypeInfected',folder,unreal.RVInfectedProfile,factory);infected_profile.modify();infected_profile.set_editor_property('Body',mesh);infected_profile.set_editor_property('AnimationClass',unreal.EditorAssetLibrary.load_blueprint_class('/Game/Characters/RV/Animations/ABP_RVHumanoid'));infected_profile.set_editor_property('BodyMapping',profile);assert unreal.EditorAssetLibrary.save_loaded_asset(infected_profile,False)
 # Work only in the new map. Re-running is idempotent by labels.
 world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();ws=world.get_world_settings();ws.modify();ws.set_editor_property('DefaultGameMode',unreal.EditorAssetLibrary.load_blueprint_class(folder+'/BP_Gate9GameMode'))
 existing={a.get_actor_label():a for a in actors.get_all_level_actors()}
 for i in range(2):
  label='Gate9_Handgun_'+str(i);a=existing.get(label) or actors.spawn_actor_from_class(unreal.RVWorldItem,unreal.Vector(-200+i*80,300,25));a.set_actor_label(label);a.modify();item=unreal.RVItemInstance();item.set_editor_property('Id',unreal.GuidLibrary.new_guid());item.set_editor_property('Definition',pistol);a.set_editor_property('Item',item);a.get_component_by_class(unreal.StaticMeshComponent).set_static_mesh(gun);a.set_actor_scale3d(unreal.Vector(1,1,1))
 for i in range(8):
  label='Gate9_Magazine_'+str(i);a=existing.get(label) or actors.spawn_actor_from_class(unreal.RVWorldItem,unreal.Vector(-240+i*45,380,25));a.set_actor_label(label);a.modify();item=unreal.RVItemInstance();item.set_editor_property('Id',unreal.GuidLibrary.new_guid());item.set_editor_property('Definition',magazine);item.set_editor_property('bMagazineInitialized',True);item.set_editor_property('MagazineRounds',15 if i<6 else 6 if i==6 else 0);a.set_editor_property('Item',item)
 for i in range(3):
  label='Gate9_Infected_'+str(i);a=existing.get(label) or actors.spawn_actor_from_class(unreal.RVInfected,unreal.Vector(3000+i*650,3000,90),unreal.Rotator(yaw=180));a.set_actor_label(label);a.modify();a.set_editor_property('Profile',infected_profile)
 nav=existing.get('Gate9_Navigation') or actors.spawn_actor_from_class(unreal.NavMeshBoundsVolume,unreal.Vector(0,0,300));nav.set_actor_label('Gate9_Navigation');nav.modify();nav.set_actor_scale3d(unreal.Vector(100,100,8))
 for i,(pos,scale) in enumerate([((1500,2500,100),(.25,12,2)),((2300,3500,100),(8,.25,2))]):
  label='Gate9_Cover_'+str(i);a=existing.get(label) or actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*pos));a.set_actor_label(label);a.static_mesh_component.set_static_mesh(cube);a.set_actor_scale3d(unreal.Vector(*scale))
 assert unreal.EditorLoadingAndSavingUtils.save_map(world,target)
 return {'map':target,'actors':len(actors.get_all_level_actors()),'gun_mesh':gun.get_path_name(),'fire_slot_tracks':str(fire.get_editor_property('SlotAnimTracks')),'nav_bounds':str(nav.get_actor_bounds(False)),'player_starts':[{ 'name':a.get_actor_label(),'position':str(a.get_actor_location())} for a in actors.get_all_level_actors() if isinstance(a,unreal.PlayerStart)],'saved':True}
try:
 result=build();(out/'saved-foundation.json').write_text(json.dumps(result,indent=2))
except Exception:
 (out/'content-error.txt').write_text(traceback.format_exc());traceback.print_exc()
finally:
 gc.collect();unreal.SystemLibrary.quit_editor()
