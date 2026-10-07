import unreal,time,sys
from pathlib import Path
sys.path.insert(0,'D:/GitHub/RVSurvival/RVSurvival/Saved/Gate3Validation')
from runner_runtime import load_runner,release_runners
B=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate7Validation')
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level('/Game/Maps/Gate7MechanicalTest')
s=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.LevelEditorPlaySettings'));s.set_editor_property('PlayNumberOfClients',1);s.set_editor_property('RunUnderOneProcess',True);s.set_editor_property('AdditionalLaunchParameters','')
n=s.get_editor_property('NetworkEmulationSettings');n.set_editor_property('bIsNetworkEmulationEnabled',False);s.set_editor_property('NetworkEmulationSettings',n)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
started=time.time();loaded=False;ending=0
def tick(dt):
 global loaded,ending
 if not loaded and time.time()-started>6:
  loaded=True;load_runner('D:/GitHub/RVSurvival/RVSurvival/Tools/Validation/Gate7/single.py')
 if not ending and (B/'single.json').exists() and (B/'single.json').stat().st_mtime>started:
  release_runners();unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play();ending=time.time()+3
 if not ending and time.time()-started>120:
  unreal.log_error('GATE7_SINGLE_TIMEOUT');release_runners();unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play();ending=time.time()+3
 if ending and time.time()>ending:
  unreal.unregister_slate_post_tick_callback(h);assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True);unreal.SystemLibrary.quit_editor()
h=unreal.register_slate_post_tick_callback(tick)
