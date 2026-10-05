import unreal,json,gc
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level('/Game/Maps/Gate4InventoryTest')
def repair():
 subsystem=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
 SC=unreal.load_class(None,'/Script/RVSurvival.RVStoragePoint')
 rv=next(a for a in subsystem.get_all_level_actors() if isinstance(a,unreal.WheeledVehiclePawn))
 positions={'General cabinet':(-222,52,155),'Medical storage':(-117,52,155),'Pantry':(-12,-32,155),'Tool storage':(-220,-73,155)}
 result=[]
 for a in subsystem.get_all_level_actors():
  if a.get_class()!=SC:continue
  name=str(a.get_editor_property('Container').get_editor_property('DisplayName'))
  if name not in positions:continue
  old=rv.get_actor_transform().inverse_transform_location(a.get_actor_location())
  a.set_actor_location(rv.get_actor_transform().transform_location(unreal.Vector(*positions[name])),False,True)
  result.append({'storage':name,'old':[old.x,old.y,old.z],'new':positions[name]})
 assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
 return result
result=repair();json.dump(result,open('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate4Validation/storage-point-repair.json','w'),indent=2)
gc.collect();unreal.SystemLibrary.collect_garbage();unreal.log('GATE4_STORAGE_POINTS_SAVED');unreal.SystemLibrary.quit_editor()
