"""Sequence scoped normal-input probes; leave PIE active for visual inspection."""
import unreal,time,runpy,json,traceback,gc
from pathlib import Path
root=Path('D:/GitHub/RVSurvival/RVSurvival');out=root/'Saved/Gate10Validation'
started=time.time();phase=0;handle=None;deadline=started+240
steps=[('normal-starting-supplies.json','guided_road_drive.py'),('guided-road-drive.json','armed_physical_gas_scavenge.py'),('armed-physical-gas-scavenge.json','normal_return_storage.py')]
runpy.run_path(str(root/'Tools/Validation/Gate10/launch_prepared_player.py'))
def tick(dt):
 global phase,handle,started
 try:
  if phase<len(steps):
   receipt,script=steps[phase];p=out/receipt
   if p.exists() and p.stat().st_mtime>started:
    data=json.loads(p.read_text());result=data.get('result','')
    if any(x in result for x in ['error','timeout','insufficient']):raise RuntimeError(result)
    phase+=1;started=time.time();runpy.run_path(str(root/'Tools/Validation/Gate10'/script))
  elif (out/'normal-return-storage.json').exists() and (out/'normal-return-storage.json').stat().st_mtime>started:
   unreal.unregister_slate_post_tick_callback(handle);handle=None;gc.collect()
  if handle and time.time()>deadline:raise RuntimeError('sequence deadline; inspect active probe')
 except Exception:
  (out/'graded-loop-sequence-error.txt').write_text(traceback.format_exc())
  unreal.unregister_slate_post_tick_callback(handle);handle=None;gc.collect()
handle=unreal.register_slate_post_tick_callback(tick)
