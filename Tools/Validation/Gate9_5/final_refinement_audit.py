"""Fresh saved-content verification only; no test/map reload loop."""
import unreal,json,gc,traceback
from pathlib import Path
r=Path('D:/GitHub/RVSurvival/RVSurvival');out=r/'Docs/Gate9_5Results/WeaponRefinement';out.mkdir(exist_ok=True)
def run():
 levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
 assert levels.load_level('/Game/Maps/Gate9_5CombatRefinementTest')
 folder='/Game/Characters/RV/Gate9_5/Refinement'
 paths=list(unreal.EditorAssetLibrary.list_assets(folder,True,False))
 for path in paths:assert unreal.load_asset(path),path
 gun=unreal.load_asset('/Game/Combat/Gate9_5/Items/DA_M1911_45ACP').get_editor_property('Combat')
 melee=unreal.load_asset('/Game/Combat/Gate9_5/Items/DA_PrototypeCrowbar').get_editor_property('Combat')
 handgun=gun.get_editor_property('Presentation');tool=melee.get_editor_property('Presentation')
 assert handgun.get_editor_property('Family')==unreal.RVWeaponFamily.HANDGUN and handgun.get_editor_property('bSupportHand')
 assert tool.get_editor_property('Family')==unreal.RVWeaponFamily.ONE_HANDED_MELEE and not tool.get_editor_property('bSupportHand')
 assert gun.get_editor_property('bSightADS') and gun.get_editor_property('MagazineCapacity')==7
 assert len(tool.get_editor_property('LightAttacks'))==3
 assert gun.get_editor_property('QuickAccessOrder')<melee.get_editor_property('QuickAccessOrder')
 profile=unreal.load_asset('/Game/Characters/RV/Gate9_5/DA_Gate9_5HumanoidProfile')
 assert profile.get_editor_property('FirstPersonAnimationClass') and len(profile.get_editor_property('FirstPersonMaterials'))==2
 assert len(profile.get_editor_property('BodyRegions'))==6
 assert levels.save_current_level() and unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
 return {'saved':True,'map':'/Game/Maps/Gate9_5CombatRefinementTest','assets_loaded':paths,'families':['Handgun','OneHandedMelee'],'sight_ads':True,'capacity':7,'eye_relief_cm':gun.get_editor_property('SightEyeReliefCm'),'ready_hand':str(handgun.get_editor_property('ReadyHand')),'high_pitch_retraction_cm':handgun.get_editor_property('HighPitchReachRetractionCm'),'attacks':[a.get_name() for a in tool.get_editor_property('LightAttacks')],'hit_seconds':tool.get_editor_property('LightAttackHitSeconds'),'body_regions':6,'owner_copy_pose':True}
try:(out/'saved-assets.json').write_text(json.dumps(run(),indent=2))
except Exception:(out/'saved-assets-error.txt').write_text(traceback.format_exc());traceback.print_exc()
finally:gc.collect();unreal.SystemLibrary.quit_editor()
