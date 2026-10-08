import unreal,gc

def tune_gate9_camera():
 profile=unreal.load_asset('/Game/Characters/RV/Gate9/DA_CombatPresentation');assert unreal.EditorAssetLibrary.save_loaded_asset(profile,False);profile.modify();profile.set_editor_property('OwnerCameraOffset',unreal.Vector(0,0,4));assert unreal.EditorAssetLibrary.save_loaded_asset(profile,False)
tune_gate9_camera();gc.collect()
exec(compile(open('D:/GitHub/RVSurvival/RVSurvival/Tools/Validation/Gate9/launch_manual_visual.py').read(),'launch_manual_visual.py','exec'))
