import unreal,gc,json
B='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate6Refinement/'
PATH='/Game/Vehicles/Gate6/BP_ClassCSystemsMotorhome'
def configure():
 assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level('/Game/Maps/Gate6FuelElectricalTest')
 assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
 bp=unreal.load_asset(PATH);c=unreal.get_default_object(unreal.EditorAssetLibrary.load_blueprint_class(PATH))
 c.set_editor_property('bInteractiveHouseDoor',True)
 unreal.BlueprintEditorLibrary.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,False)
 actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
 v=next(a for a in actors if isinstance(a,unreal.RVInteriorMotorhome));v.set_editor_property('bInteractiveHouseDoor',True);v.refresh_configuration()
 for a in actors:
  if isinstance(a,unreal.RVRestPoint) and str(a.get_editor_property('DisplayName'))=='Rear bed':
   a.set_editor_property('bUseLyingPose',True)
   a.set_editor_property('LyingOffset',unreal.Vector(-70,15,50))
   a.set_editor_property('LyingRotation',unreal.Rotator(yaw=90))
   a.set_editor_property('WakeAisleLocation',unreal.Vector(-185,0,185))
 assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
 assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
 json.dump({'interactive_house_door':True,'rear_bed_pose':True,'saved':True},open(B+'configured.json','w'),indent=2)
configure();gc.collect();unreal.SystemLibrary.quit_editor()
