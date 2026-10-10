"""Open one-player PIE on the saved regraded region without saving anything, then run the normal-input route drive."""
import unreal,time,json,runpy,traceback,gc,sys
from pathlib import Path
root=Path('D:/GitHub/RVSurvival/RVSurvival');out=root/'Saved/Gate10Validation';started=time.time();phase=0;handle=None
def ready():
 for w in unreal.ObjectIterator(unreal.World):
  if w.get_name()=='WNY_PrototypeRegion' and unreal.GameplayStatics.get_game_mode(w):
   pc=unreal.GameplayStatics.get_player_controller(w,0)
   if pc and pc.get_controlled_pawn():return True
 return False
def launch():
 assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level('/Game/Maps/WNY_PrototypeRegion')
 settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.LevelEditorPlaySettings'));settings.set_editor_property('RunUnderOneProcess',True);settings.set_editor_property('PlayNumberOfClients',1);settings.set_editor_property('AdditionalLaunchParameters','')
 network=settings.get_editor_property('NetworkEmulationSettings');network.set_editor_property('bIsNetworkEmulationEnabled',False);settings.set_editor_property('NetworkEmulationSettings',network);settings=None;network=None
 unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings')).set_editor_property('bThrottleCPUWhenNotForeground',False)
 unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
def tick(dt):
 global phase,handle
 try:
  if phase==0 and time.time()-started>5:phase=10;launch();phase=1
  elif phase==1 and time.time()-started>25 and ready():
   phase=2;unreal.unregister_slate_post_tick_callback(handle);handle=None;gc.collect()
   runpy.run_path(str(root/'Tools/Validation/Gate10/regraded_route_drive.py'))
  elif phase==1 and time.time()-started>180:raise RuntimeError('PIE player not ready')
 except Exception:
  (out/'regraded-route-launch-error.txt').write_text(traceback.format_exc())
  if handle:unreal.unregister_slate_post_tick_callback(handle);handle=None
  for k in ['last_traceback','last_value','last_type','last_exc']:
   if hasattr(sys,k):setattr(sys,k,None)
  gc.collect()
handle=unreal.register_slate_post_tick_callback(tick)
