"""Transfer scalar Gate6 collision/roof configuration; never retain world UObjects."""
import unreal,json,gc
from pathlib import Path
ROOT=Path('D:/GitHub/RVSurvival/RVSurvival')
def baseline():
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    rv=next(a for a in actors if isinstance(a,unreal.RVSystemsMotorhome))
    def v(x):return [x.x,x.y,x.z]
    return [{'name':str(d.name),'center':v(d.center),'extent':v(d.extent),'floor':d.get_editor_property('bPassengerFloor'),'visible':d.get_editor_property('bVisiblePrototype')} for d in rv.get_editor_property('InteriorCollision')]
def configure(data):
    editor=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors=editor.get_all_level_actors()
    rv=next(a for a in actors if isinstance(a,unreal.RVMechanicalMotorhome))
    removed=[]
    for a in actors:
        if isinstance(a,unreal.RVRestPoint) and str(a.get_editor_property('DisplayName'))=='Dinette rest':
            removed.append(a.get_actor_label());assert editor.destroy_actor(a)
    collision=[]
    for x in data:
        d=unreal.RVInteriorCollision();d.set_editor_property('Name',x['name']);d.set_editor_property('Center',unreal.Vector(*x['center']));d.set_editor_property('Extent',unreal.Vector(*x['extent']));d.set_editor_property('bPassengerFloor',x['floor']);d.set_editor_property('bVisiblePrototype',x['visible']);collision.append(d)
    rv.set_editor_property('InteriorCollision',collision);rv.set_editor_property('bPhysicalDoorEntry',True);rv.refresh_configuration()
    for a in actors:
        if isinstance(a,unreal.RVLadder):
            a.set_editor_property('bRoofAccess',True);a.set_editor_property('RoofSurfaceHeight',319.6);a.set_editor_property('RoofExitLocal',unreal.Vector(-315,75,410));a.set_editor_property('ClimbHeight',335.6)
    bp=unreal.load_asset('/Game/Vehicles/Gate7/BP_ClassCMechanicalMotorhome')
    cdo=unreal.get_default_object(unreal.EditorAssetLibrary.load_blueprint_class('/Game/Vehicles/Gate7/BP_ClassCMechanicalMotorhome'))
    cdo.set_editor_property('InteriorCollision',collision);cdo.set_editor_property('bPhysicalDoorEntry',True)
    unreal.BlueprintEditorLibrary.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,False)
    assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    return {'saved':True,'removed':removed,'collision_count':len(collision),'physical_entry':True,'roof_access':True,'mechanical_profile':rv.get_editor_property('CoolingSystem').get_editor_property('Profile').get_path_name()}
try:
    levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    assert levels.load_level('/Game/Maps/Gate6FuelElectricalTest')
    data=baseline();gc.collect();unreal.SystemLibrary.collect_garbage()
    assert levels.load_level('/Game/Maps/Gate7MechanicalTest')
    result=configure(data)
    (ROOT/'Saved/Gate7Resume/integrated.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
finally:unreal.SystemLibrary.quit_editor()
