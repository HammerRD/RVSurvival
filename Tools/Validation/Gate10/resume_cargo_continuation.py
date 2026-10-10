"""Resume the existing interrupted PIE at cargo; no completed drive/scavenge replay."""
import unreal,runpy,time,json,gc,traceback
from pathlib import Path
root=Path('D:/GitHub/RVSurvival/RVSurvival');out=root/'Saved/Gate10Validation';started=time.time();handle=None
runpy.run_path(str(root/'Tools/Validation/Gate10/walk_and_store_food.py'),init_globals={'close_inventory':False})
def tick(dt):
 global handle
 p=out/'normal-store-conservation.json'
 if p.exists() and p.stat().st_mtime>started:
  unreal.unregister_slate_post_tick_callback(handle);handle=None
  if not json.loads(p.read_text()).get('pass'):raise RuntimeError('Conservation failed; do not continue drive')
  runpy.run_path(str(root/'Tools/Validation/Gate10/continue_region_drive.py'));gc.collect()
 elif time.time()-started>45:
  unreal.unregister_slate_post_tick_callback(handle);handle=None
  (out/'resume-cargo-error.txt').write_text('No fresh conservation result; inspect the cargo approach before retry.');gc.collect()
handle=unreal.register_slate_post_tick_callback(tick)
