import unreal
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
level.load_level('/Game/Maps/Gate2VehicleTest')
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.LevelEditorPlaySettings'))
settings.set_editor_property('PlayNumberOfClients',2)
settings.set_editor_property('RunUnderOneProcess',True)
network=settings.get_editor_property('NetworkEmulationSettings')
network.set_editor_property('bIsNetworkEmulationEnabled',False)
settings.set_editor_property('NetworkEmulationSettings',network)
unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings')).set_editor_property('bThrottleCPUWhenNotForeground',False)
unreal.SystemLibrary.execute_console_command(unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world(),'t.MaxFPS 60')
level.editor_request_begin_play()
elapsed=0
def start(dt):
    global elapsed
    elapsed+=dt
    if elapsed>5:
        unreal.unregister_slate_post_tick_callback(h)
        exec(open('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate2Validation/multi.py').read(),{'__name__':'__main__'})
h=unreal.register_slate_post_tick_callback(start)
