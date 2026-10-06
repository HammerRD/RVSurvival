import unreal,gc
def configure():
 bp=unreal.load_asset('/Game/Vehicles/Gate6/BP_ClassCSystemsMotorhome')
 c=unreal.get_default_object(unreal.EditorAssetLibrary.load_blueprint_class('/Game/Vehicles/Gate6/BP_ClassCSystemsMotorhome'))
 defs=list(c.get_editor_property('Stations'))
 for d in defs:
  if str(d.name)=='Navigation':d.set_editor_property('RequiredPowerLoad','PoweredStation')
 c.set_editor_property('Stations',defs)
 profile=unreal.load_asset('/Game/Resources/DA_NormalRVEnergy')
 tuning=profile.get_editor_property('Values');loads=list(tuning.get_editor_property('Loads'))
 for load in loads:
  if str(load.id)=='PoweredStation':load.set_editor_property('bEnabled',True)
 tuning.set_editor_property('Loads',loads);profile.set_editor_property('Values',tuning)
 assert unreal.EditorAssetLibrary.save_loaded_asset(profile,False)
 unreal.BlueprintEditorLibrary.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,False)
 assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level('/Game/Maps/Gate6FuelElectricalTest')
 assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
 assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
configure();gc.collect();unreal.SystemLibrary.collect_garbage();unreal.log('GATE6_POWER_STATION_SAVED');unreal.SystemLibrary.quit_editor()
