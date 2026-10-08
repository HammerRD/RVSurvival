"""Historical focused authoring iteration; configure_character.py reproduces final tuning."""
import unreal,gc
p=unreal.load_asset('/Game/Characters/RV/Animations/A_PrototypeTreatment');m=unreal.load_asset('/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple')
d={'upperarm_l':unreal.Vector(0,1,-1),'upperarm_r':unreal.Vector(0,1,-1),'lowerarm_l':unreal.Vector(.2,1,.2),'lowerarm_r':unreal.Vector(-.2,1,.2)}
assert unreal.RVCharacterContentLibrary.align_pose_bones(p,m,d);assert unreal.EditorAssetLibrary.save_loaded_asset(p,False)
p=None;m=None;gc.collect();unreal.SystemLibrary.quit_editor()
