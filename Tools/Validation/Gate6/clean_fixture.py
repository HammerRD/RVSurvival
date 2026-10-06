import unreal,json,gc

def clean():
    level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    assert level.load_level('/Game/Maps/Gate6FuelElectricalTest')
    assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    removed=[]
    for actor in actors.get_all_level_actors():
        if not isinstance(actor,unreal.RVWorldItem): continue
        definition=actor.get_editor_property('Item').definition
        if definition and str(definition.get_editor_property('CatalogId'))=='FuelCan' and not definition.get_editor_property('Fuel').get_editor_property('bFuelContainer'):
            removed.append(actor.get_actor_label())
            assert actors.destroy_actor(actor)
    assert len(removed)==1,removed
    assert level.save_current_level()
    assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    return {'results':[{'case':'remove_only_gate6_legacy_inert_pickup','pass':True,'detail':removed}], 'actors':len(actors.get_all_level_actors()),'pickups':sum(isinstance(a,unreal.RVWorldItem) for a in actors.get_all_level_actors())}

data=clean()
gc.collect();unreal.SystemLibrary.collect_garbage()
json.dump(data,open('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate6Validation/fixture-clean.json','w'),indent=2)
unreal.SystemLibrary.quit_editor()
