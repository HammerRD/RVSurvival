"""Project-side native Unreal hand IK derivative; preserves accepted animation assets."""
import unreal,json,gc,traceback
from pathlib import Path
root=Path('D:/GitHub/RVSurvival/RVSurvival');out=root/'Docs/Gate9_5Results';folder='/Game/Characters/RV/Gate9_5'
def run():
 pawn=unreal.load_asset(folder+'/BP_Gate9_5Survivor');cdo=unreal.get_default_object(unreal.EditorAssetLibrary.load_blueprint_class(folder+'/BP_Gate9_5Survivor'));presentation=cdo.get_component_by_class(unreal.RVCharacterPresentationComponent);original=presentation.get_editor_property('Profile')
 profile=unreal.load_asset(folder+'/DA_Gate9_5HumanoidProfile') or unreal.EditorAssetLibrary.duplicate_asset(original.get_path_name().split('.')[0],folder+'/DA_Gate9_5HumanoidProfile')
 oldclass=original.get_editor_property('AnimationClass');blueprint=unreal.load_asset(folder+'/ABP_Gate9_5Humanoid') or unreal.EditorAssetLibrary.duplicate_asset(oldclass.get_path_name().split('.')[0],folder+'/ABP_Gate9_5Humanoid')
 anchors=list(profile.get_editor_property('EquipmentAnchors'));primary=next(a.bone for a in anchors if str(a.id)=='Tool');support=next(a.bone for a in anchors if str(a.id)=='CarriedItem')
 assert unreal.RVCharacterContentLibrary.add_weapon_grip_ik(blueprint,primary,support)
 assert unreal.EditorAssetLibrary.save_loaded_asset(blueprint,False)
 profile.modify();profile.set_editor_property('AnimationClass',unreal.EditorAssetLibrary.load_blueprint_class(folder+'/ABP_Gate9_5Humanoid'));assert unreal.EditorAssetLibrary.save_loaded_asset(profile,False)
 pawn.modify();cdo.modify();presentation.modify();presentation.set_editor_property('Profile',profile);assert unreal.EditorAssetLibrary.save_loaded_asset(pawn,False)
 return {'blueprint':blueprint.get_path_name(),'profile':profile.get_path_name(),'primary_bone':str(primary),'support_bone':str(support),'owner_only_ads':True,'reload_disables_ik':True,'native_nodes':['LocalToComponentSpace','TwoBoneIK x2','ModifyBone rotation','ComponentToLocalSpace'],'saved':True}
try:(out/'native-ik-content.json').write_text(json.dumps(run(),indent=2))
except Exception:(out/'native-ik-content-error.txt').write_text(traceback.format_exc());traceback.print_exc()
finally:gc.collect();unreal.SystemLibrary.quit_editor()
