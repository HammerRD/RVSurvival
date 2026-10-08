import unreal,gc

def fix_saved_aim_graph():
 bp=unreal.load_asset('/Game/Characters/RV/Gate9/ABP_Gate9Humanoid');assert unreal.EditorAssetLibrary.save_loaded_asset(bp,False)
 poses=[unreal.load_asset('/Game/Characters/RV/Animations/A_Prototype'+n) for n in ['Driver','Passenger','Bed','Downed','Ladder','Treatment']]+[unreal.load_asset('/Game/Characters/Mannequins/Anims/Unarmed/Jump/'+n) for n in ['MM_Fall_Loop','MM_Jump','MM_Land']]+[unreal.load_asset('/Game/Characters/RV/Animations/A_PrototypeDownedSeated')]
 assert unreal.RVCharacterContentLibrary.build_animation_graph(bp,unreal.load_asset('/Game/Characters/RV/Animations/BS_RVLocomotion'),poses,unreal.load_asset('/Game/Characters/RV/Gate9/BS_PistolLocomotion'),unreal.load_asset('/Game/Characters/Mannequins/Anims/Pistol/Aim/AO_Pistol'))
 assert unreal.EditorAssetLibrary.save_loaded_asset(bp,False)
fix_saved_aim_graph();gc.collect()
exec(compile(open('D:/GitHub/RVSurvival/RVSurvival/Tools/Validation/Gate9/launch_manual_visual.py').read(),'launch_manual_visual.py','exec'))
