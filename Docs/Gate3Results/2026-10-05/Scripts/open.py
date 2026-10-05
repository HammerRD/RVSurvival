import unreal
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level('/Game/Maps/Gate3MovingInteriorTest')
unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings')).set_editor_property('bThrottleCPUWhenNotForeground',False)
exec(open('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate3Validation/jobs.py').read(),{'__name__':'__main__'})
