import unreal,time,json,sys,os
sys.path.insert(0,'D:/GitHub/RVSurvival/RVSurvival/Saved/Gate3Validation')
from runner_runtime import load_runner
B='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate5Refinement/'
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level('/Game/Maps/Gate5SurvivalTest')
assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
s=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.LevelEditorPlaySettings'));s.set_editor_property('RunUnderOneProcess',True);s.set_editor_property('PlayNumberOfClients',1);s.set_editor_property('AdditionalLaunchParameters','')
n=s.get_editor_property('NetworkEmulationSettings');n.set_editor_property('bIsNetworkEmulationEnabled',False);s.set_editor_property('NetworkEmulationSettings',n)
unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings')).set_editor_property('bThrottleCPUWhenNotForeground',False)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
t=0;loaded=False;ending=None;start=time.time()
def tick(dt):
 global t,loaded,ending
 t+=dt
 if t>6 and not loaded:loaded=True;load_runner(B+'camera.py')
 if loaded and not ending and os.path.exists(B+'camera.json') and os.path.getmtime(B+'camera.json')>start:
  unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play();ending=time.time()+4
 if t>140 and not ending:unreal.log_error('REFINE_TIMEOUT');unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play();ending=time.time()+4
 if ending and time.time()>ending:
  unreal.unregister_slate_post_tick_callback(h);q=unreal.SystemLibrary.quit_editor
  from runner_runtime import release_runners
  release_runners();q()
h=unreal.register_slate_post_tick_callback(tick)
