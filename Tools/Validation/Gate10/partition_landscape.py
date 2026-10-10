"""Supported native non-grid Landscape conversion on the new WNY map only."""
import unreal,time,json,gc,traceback,sys
from pathlib import Path
out=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate10Validation');started=time.time();phase=0;handle=None
def convert():
 assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level('/Game/Maps/WNY_PrototypeRegion')
 world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert unreal.RVWorldContentLibrary.set_region_authoring_loaded(world,True)
 result=dict(unreal.RVWorldContentLibrary.partition_region_landscape(world));assert result.get('Landscape parents')==1 and result.get('Terrain components')==256 and result.get('Streaming proxies',0)>0,result
 assert unreal.EditorLoadingAndSavingUtils.save_map(world,'/Game/Maps/WNY_PrototypeRegion');assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
 (out/'landscape-partition.json').write_text(json.dumps({'saved':True,'native_conversion':result,'heightfield':'retained, not regenerated','runtime_cell_floor_and_pcg_validation':'pending'},indent=2))
 assert unreal.RVWorldContentLibrary.set_region_authoring_loaded(world,False)
def tick(dt):
 global phase,handle
 if phase==0 and time.time()-started>5:
  phase=10
  try:convert()
  except Exception:
   (out/'landscape-partition-error.txt').write_text(traceback.format_exc())
   for k in ['last_traceback','last_value','last_type','last_exc']:
    if hasattr(sys,k):setattr(sys,k,None)
  gc.collect();phase=1
 elif phase==1:
  phase=2;unreal.unregister_slate_post_tick_callback(handle);handle=None;gc.collect();unreal.SystemLibrary.quit_editor()
handle=unreal.register_slate_post_tick_callback(tick)
