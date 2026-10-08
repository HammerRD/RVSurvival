"""Aim prototype climbing arms toward the rungs; preserve the leg-cycle tracks."""
import unreal,gc
pose=unreal.load_asset('/Game/Characters/RV/Animations/A_PrototypeLadder')
mesh=unreal.load_asset('/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple')
directions={'upperarm_l':unreal.Vector(.25,.5,1),'upperarm_r':unreal.Vector(-.25,.5,1),'lowerarm_l':unreal.Vector(0,.7,.7),'lowerarm_r':unreal.Vector(0,.7,.7)}
assert unreal.RVCharacterContentLibrary.align_pose_bones(pose,mesh,directions)
assert unreal.EditorAssetLibrary.save_loaded_asset(pose,False)
pose=None;mesh=None;gc.collect();unreal.SystemLibrary.quit_editor()
