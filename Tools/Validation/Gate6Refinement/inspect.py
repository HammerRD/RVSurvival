import unreal,json,gc
B='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate6Refinement/'
def inspect():
 assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level('/Game/Maps/Gate6FuelElectricalTest')
 assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
 actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
 v=next(a for a in actors if isinstance(a,unreal.RVInteriorMotorhome))
 result={'parts':[],'collision':[],'stations':[],'rest':[]}
 for d in v.get_editor_property('VisualParts'):
  if any(n in str(d.name) for n in ['Door_Back','Bed','Interior']):
   b=d.mesh.get_bounds();result['parts'].append({'name':str(d.name),'transform':str(d.transform),'origin':str(b.origin),'extent':str(b.box_extent)})
 for d in v.get_editor_property('InteriorCollision'):result['collision'].append({'name':str(d.name),'center':str(d.center),'extent':str(d.extent),'floor':d.get_editor_property('bPassengerFloor')})
 for d in v.get_editor_property('Stations'):result['stations'].append({'name':str(d.name),'position':str(d.position)})
 for a in actors:
  if isinstance(a,unreal.RVRestPoint):result['rest'].append({'name':str(a.get_editor_property('DisplayName')),'local':str(v.get_actor_transform().inverse_transform_location(a.get_actor_location())),'parent':str(a.get_attach_parent_actor())})
 json.dump(result,open(B+'layout.json','w'),indent=2)
inspect();gc.collect();unreal.SystemLibrary.quit_editor()
