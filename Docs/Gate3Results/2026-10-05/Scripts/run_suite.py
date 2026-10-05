from runner_runtime import load_runner
import unreal
load_runner('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate3Validation/play_settings.py')
s=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.LevelEditorPlaySettings'))
s.set_editor_property('RunUnderOneProcess',True);s.set_editor_property('AdditionalLaunchParameters','')
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
elapsed=0
def start(dt):
    global elapsed
    elapsed+=dt
    if elapsed>5:
        unreal.unregister_slate_post_tick_callback(h)
        load_runner('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate3Validation/suite.py')
h=unreal.register_slate_post_tick_callback(start)
