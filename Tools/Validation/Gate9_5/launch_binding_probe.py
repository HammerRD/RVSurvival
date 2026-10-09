"""One-player pose development; safe runner release before PIE ends."""
import unreal,time,json,sys
from pathlib import Path
sys.path.insert(0,'D:/GitHub/RVSurvival/RVSurvival/Saved/Gate3Validation')
from runner_runtime import load_runner,release_runners
B=Path('D:/GitHub/RVSurvival/RVSurvival/Docs/Gate9_5Results')
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level('/Game/Maps/Gate9_5CombatRefinementTest')
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
s=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.LevelEditorPlaySettings'));s.set_editor_property('RunUnderOneProcess',True);s.set_editor_property('PlayNumberOfClients',1);s.set_editor_property('AdditionalLaunchParameters','')
n=s.get_editor_property('NetworkEmulationSettings');n.set_editor_property('bIsNetworkEmulationEnabled',False);s.set_editor_property('NetworkEmulationSettings',n)
unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings')).set_editor_property('bThrottleCPUWhenNotForeground',False)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
started=time.time();loaded=False;ending=None
def tick(dt):
 global loaded,ending
 if not loaded and time.time()-started>4:
  worlds=[w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='Gate9_5CombatRefinementTest' and unreal.GameplayStatics.get_player_controller(w,0) and unreal.GameplayStatics.get_player_controller(w,0).get_controlled_pawn()]
  if worlds:
   loaded=True;worlds=None
   try:load_runner('D:/GitHub/RVSurvival/RVSurvival/Tools/Validation/Gate9_5/binding_label_probe.py')
   except Exception:
    import traceback;traceback.print_exc();release_runners();unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play();ending=time.time()+4
  worlds=None
 if loaded and not ending and (B/'binding-label-probe.json').exists() and (B/'binding-label-probe.json').stat().st_mtime>started:
  release_runners();unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play();ending=time.time()+4
 if not ending and time.time()-started>100:
  release_runners();unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play();ending=time.time()+4
 if ending and time.time()>ending:
  unreal.unregister_slate_post_tick_callback(handle);release_runners();unreal.SystemLibrary.quit_editor()
handle=unreal.register_slate_post_tick_callback(tick)

