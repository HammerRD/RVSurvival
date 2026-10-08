import unreal,gc
from pathlib import Path
folder='/Game/Characters/RV';profile=unreal.load_asset(folder+'/DA_MannyPresentation');profile.modify();profile.set_editor_property('BedOffset',unreal.Vector(85,0,-15));profile.set_editor_property('DownedOffset',unreal.Vector(85,0,4));profile.set_editor_property('SeatedOffset',unreal.Vector(0,0,-25));profile.set_editor_property('OwnerCameraOffset',unreal.Vector(20,0,0));assert unreal.EditorAssetLibrary.save_loaded_asset(profile,False);mesh=unreal.load_asset('/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple')
legs={'thigh_l':unreal.Vector(0,1,0),'thigh_r':unreal.Vector(0,1,0),'calf_l':unreal.Vector(0,0,-1),'calf_r':unreal.Vector(0,0,-1)}
for name in ['Driver','Passenger','DownedSeated']:
 pose=unreal.load_asset(folder+'/Animations/A_Prototype'+name);directions=dict(legs)
 if name=='Driver':
  directions.update({'upperarm_l':unreal.Vector(0,1,-1),'upperarm_r':unreal.Vector(0,1,-1),'lowerarm_l':unreal.Vector(0,1,0.2),'lowerarm_r':unreal.Vector(0,1,0.2)})
 else:
  directions.update({'upperarm_l':unreal.Vector(0,0,-1),'upperarm_r':unreal.Vector(0,0,-1),'lowerarm_l':unreal.Vector(0,1,0.15),'lowerarm_r':unreal.Vector(0,1,0.15)})
 assert unreal.RVCharacterContentLibrary.align_pose_bones(pose,mesh,directions);assert unreal.EditorAssetLibrary.save_loaded_asset(pose,False)
pose=None;mesh=None;gc.collect();unreal.SystemLibrary.quit_editor()

