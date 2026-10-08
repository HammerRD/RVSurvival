"""Saved, project-side visual assets and one new test map; scoped UObject lifetimes."""
import unreal,json,gc
from pathlib import Path
root=Path('D:/GitHub/RVSurvival/RVSurvival');out=root/'Docs/Gate8_5Results'
def assets():
 tools=unreal.AssetToolsHelpers.get_asset_tools();folder='/Game/Characters/RV'
 mesh=unreal.load_asset('/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple');assert mesh
 skeleton=mesh.get_editor_property('Skeleton');idle=unreal.load_asset('/Game/Characters/Mannequins/Anims/Unarmed/MM_Idle')
 def rotations(data):return {k:unreal.Rotator(pitch=v[0],yaw=v[1],roll=v[2]) for k,v in data.items()}
 # Prototype local-bone offsets. Visual inspection, not these values, certifies poses.
 legs={'thigh_l':(-90,0,0),'thigh_r':(-90,0,0),'calf_l':(90,0,0),'calf_r':(90,0,0)}
 passenger=dict(legs,**{'upperarm_l':(0,0,-20),'upperarm_r':(0,0,20),'lowerarm_l':(0,0,-55),'lowerarm_r':(0,0,55)})
 driver=dict(legs,**{'upperarm_l':(0,-55,0),'upperarm_r':(0,55,0),'lowerarm_l':(0,0,-45),'lowerarm_r':(0,0,45)})
 lying={'root':(0,0,-90),'upperarm_l':(0,0,-10),'upperarm_r':(0,0,10)}
 climb={'upperarm_l':(0,-120,0),'upperarm_r':(0,120,0),'lowerarm_l':(0,0,-50),'lowerarm_r':(0,0,50),'thigh_l':(-25,0,0),'thigh_r':(-25,0,0),'calf_l':(35,0,0),'calf_r':(35,0,0)}
 treatment={'spine_02':(0,0,15),'upperarm_l':(0,-55,0),'upperarm_r':(0,55,0),'lowerarm_l':(0,0,-85),'lowerarm_r':(0,0,85)}
 downseat=dict(passenger,**{'spine_02':(0,0,35),'neck_01':(0,0,15)})
 poses={}
 for name,data in [('Driver',driver),('Passenger',passenger),('Bed',lying),('Downed',lying),('Ladder',climb),('Treatment',treatment),('DownedSeated',downseat)]:
  poses[name]=unreal.RVCharacterContentLibrary.create_prototype_pose(folder+'/Animations/A_Prototype'+name,mesh,rotations(data),name=='Ladder',idle);assert poses[name]
  if name in ['Driver','Passenger','DownedSeated']:
   directions={'thigh_l':unreal.Vector(0,1,0),'thigh_r':unreal.Vector(0,1,0),'calf_l':unreal.Vector(0,0,-1),'calf_r':unreal.Vector(0,0,-1)}
   if name=='Driver':directions.update({'upperarm_l':unreal.Vector(0,1,-0.6),'upperarm_r':unreal.Vector(0,1,-0.6),'lowerarm_l':unreal.Vector(0,1,0.7),'lowerarm_r':unreal.Vector(0,1,0.7)})
   else:directions.update({'upperarm_l':unreal.Vector(0,0,-1),'upperarm_r':unreal.Vector(0,0,-1),'lowerarm_l':unreal.Vector(0,1,0.15),'lowerarm_r':unreal.Vector(0,1,0.15)})
   assert unreal.RVCharacterContentLibrary.align_pose_bones(poses[name],mesh,directions)
  assert unreal.EditorAssetLibrary.save_loaded_asset(poses[name],False)
 factory=unreal.BlendSpaceFactoryNew();factory.set_editor_property('TargetSkeleton',skeleton)
 blend=unreal.load_asset(folder+'/Animations/BS_RVLocomotion') or tools.create_asset('BS_RVLocomotion',folder+'/Animations',unreal.BlendSpace,factory)
 clips=[];coords=[]
 directions=[(-180,'Bwd'),(-135,'Bwd_Left'),(-90,'Left'),(-45,'Fwd_Left'),(0,'Fwd'),(45,'Fwd_Right'),(90,'Right'),(135,'Bwd_Right'),(180,'Bwd')]
 for speed,gait in [(0,None),(180,'Walk'),(600,'Jog')]:
  for angle,name in directions:
   clips.append(idle if gait is None else unreal.load_asset('/Game/Characters/Mannequins/Anims/Unarmed/'+gait+'/MF_Unarmed_'+gait+'_'+name));coords.append(unreal.Vector(speed,angle,0))
 assert unreal.RVCharacterContentLibrary.populate_locomotion(blend,clips,coords)
 assert unreal.EditorAssetLibrary.save_loaded_asset(blend)
 factory=unreal.AnimBlueprintFactory();factory.set_editor_property('ParentClass',unreal.RVHumanoidAnimInstance);factory.set_editor_property('TargetSkeleton',skeleton);factory.set_editor_property('PreviewSkeletalMesh',mesh)
 bp=unreal.load_asset(folder+'/Animations/ABP_RVHumanoid') or tools.create_asset('ABP_RVHumanoid',folder+'/Animations',unreal.AnimBlueprint,factory)
 sequences=[poses['Driver'],poses['Passenger'],poses['Bed'],poses['Downed'],poses['Ladder'],poses['Treatment']]+[unreal.load_asset('/Game/Characters/Mannequins/Anims/Unarmed/Jump/'+n) for n in ['MM_Fall_Loop','MM_Jump','MM_Land']]+[poses['DownedSeated']]
 assert unreal.RVCharacterContentLibrary.build_animation_graph(bp,blend,sequences)
 assert unreal.EditorAssetLibrary.save_loaded_asset(bp)
 factory=unreal.DataAssetFactory();factory.set_editor_property('DataAssetClass',unreal.RVCharacterVisualProfile)
 profile=unreal.load_asset(folder+'/DA_MannyPresentation') or tools.create_asset('DA_MannyPresentation',folder,unreal.RVCharacterVisualProfile,factory)
 profile.set_editor_property('OwnerCameraOffset',unreal.Vector(20,0,0));profile.set_editor_property('Body',mesh);profile.set_editor_property('AnimationClass',unreal.EditorAssetLibrary.load_blueprint_class(folder+'/Animations/ABP_RVHumanoid'));profile.set_editor_property('OwnerHiddenHead','head')
 regions=[]
 for region,bone,roots in [('HEAD','head',['neck_01']),('TORSO','spine_03',['pelvis','spine_01','clavicle_l','clavicle_r']),('LEFT_ARM','lowerarm_l',['upperarm_l']),('RIGHT_ARM','lowerarm_r',['upperarm_r']),('LEFT_LEG','calf_l',['thigh_l']),('RIGHT_LEG','calf_r',['thigh_r'])]:
  binding=unreal.RVBodyRegionBones();binding.set_editor_property('Region',getattr(unreal.RVBodyRegion,region));binding.set_editor_property('AnchorBone',bone);binding.set_editor_property('Roots',roots);regions.append(binding)
 profile.set_editor_property('BodyRegions',regions)
 anchors=[]
 for name,bone in [('Backpack','spine_03'),('LongGun','spine_03'),('HandgunHolster','pelvis'),('Tool','hand_r'),('CarriedItem','hand_l'),('Flashlight','hand_r'),('MedicalBag','hand_l')]:
  anchor=unreal.RVEquipmentAnchor();anchor.set_editor_property('Id',name);anchor.set_editor_property('Bone',bone);anchors.append(anchor)
 profile.set_editor_property('EquipmentAnchors',anchors);assert unreal.EditorAssetLibrary.save_loaded_asset(profile)
 factory=unreal.BlueprintFactory();factory.set_editor_property('ParentClass',unreal.RVInteriorTestCharacter)
 character=unreal.load_asset(folder+'/BP_RVHumanoid') or tools.create_asset('BP_RVHumanoid',folder,unreal.Blueprint,factory)
 cls=unreal.EditorAssetLibrary.load_blueprint_class(folder+'/BP_RVHumanoid');cdo=unreal.get_default_object(cls)
 unreal.BlueprintEditorLibrary.compile_blueprint(character)
 character.modify();cdo.modify();component=cdo.get_editor_property('CharacterPresentation');component.modify();component.set_editor_property('Profile',profile)
 body=cdo.get_editor_property('Mesh');body.set_skeletal_mesh(mesh);body.set_anim_instance_class(unreal.EditorAssetLibrary.load_blueprint_class(folder+'/Animations/ABP_RVHumanoid'));body.set_relative_location(unreal.Vector(0,0,-88),False,False);body.set_relative_rotation(unreal.Rotator(yaw=-90),False,False)
 assert unreal.EditorAssetLibrary.save_loaded_asset(character,False)
 gm=unreal.load_asset(folder+'/BP_Gate8_5GameMode') or unreal.EditorAssetLibrary.duplicate_asset('/Game/Medical/BP_Gate8GameMode',folder+'/BP_Gate8_5GameMode')
 gmcls=unreal.EditorAssetLibrary.load_blueprint_class(folder+'/BP_Gate8_5GameMode');unreal.get_default_object(gmcls).set_editor_property('DefaultPawnClass',unreal.EditorAssetLibrary.load_blueprint_class(folder+'/BP_RVHumanoid'))
 unreal.BlueprintEditorLibrary.compile_blueprint(gm);assert unreal.EditorAssetLibrary.save_loaded_asset(gm)
 assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
 return {'mesh':mesh.get_path_name(),'skeleton':skeleton.get_path_name(),'animation_blueprint':bp.get_path_name(),'body_regions':6,'equipment_anchors':7}
def test_map():
 levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);target='/Game/Maps/Gate8_5CharacterTest'
 if not unreal.EditorAssetLibrary.does_asset_exist(target):
  assert levels.load_level('/Game/Maps/Gate8MedicalTest')
  assert unreal.EditorLoadingAndSavingUtils.save_map(unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world(),target)
 else:assert levels.load_level(target)
 world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();world.get_world_settings().modify();world.get_world_settings().set_editor_property('DefaultGameMode',unreal.EditorAssetLibrary.load_blueprint_class('/Game/Characters/RV/BP_Gate8_5GameMode'))
 assert unreal.EditorLoadingAndSavingUtils.save_map(world,target)
 return {'map':target,'actors':len(unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()),'saved':True}
try:
 result=assets();gc.collect();unreal.SystemLibrary.collect_garbage();result.update(test_map());(out/'saved-character-foundation.json').write_text(json.dumps(result,indent=2))
finally:
 gc.collect();unreal.SystemLibrary.quit_editor()


