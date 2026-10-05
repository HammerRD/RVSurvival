from runner_runtime import load_runner
import unreal
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
level.load_level('/Game/Maps/Gate1Test')
s=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.LevelEditorPlaySettings'))
s.set_editor_property('PlayNumberOfClients',1);s.set_editor_property('RunUnderOneProcess',True);s.set_editor_property('AdditionalLaunchParameters','')
n=s.get_editor_property('NetworkEmulationSettings');n.set_editor_property('bIsNetworkEmulationEnabled',False);s.set_editor_property('NetworkEmulationSettings',n)
level.editor_request_begin_play()
def begin_multi():
    s.set_editor_property('PlayNumberOfClients',2)
    level.editor_request_begin_play()
events=[(5,lambda:load_runner('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate1Validation/single.py')),(25,level.editor_request_end_play),(28,begin_multi),(34,lambda:load_runner('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate1Validation/multi.py')),(51,level.editor_request_end_play)]
t=0;i=0
def tick(dt):
    global t,i
    t+=dt
    try:
        while i<len(events) and t>=events[i][0]:f=events[i][1];i+=1;f()
        if t>53:
            unreal.unregister_slate_post_tick_callback(h)
            unreal.log('GATE2_GATE1_REGRESSION_DONE')
    except Exception as e:unreal.log_error('GATE2_REGRESSION_ERROR '+str(e));unreal.unregister_slate_post_tick_callback(h)
h=unreal.register_slate_post_tick_callback(tick)

