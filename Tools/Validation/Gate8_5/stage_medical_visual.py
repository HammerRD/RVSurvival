from pathlib import Path
r=Path('D:/GitHub/RVSurvival/RVSurvival');b=r/'Saved/Gate8_5Validation';d=r/'Tools/Validation/Gate8_5'
text=(r/'Tools/Validation/Gate8/process_medical.py').read_text().replace('Saved/Gate8Validation','Saved/Gate8_5Validation').replace('Gate8MedicalTest','Gate8_5CharacterTest')
extra='''
camera=None
visuals=[]
def inspect_pose(name,c,expected):
 global camera
 if c==p:return
 visual=c.get_component_by_class(unreal.RVCharacterPresentationComponent);mesh=c.get_editor_property('Mesh');anim=mesh.get_anim_instance()
 check('remote_pose_'+name,visual.has_configured_visuals() and anim.get_editor_property('PoseIndex')==expected,anim.get_editor_property('PoseIndex'))
 target=mesh.get_socket_location('spine_03');location=target+unreal.Vector(-140,140,85);rotation=unreal.MathLibrary.find_look_at_rotation(location,target)
 if camera is None:camera=unreal.RVCharacterContentLibrary.spawn_observation_camera(p,location,rotation)
 else:camera.set_actor_location_and_rotation(location,rotation,False,True)
 pc.set_view_target_with_blend(camera,0)
 visuals.append({'name':name,'pose_index':anim.get_editor_property('PoseIndex'),'region_transforms':{str(region):str(visual.get_body_region_transform(region)) for region in [unreal.RVBodyRegion.HEAD,unreal.RVBodyRegion.TORSO,unreal.RVBodyRegion.LEFT_ARM,unreal.RVBodyRegion.RIGHT_ARM,unreal.RVBodyRegion.LEFT_LEG,unreal.RVBodyRegion.RIGHT_LEG]}})
def snap(name):unreal.SystemLibrary.execute_console_command(pc,'shot showui filename='+str(B/(config['name']+'_'+role+'_'+name+'.png')).replace('\\\\','/')+' -nosuffix',pc)
def reset_view():pc.set_view_target_with_blend(pc.get_controlled_pawn(),0)
for when,name,c,expected in [(5,'downed',patient,4),(12,'treatment',healer,6),(39,'revived',patient,0)]:
 events.extend([(when,lambda name=name,c=c,expected=expected:inspect_pose(name,c,expected)),(when+.2,lambda name=name,c=c:snap(name) if c!=p else None),(when+.4,reset_view)])
events.sort(key=lambda item:item[0])
'''
text=text.replace('def tick(dt):',extra+'\ndef tick(dt):').replace("'results':results},indent=2)","'results':results,'visuals':visuals},indent=2)")
(d/'process_medical.py').write_text(text)
