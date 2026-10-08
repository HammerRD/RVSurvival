import unreal,json
from pathlib import Path
def inspect_gate9_pose():
 w=next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='Gate9CombatInfectedTest' and unreal.GameplayStatics.get_player_controller(w,0) and unreal.GameplayStatics.get_player_controller(w,0).get_controlled_pawn());p=unreal.GameplayStatics.get_player_controller(w,0).get_controlled_pawn();an=p.mesh.get_anim_instance();ao=unreal.load_asset('/Game/Characters/Mannequins/Anims/Pistol/Aim/AO_Pistol')
 report={'anim_pitch':an.aim_pitch,'speed':an.ground_speed,'pose':an.pose_index,'hand_rotation':str(p.mesh.get_socket_rotation('hand_r')),'head_location':str(p.mesh.get_socket_location('head')),'hand_location':str(p.mesh.get_socket_location('hand_r')),'actor_rotation':str(p.get_actor_rotation()),'eyes':str(p.get_actor_eyes_view_point()),'aim_axes':[{k:str(a.get_editor_property(k)) for k in ['DisplayName','Min','Max']} for a in ao.get_editor_property('BlendParameters')], 'aim_samples':[{'position':str(a.get_editor_property('SampleValue')),'animation':a.get_editor_property('Animation').get_name(),'additive':str(a.get_editor_property('Animation').get_editor_property('AdditiveAnimType')),'base':str(a.get_editor_property('Animation').get_editor_property('RefPoseSeq'))} for a in ao.get_editor_property('SampleData')]}
 report['animation_bones']=[]
 for path in ['/Game/Characters/Mannequins/Anims/Pistol/MF_Pistol_Idle_ADS','/Game/Characters/Mannequins/Anims/Pistol/Aim/MF_Pistol_Idle_ADS1']:
  clip=unreal.load_asset(path);opts=unreal.AnimPoseEvaluationOptions();opts.set_editor_property('OptionalSkeletalMesh',p.mesh.skeletal_mesh);pose=unreal.AnimPoseExtensions.get_anim_pose_at_time(clip,0,opts)
  report['animation_bones'].append({'clip':path,'hand':str(unreal.AnimPoseExtensions.get_bone_pose(pose,'hand_r',unreal.AnimPoseSpaces.WORLD)),'head':str(unreal.AnimPoseExtensions.get_bone_pose(pose,'head',unreal.AnimPoseSpaces.WORLD))})
 Path('D:/GitHub/RVSurvival/RVSurvival/Docs/Gate9Results/pose-inspection.json').write_text(json.dumps(report,indent=2))
inspect_gate9_pose()



