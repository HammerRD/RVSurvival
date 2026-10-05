import unreal
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
elapsed=0
def start(dt):
    global elapsed
    elapsed+=dt
    if elapsed>5:
        unreal.unregister_slate_post_tick_callback(h)
        exec(open('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate3Validation/integration_regression.py').read(),{'__name__':'__main__'})
h=unreal.register_slate_post_tick_callback(start)
