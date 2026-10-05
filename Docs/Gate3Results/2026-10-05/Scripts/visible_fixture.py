import unreal,json
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert level.load_level('/Game/Maps/Gate3MovingInteriorTest')
tools=unreal.AssetToolsHelpers.get_asset_tools();bp=unreal.load_asset('/Game/Vehicles/Gate3/BP_Gate3GameMode')
if not bp:
 f=unreal.BlueprintFactory();f.set_editor_property('parent_class',unreal.load_class(None,'/Script/RVSurvival.RVGameMode'));bp=tools.create_asset('BP_Gate3GameMode','/Game/Vehicles/Gate3',unreal.Blueprint,f)
c=unreal.get_default_object(bp.generated_class());c.set_editor_property('DefaultPawnClass',unreal.load_class(None,'/Script/RVSurvival.RVInteriorTestCharacter'));unreal.BlueprintEditorLibrary.compile_blueprint(bp);unreal.EditorAssetLibrary.save_loaded_asset(bp,False)
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();w.get_world_settings().set_editor_property('default_game_mode',bp.generated_class());assert level.save_current_level()
unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings')).set_editor_property('bThrottleCPUWhenNotForeground',False)
exec(open('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate3Validation/jobs.py').read(),{'__name__':'__main__'})
