import unreal,time,json,os
from runner_runtime import load_runner
B='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate5Validation/'
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level('/Game/Maps/Gate5SurvivalTest')
s=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.LevelEditorPlaySettings'))
s.set_editor_property('RunUnderOneProcess',True);s.set_editor_property('PlayNumberOfClients',1);s.set_editor_property('AdditionalLaunchParameters','')
n=s.get_editor_property('NetworkEmulationSettings');n.set_editor_property('bIsNetworkEmulationEnabled',False);s.set_editor_property('NetworkEmulationSettings',n)
unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings')).set_editor_property('bThrottleCPUWhenNotForeground',False)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
t=0;loaded=False;ending=None;started=time.time()
def tick(dt):
 global t,loaded,ending
 t+=dt
 if t>6 and not loaded:
  loaded=True;load_runner(B+'stress_suite.py')
 p=B+'stress.json'
 if loaded and not ending and os.path.exists(p) and os.path.getmtime(p)>started:
  unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play();ending=time.time()+4
 if ending and time.time()>ending:
  unreal.unregister_slate_post_tick_callback(h)
  quit=unreal.SystemLibrary.quit_editor
  from runner_runtime import release_runners
  release_runners();quit()
h=unreal.register_slate_post_tick_callback(tick)

