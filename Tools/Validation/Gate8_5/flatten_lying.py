import unreal,gc,math,json
from pathlib import Path
m=unreal.load_asset('/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple');report={}
for name in ['Bed','Downed']:
 p=unreal.load_asset('/Game/Characters/RV/Animations/A_Prototype'+name);t=unreal.RVCharacterContentLibrary.get_pose_bone_transforms(p,m);t={str(k):v for k,v in t.items()};head=t['head'].translation;pelvis=t['pelvis'].translation;dx=head.x-pelvis.x;dy=head.y-pelvis.y;length=math.hypot(dx,dy);d=unreal.Vector(-dx/length,-dy/length,0)
 report[name]={'before':{k:str(t[k].translation) for k in ['head','pelvis','calf_l','calf_r','foot_l','foot_r']},'leg_direction':str(d)}
 directions={k:d for k in ['thigh_l','thigh_r','calf_l','calf_r','foot_l','foot_r']}
 assert unreal.RVCharacterContentLibrary.align_pose_bones(p,m,directions);assert unreal.EditorAssetLibrary.save_loaded_asset(p,False)
 t={str(k):v for k,v in unreal.RVCharacterContentLibrary.get_pose_bone_transforms(p,m).items()};report[name]['after']={k:str(t[k].translation) for k in ['head','pelvis','calf_l','calf_r','foot_l','foot_r']}
profile=unreal.load_asset('/Game/Characters/RV/DA_MannyPresentation');profile.modify();profile.set_editor_property('BedOffset',unreal.Vector(-85,0,0));profile.set_editor_property('DownedOffset',unreal.Vector(85,0,15));assert unreal.EditorAssetLibrary.save_loaded_asset(profile,False)
Path('D:/GitHub/RVSurvival/RVSurvival/Docs/Gate8_5Results/lying-limb-authoring.json').write_text(json.dumps(report,indent=2))
p=None;m=None;t=None;profile=None;gc.collect();unreal.SystemLibrary.quit_editor()
