"""Project-side native Unreal animation authoring; no vendor package writes."""
import unreal,json,gc,traceback
from pathlib import Path
r=Path('D:/GitHub/RVSurvival/RVSurvival');out=r/'Saved/Gate9_5Validation';folder='/Game/Characters/RV/Gate9_5/Refinement';items='/Game/Combat/Gate9_5/Items'
def run():
 tools=unreal.AssetToolsHelpers.get_asset_tools();mesh=unreal.load_asset('/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple');assert mesh
 def save(a):assert a and unreal.EditorAssetLibrary.save_loaded_asset(a,False)
 def profile(name):
  factory=unreal.DataAssetFactory();factory.set_editor_property('DataAssetClass',unreal.RVWeaponPresentationProfile)
  return unreal.load_asset(folder+'/'+name) or tools.create_asset(name,folder,unreal.RVWeaponPresentationProfile,factory)
 idle=unreal.load_asset('/Game/Characters/Mannequins/Anims/Unarmed/MM_Idle');pistolready=unreal.load_asset('/Game/Characters/Mannequins/Anims/Pistol/MF_Pistol_Idle_ADS')
 ready=unreal.RVCharacterContentLibrary.create_prototype_pose(folder+'/A_OneHandToolReady',mesh,{},False,pistolready)
 assert unreal.RVCharacterContentLibrary.align_pose_bones(ready,mesh,{'upperarm_r':unreal.Vector(.15,1,-.3),'lowerarm_r':unreal.Vector(0,1,.4),'upperarm_l':unreal.Vector(0,0,-1),'lowerarm_l':unreal.Vector(0,.15,-1)})
 save(ready);attacks=[]
 for i,name in enumerate(['Diagonal','Horizontal','Downward']):
  sequence=unreal.RVCharacterContentLibrary.create_one_handed_attack(folder+'/A_Crowbar'+name,mesh,ready,i);save(sequence)
  f=unreal.AnimMontageFactory();f.set_editor_property('TargetSkeleton',mesh.get_editor_property('Skeleton'));f.set_editor_property('SourceAnimation',sequence)
  montage=unreal.load_asset(folder+'/AM_Crowbar'+name) or tools.create_asset('AM_Crowbar'+name,folder,unreal.AnimMontage,f)
  tracks=montage.get_editor_property('SlotAnimTracks')
  for index,track in enumerate(tracks):track.set_editor_property('SlotName','DefaultSlot');tracks[index]=track
  montage.set_editor_property('SlotAnimTracks',tracks);save(montage);attacks.append(montage)
 handgun=profile('DA_HandgunPresentation');handgun.modify();handgun.set_editor_property('Family',unreal.RVWeaponFamily.HANDGUN);handgun.set_editor_property('bSupportHand',True);handgun.set_editor_property('ReadyPose',pistolready)
 handgun.set_editor_property('ReadyHand',unreal.Transform(location=unreal.Vector(45,8,50),rotation=unreal.Rotator(yaw=180)))
 handgun.set_editor_property('AimOffset',unreal.load_asset('/Game/Characters/Mannequins/Anims/Pistol/Aim/AO_Pistol'));handgun.set_editor_property('LocomotionOverlay',unreal.load_asset('/Game/Characters/RV/Gate9/BS_PistolLocomotion'));save(handgun)
 crowbar=profile('DA_OneHandedMeleePresentation');crowbar.modify();crowbar.set_editor_property('Family',unreal.RVWeaponFamily.ONE_HANDED_MELEE);crowbar.set_editor_property('bSupportHand',False);crowbar.set_editor_property('bOwnerReadyIK',False);crowbar.set_editor_property('ReadyPose',ready);crowbar.set_editor_property('LightAttacks',attacks);crowbar.set_editor_property('LightAttackHitSeconds',.27);save(crowbar)
 for name,family,order in [('DA_M1911_45ACP',handgun,10),('DA_PrototypeCrowbar',crowbar,20)]:
  asset=unreal.load_asset(items+'/'+name);asset.modify();data=asset.get_editor_property('Combat');data.set_editor_property('Presentation',family);data.set_editor_property('QuickAccessOrder',order);data.set_editor_property('bQuickAccess',True)
  if order==10:data.set_editor_property('SightEyeReliefCm',55)
  asset.set_editor_property('Combat',data);save(asset)
 blueprint=unreal.load_asset('/Game/Characters/RV/Gate9_5/ABP_Gate9_5Humanoid')
 poses=[unreal.load_asset('/Game/Characters/RV/Animations/A_Prototype'+n) for n in ['Driver','Passenger','Bed','Downed','Ladder','Treatment']]+[unreal.load_asset('/Game/Characters/Mannequins/Anims/Unarmed/Jump/'+n) for n in ['MM_Fall_Loop','MM_Jump','MM_Land']]+[unreal.load_asset('/Game/Characters/RV/Animations/A_PrototypeDownedSeated')]
 assert unreal.RVCharacterContentLibrary.build_animation_graph(blueprint,unreal.load_asset('/Game/Characters/RV/Animations/BS_RVLocomotion'),poses,handgun.get_editor_property('LocomotionOverlay'),handgun.get_editor_property('AimOffset'),ready)
 assert unreal.RVCharacterContentLibrary.add_weapon_grip_ik(blueprint,'hand_r','hand_l')
 cdo=unreal.get_default_object(unreal.EditorAssetLibrary.load_blueprint_class('/Game/Characters/RV/Gate9_5/ABP_Gate9_5Humanoid'));cdo.modify()
 for key,value in [('DefaultWeaponLocomotion',handgun.get_editor_property('LocomotionOverlay')),('DefaultWeaponAim',handgun.get_editor_property('AimOffset')),('DefaultToolReady',ready)]:cdo.set_editor_property(key,value)
 save(blueprint)
 factory=unreal.AnimBlueprintFactory();factory.set_editor_property('ParentClass',unreal.AnimInstance);factory.set_editor_property('TargetSkeleton',mesh.get_editor_property('Skeleton'));factory.set_editor_property('PreviewSkeletalMesh',mesh)
 owner=unreal.load_asset(folder+'/ABP_OwnerBodyCopy') or tools.create_asset('ABP_OwnerBodyCopy',folder,unreal.AnimBlueprint,factory)
 assert unreal.RVCharacterContentLibrary.build_owner_copy_pose_graph(owner,'neck_01');save(owner)
 import sys
 sys.path.insert(0,str(r/'Tools/Validation/Gate9_5'))
 from configure_owner_materials import create_owner_materials
 from correct_project_weapon_materials import configure
 configure()
 profile_asset=unreal.load_asset('/Game/Characters/RV/Gate9_5/DA_Gate9_5HumanoidProfile');profile_asset.modify();profile_asset.set_editor_property('FirstPersonAnimationClass',unreal.EditorAssetLibrary.load_blueprint_class(folder+'/ABP_OwnerBodyCopy'));profile_asset.set_editor_property('FirstPersonMaterials',create_owner_materials(mesh,folder+'/OwnerMaterials'));save(profile_asset)
 assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
 return {'saved':True,'profiles':[handgun.get_path_name(),crowbar.get_path_name()],'attacks':[m.get_path_name() for m in attacks],'support_space':'hand_r bone space, after primary rotation','weapon_attachment':'primary hand','source':'existing Epic free pistol/unarmed animations + project native animation data controller derivatives'}
try:(out/'weapon-family-content.json').write_text(json.dumps(run(),indent=2))
except Exception:(out/'weapon-family-content-error.txt').write_text(traceback.format_exc());traceback.print_exc()
finally:gc.collect();unreal.SystemLibrary.quit_editor()
