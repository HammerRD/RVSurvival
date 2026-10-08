from pathlib import Path
import json
r=Path('D:/GitHub/RVSurvival/RVSurvival');d=r/'Tools/Validation/Gate8_5';b=r/'Saved/Gate8_5Validation'
for name in ['process_startup.py','process_ready.py','process_refinement.py','launch_process.py']:
 text=(r/'Tools/Validation/Gate6PhysicalRefinement'/name).read_text().replace('Saved/Gate6PhysicalRefinement','Saved/Gate8_5Validation').replace('Gate6FuelElectricalTest','Gate8_5CharacterTest')
 if name=='launch_process.py':text=text.replace('assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)','assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()')
 if name=='process_refinement.py':
  extra='''
camera=None
visual_rows=[]
def inspect_remote(name,c,kind='seat'):
 global camera
 if c==p:return
 component=c.get_component_by_class(unreal.RVCharacterPresentationComponent)
 skeletal=c.get_editor_property('Mesh');anim=skeletal.get_anim_instance()
 check('remote_skeletal_'+name,component.has_configured_visuals() and isinstance(anim,unreal.RVHumanoidAnimInstance),component.get_editor_property('VisualState'))
 target=skeletal.get_socket_location('spine_03');q=v.get_actor_transform().inverse_transform_location(target)
 if kind=='bed':delta=unreal.Vector(100,-q.y,100)
 elif kind=='ladder':delta=unreal.Vector(-200,100,30)
 else:delta=unreal.Vector(-65,-65 if q.y>0 else 65,35)
 location=target+v.get_actor_transform().transform_location(delta)-v.get_actor_location()
 rotation=unreal.MathLibrary.find_look_at_rotation(location,target)
 if camera is None:camera=unreal.RVCharacterContentLibrary.spawn_observation_camera(v,location,rotation)
 else:camera.set_actor_location_and_rotation(location,rotation,False,True)
 pc.set_view_target_with_blend(camera,0)
 visual_rows.append({'name':name,'remote':True,'pose_index':anim.get_editor_property('PoseIndex'),'local_position':local(c),'camera':str(location)})
def capture(name):cmd('shot showui filename='+str(B/(config['name']+('_server_' if authority else '_client_')+name+'.png')).replace('\\\\','/')+' -nosuffix')
def restore_view():pc.set_view_target_with_blend(pc.get_controlled_pawn(),0)
for when,name,character,kind in [(8.0,'driver',dp,'seat'),(13.1,'passenger',wp,'seat'),(21.9,'dinette_front',wp,'seat'),(27.6,'dinette_rear',wp,'seat'),(33.0,'bed',wp,'bed'),(57.0,'ladder',wp,'ladder')]:
 delay=20 if when>=29 else 0
 at(when+delay,lambda name=name,c=character,kind=kind:inspect_remote(name,c,kind))
 at(when+delay+.2,lambda name=name,c=character:capture(name) if c!=p else None)
 at(when+delay+.4,restore_view)
'''
  text=text.replace('events.sort(key=lambda pair:pair[0])',extra+'\nevents.sort(key=lambda pair:pair[0])')
  text=text.replace("'results':results,'samples':samples","'results':results,'visual_observations':visual_rows,'samples':samples")
  text=text.replace("'ladder']:globals()[name]=None","'ladder','camera']:globals()[name]=None")
 (d/name).write_text(text);(b/name).write_text(text)
(b/'case.json').write_text(json.dumps({'name':'character_host_baseline','driver':'host','network':False,'disconnect':''}))


