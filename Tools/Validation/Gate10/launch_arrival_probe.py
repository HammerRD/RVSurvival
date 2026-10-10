"""Launch saved single-player map; scoped runner doesn't hold UObject wrappers."""
import unreal,time,runpy,traceback,json,gc
from pathlib import Path
out=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate10Validation');started=time.time();handle=None;loaded=False
runpy.run_path('D:/GitHub/RVSurvival/RVSurvival/Tools/Validation/Gate10/launch_manual.py')
def ready():
 for w in unreal.ObjectIterator(unreal.World):
  if w.get_name()=='WNY_PrototypeRegion' and unreal.GameplayStatics.get_game_mode(w):
   pc=unreal.GameplayStatics.get_player_controller(w,0)
   if pc and pc.get_controlled_pawn():return True
 return False
def tick(dt):
 global loaded,handle
 if not loaded and time.time()-started>15 and ready():
  loaded=True;unreal.unregister_slate_post_tick_callback(handle);handle=None
  try:runpy.run_path('D:/GitHub/RVSurvival/RVSurvival/Tools/Validation/Gate10/inspect_arrival.py')
  except Exception:(out/'arrival-launch-error.txt').write_text(traceback.format_exc())
  gc.collect()
handle=unreal.register_slate_post_tick_callback(tick)

