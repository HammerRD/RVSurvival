"""One final updated-world loop; preserve fresh receipts and leave PIE for visual review."""
import unreal,time,runpy,json,gc,traceback,sys
from pathlib import Path
root=Path('D:/GitHub/RVSurvival/RVSurvival');out=root/'Saved/Gate10Validation';started=time.time();deadline=started+950;phase=0;handle=None
steps=[('normal-starting-supplies.json','guided_road_drive.py'),('guided-road-drive.json','armed_physical_gas_scavenge.py'),('armed-physical-gas-scavenge.json','normal_return_storage.py'),('normal-return-storage.json','walk_and_store_food.py'),('normal-store-conservation.json','continue_region_drive.py')]
runpy.run_path(str(root/'Tools/Validation/Gate10/launch_prepared_player.py'))
def tick(dt):
 global phase,started,handle
 try:
  if phase<len(steps):
   receipt,script=steps[phase];p=out/receipt
   if p.exists() and p.stat().st_mtime>started:
    j=json.loads(p.read_text());result=j.get('result','')
    if any(v in result for v in ['error','timeout','insufficient']) or j.get('pass',True)==False:raise RuntimeError(result or 'conservation failed')
    phase+=1;started=time.time();runpy.run_path(str(root/'Tools/Validation/Gate10'/script))
  elif (out/'continued-region-drive.json').exists() and (out/'continued-region-drive.json').stat().st_mtime>started:
   unreal.unregister_slate_post_tick_callback(handle);handle=None;gc.collect()
  if handle and time.time()>deadline:raise RuntimeError('loop deadline; inspect current probe')
 except Exception:
  (out/'continued-loop-sequence-error.txt').write_text(traceback.format_exc());unreal.unregister_slate_post_tick_callback(handle);handle=None
  for k in ['last_traceback','last_value','last_type','last_exc']:
   if hasattr(sys,k):setattr(sys,k,None)
  gc.collect()
handle=unreal.register_slate_post_tick_callback(tick)
