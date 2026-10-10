"""Native -game readiness rendezvous, without PIE package prefixes."""
import unreal,json,runpy,gc
from pathlib import Path
out=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate10Validation');handle=None

def ready_role():
 for w in unreal.ObjectIterator(unreal.World):
  if w.get_name()!='WNY_PrototypeRegion':continue
  pc=unreal.GameplayStatics.get_player_controller(w,0)
  if pc and pc.get_controlled_pawn() and pc.get_controlled_pawn().player_state:
   return 'server' if unreal.GameplayStatics.get_game_mode(w) else 'client'
 return None

def tick(dt):
 global handle
 try:session=json.loads((out/'process-session.json').read_text())
 except (OSError,ValueError):return
 role=ready_role()
 if not role:return
 (out/('standalone-ready-'+role+'.json')).write_text(json.dumps({'id':session['id']}))
 if session.get('start'):
  unreal.unregister_slate_post_tick_callback(handle);handle=None
  runpy.run_path('D:/GitHub/RVSurvival/RVSurvival/Tools/Validation/Gate10/process_region.py');gc.collect()
handle=unreal.register_slate_post_tick_callback(tick)
