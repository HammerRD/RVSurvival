"""Child readiness uses scoped reacquisition; no persistent UObject wrappers."""
import unreal,time,json,runpy,gc
from pathlib import Path
out=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate10Validation');handle=None
def tick(dt):
 global handle
 try:session=json.loads((out/'process-session.json').read_text())
 except (OSError,ValueError):return
 ready=False
 for w in unreal.ObjectIterator(unreal.World):
  if w.get_name()=='WNY_PrototypeRegion' and not unreal.GameplayStatics.get_game_mode(w):
   pc=unreal.GameplayStatics.get_player_controller(w,0)
   if pc and pc.get_controlled_pawn() and pc.get_controlled_pawn().player_state:ready=True
 if not ready:return
 (out/'process-ready.json').write_text(json.dumps({'id':session['id']}))
 if session.get('start'):
  unreal.unregister_slate_post_tick_callback(handle);handle=None
  runpy.run_path('D:/GitHub/RVSurvival/RVSurvival/Tools/Validation/Gate10/process_region.py');gc.collect()
handle=unreal.register_slate_post_tick_callback(tick)
