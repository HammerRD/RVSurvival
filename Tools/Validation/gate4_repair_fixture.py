import unreal,json,gc
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level('/Game/Maps/Gate4InventoryTest')
def repair():
 subsystem=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
 seen=set();removed=[]
 for actor in subsystem.get_all_level_actors():
  cls=actor.get_class().get_name()
  if cls not in ['RVWorldItem','RVStoragePoint']:continue
  p=actor.get_actor_location();key=(cls,round(p.x,2),round(p.y,2),round(p.z,2))
  if key in seen:
   removed.append(actor.get_path_name());assert subsystem.destroy_actor(actor)
  else:seen.add(key)
 assert len(seen)==17
 assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
 return removed
removed=repair()
json.dump({'removed_duplicate_fixture_actors':removed,'retained_gate4_actors':17},open('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate4Validation/fixture-recovery.json','w'),indent=2)
gc.collect();unreal.SystemLibrary.collect_garbage();unreal.log('GATE4_FIXTURE_DEDUPLICATED_AND_SAVED')
unreal.SystemLibrary.quit_editor()
