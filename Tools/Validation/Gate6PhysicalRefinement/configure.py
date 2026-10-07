"""Project-side Gate6 content milestone. Save before/after; scoped refs only."""
import unreal,json
from pathlib import Path
B=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate6PhysicalRefinement')
def configure():
    levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    assert levels.load_level('/Game/Maps/Gate6FuelElectricalTest')
    assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    editor=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors=editor.get_all_level_actors()
    rv=next(a for a in actors if isinstance(a,unreal.RVSystemsMotorhome))
    removed=[]
    for actor in actors:
        if isinstance(actor,unreal.RVRestPoint) and str(actor.get_editor_property('DisplayName'))=='Dinette rest':
            assert not actor.get_editor_property('Occupant')
            removed.append(actor.get_actor_label());assert editor.destroy_actor(actor)
    collision=list(rv.get_editor_property('InteriorCollision'))
    # Doorway/well starts atx55. Keep a fitted kitchen proxy beside it rather
    # than blocking its left half with the old x85 rectangular cabinet.
    for d in collision:
        if str(d.name)=='KitchenCabinet':
            d.set_editor_property('Center',unreal.Vector(5,80,130));d.set_editor_property('Extent',unreal.Vector(50,35,43))
    definitions=[('RoofWalkMain',(-65,0,316.6),(290,116,3),True),
                 ('RoofAC',(68,0,333.6),(30,22,14),False),
                 ('RoofVentRear',(-211,27,322.5),(24,24,3),False)]
    for name,center,extent,floor in definitions:
        d=next((d for d in collision if str(d.name)==name),None)
        if d is None:d=unreal.RVInteriorCollision()
        d.set_editor_property('Name',name);d.set_editor_property('Center',unreal.Vector(*center));d.set_editor_property('Extent',unreal.Vector(*extent))
        d.set_editor_property('bPassengerFloor',floor)
        index=next((i for i,p in enumerate(collision) if str(p.name)==name),None)
        if index is None:collision.append(d)
        else:collision[index]=d
    rv.set_editor_property('InteriorCollision',collision);rv.set_editor_property('bPhysicalDoorEntry',True)
    rv.refresh_configuration()
    ladder=next(a for a in actors if isinstance(a,unreal.RVLadder))
    ladder.set_editor_property('bRoofAccess',True)
    ladder.set_editor_property('RoofSurfaceHeight',319.6)
    ladder.set_editor_property('RoofExitLocal',unreal.Vector(-315,75,410))
    ladder.set_editor_property('ClimbHeight',322.6)
    ladder.set_actor_label('Gate6_RearLadder_RoofAccess')
    assert levels.save_current_level()
    bp_path='/Game/Vehicles/Gate6/BP_ClassCSystemsMotorhome'
    bp=unreal.load_asset(bp_path);cdo=unreal.get_default_object(unreal.EditorAssetLibrary.load_blueprint_class(bp_path))
    for field in ['InteriorCollision','bPhysicalDoorEntry']:cdo.set_editor_property(field,rv.get_editor_property(field))
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    assert unreal.EditorAssetLibrary.save_loaded_asset(bp,False)
    del rv,cdo,bp,actors,ladder
    assert levels.save_current_level()
    assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    return {'saved':True,'removed_rest_markers':removed,'roof_surface_cm':319.6,'new_collision':definitions,'physical_door_entry':True,'validation':'pending'}
try:(B/'configured.json').write_text(json.dumps(configure(),indent=2),encoding='utf-8')
finally:unreal.SystemLibrary.quit_editor()
