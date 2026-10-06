import unreal

def inspect_refined_assets(check):
 cls=unreal.EditorAssetLibrary.load_blueprint_class('/Game/Vehicles/Gate6/BP_ClassCSystemsMotorhome')
 c=unreal.get_default_object(cls)
 check('live_house_door_saved_enabled',c.get_editor_property('bInteractiveHouseDoor'))
 check('saved_replaceable_door_parts',str(c.get_editor_property('HouseDoorPartName'))=='Art_RV_Van_Door_Back' and str(c.get_editor_property('HouseDoorGlassPartName'))=='Art_RV_Glass_Door_Back')
 actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
 bed=next(a for a in actors if isinstance(a,unreal.RVRestPoint) and str(a.get_editor_property('DisplayName'))=='Rear bed')
 check('saved_rear_lying_state',bed.get_editor_property('bUseLyingPose'))
 offset=bed.get_editor_property('LyingCameraOffset')
 check('saved_head_camera',offset.x==80 and offset.y==0 and offset.z==25)
 offset=bed.get_editor_property('WakeAisleLocation')
 check('saved_wake_aisle',offset.x==-185 and offset.y==0 and offset.z==185)

