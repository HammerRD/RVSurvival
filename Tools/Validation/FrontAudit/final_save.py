import unreal, json, gc

B = 'D:/GitHub/RVSurvival/RVSurvival/Docs/Gate5FrontAudit/'
assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level('/Game/Maps/Gate5SurvivalTest')

def inspect():
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    vehicles = [a for a in actors if isinstance(a, unreal.RVInteriorMotorhome)]
    assert len(vehicles) == 1
    vehicle = vehicles[0]
    assert vehicle.get_class().get_name() == 'BP_ClassCRefinedMotorhome_C'
    boxes = vehicle.get_editor_property('InteriorCollision')
    names = {str(b.name) for b in boxes}
    assert {'FrontFascia', 'HoodTop', 'CabExteriorLeft', 'CabExteriorRight', 'FrontWall'}.issubset(names)
    return {'map': '/Game/Maps/Gate5SurvivalTest', 'vehicle_class': vehicle.get_class().get_path_name(),
            'actor_count': len(actors), 'collision': [
                {'name': str(b.name), 'center': [b.center.x,b.center.y,b.center.z],
                 'extent': [b.extent.x,b.extent.y,b.extent.z]} for b in boxes]}

data = inspect()  # Only primitive data survives the inspection.
gc.collect()
settings = unreal.get_default_object(unreal.load_class(None, '/Script/UnrealEd.LevelEditorPlaySettings'))
settings.set_editor_property('RunUnderOneProcess', True)
settings.set_editor_property('PlayNumberOfClients', 1)
settings.set_editor_property('AdditionalLaunchParameters', '')
network = settings.get_editor_property('NetworkEmulationSettings')
network.set_editor_property('bIsNetworkEmulationEnabled', False)
settings.set_editor_property('NetworkEmulationSettings', network)
assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
data['save_before_after'] = True
json.dump(data, open(B + 'final-saved-inspection.json', 'w'), indent=2)
unreal.log('FRONT_AUDIT_FINAL_SAVED')
unreal.SystemLibrary.quit_editor()
