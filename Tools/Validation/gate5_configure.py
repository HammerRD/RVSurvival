import unreal,json,gc
B='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate5Validation/'
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level('/Game/Maps/Gate5SurvivalTest')
def configure():
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for p in actors.get_all_level_actors():
        if p.get_class()==unreal.load_class(None,'/Script/RVSurvival.RVStoragePoint'):
            c=p.get_editor_property('Container')
            if str(c.get_editor_property('DisplayName'))=='Water supplies':
                c.set_editor_property('AllowedTags',unreal.GameplayTagLibrary.make_gameplay_tag_container_from_array([unreal.RVItemDefinition.find_registered_tag('Item.Category.Water')]))
    tools=unreal.AssetToolsHelpers.get_asset_tools()
    profile_cls=unreal.load_class(None,'/Script/RVSurvival.RVNeedsProfile')
    factory=unreal.DataAssetFactory();factory.set_editor_property('DataAssetClass',profile_cls)
    profile=unreal.load_asset('/Game/Survival/DA_NormalNeeds') or tools.create_asset('DA_NormalNeeds','/Game/Survival',profile_cls,factory)
    assert unreal.EditorAssetLibrary.save_loaded_asset(profile)
    ps=unreal.load_asset('/Game/Survival/BP_SurvivalPlayerState')
    if not ps:
        factory=unreal.BlueprintFactory();factory.set_editor_property('ParentClass',unreal.load_class(None,'/Script/RVSurvival.RVPlayerState'))
        ps=tools.create_asset('BP_SurvivalPlayerState','/Game/Survival',unreal.Blueprint,factory)
    pscls=unreal.EditorAssetLibrary.load_blueprint_class('/Game/Survival/BP_SurvivalPlayerState')
    unreal.get_default_object(pscls).get_editor_property('Needs').set_editor_property('TuningAsset',profile)
    unreal.BlueprintEditorLibrary.compile_blueprint(ps);assert unreal.EditorAssetLibrary.save_loaded_asset(ps)
    world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();settings=world.get_world_settings();source=settings.get_editor_property('DefaultGameMode')
    gm=unreal.load_asset('/Game/Survival/BP_Gate5GameMode') or unreal.EditorAssetLibrary.duplicate_asset(source.get_path_name().removesuffix('_C'),'/Game/Survival/BP_Gate5GameMode')
    gmcls=unreal.EditorAssetLibrary.load_blueprint_class('/Game/Survival/BP_Gate5GameMode');unreal.get_default_object(gmcls).set_editor_property('PlayerStateClass',pscls)
    unreal.BlueprintEditorLibrary.compile_blueprint(gm);assert unreal.EditorAssetLibrary.save_loaded_asset(gm)
    settings.set_editor_property('DefaultGameMode',gmcls)
    assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    json.dump({'map':'/Game/Maps/Gate5SurvivalTest','actors':len(actors.get_all_level_actors()),'rest':['Rear bed','Dinette rest'],'profile':'/Game/Survival/DA_NormalNeeds'},open(B+'fixture.json','w'),indent=2)
configure()
gc.collect();unreal.SystemLibrary.collect_garbage();unreal.log('GATE5_CONTENT_SAVED');unreal.SystemLibrary.quit_editor()
