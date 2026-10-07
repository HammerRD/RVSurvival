"""Read saved Gate6 state and clear automation launch preferences; never start PIE."""
import unreal,json,gc
from pathlib import Path
root=Path('D:/GitHub/RVSurvival/RVSurvival')
def inspect_saved():
    assert not any('UEDPIE_' in world.get_path_name() for world in unreal.ObjectIterator(unreal.World))
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    rv=next(actor for actor in actors if isinstance(actor,unreal.RVSystemsMotorhome))
    rests=[str(actor.get_editor_property('DisplayName')) for actor in actors if isinstance(actor,unreal.RVRestPoint)]
    collision={str(box.name):box for box in rv.get_editor_property('InteriorCollision')}
    assert len(actors)==69 and rests==['Rear bed'] and rv.get_editor_property('bPhysicalDoorEntry')
    assert collision['EntryStepLow'].get_editor_property('bVisiblePrototype')
    roof=collision['RoofWalkMain']
    assert abs(roof.center.z+roof.extent.z-319.6)<.01
    assert abs(collision['KitchenCabinet'].center.x+collision['KitchenCabinet'].extent.x-55)<.01
    ladder=next(actor for actor in actors if isinstance(actor,unreal.RVLadder))
    assert ladder.get_editor_property('bRoofAccess')
    return {'map':'/Game/Maps/Gate6FuelElectricalTest','actors':len(actors),'rest_points':rests,'physical_entry':True,'roof_surface_cm':roof.center.z+roof.extent.z,'ladder_roof_access':True}
receipt=inspect_saved();gc.collect()
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.LevelEditorPlaySettings'))
settings.set_editor_property('PlayNumberOfClients',1)
settings.set_editor_property('RunUnderOneProcess',True)
# UE5.8 does not expose this private enum to Python. Its canonical config
# value is restored after normal shutdown, without adding a C++ workaround.
settings.set_editor_property('bLaunchSeparateServer',False)
settings.set_editor_property('AdditionalLaunchParameters','')
network=settings.get_editor_property('NetworkEmulationSettings')
network.set_editor_property('bIsNetworkEmulationEnabled',False)
settings.set_editor_property('NetworkEmulationSettings',network)
unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings')).set_editor_property('bThrottleCPUWhenNotForeground',True)
assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
receipt.update({'PIE_started':False,'clients':1,'one_process':True,'net_mode':'canonical config restoration after shutdown','emulation_enabled':False,'additional_launch_parameters':settings.get_editor_property('AdditionalLaunchParameters'),'save_all':True})
(root/'Docs/Gate6PhysicalRefinement/final-editor-preferences.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
unreal.log('PHYSICAL_REFINEMENT_PREFERENCES_RESTORED_NO_PIE')
unreal.SystemLibrary.quit_editor()
