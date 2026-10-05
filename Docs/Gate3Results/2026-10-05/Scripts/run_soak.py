import unreal
exec(open('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate3Validation/play_settings.py').read(),{'__name__':'__main__'})
s=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.LevelEditorPlaySettings'))
s.set_editor_property('RunUnderOneProcess',True);s.set_editor_property('AdditionalLaunchParameters','')
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
elapsed=0
def start(dt):
    global elapsed
    elapsed+=dt
    if elapsed>5:
        unreal.unregister_slate_post_tick_callback(h)
        exec(open('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate3Validation/soak.py').read(),{'__name__':'__main__'})
h=unreal.register_slate_post_tick_callback(start)
