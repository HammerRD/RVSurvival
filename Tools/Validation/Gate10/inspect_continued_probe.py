"""Read scoped Python probe values; never retain Unreal object references."""
import gc,types,json
from pathlib import Path
def inspect():
 rows=[]
 for obj in gc.get_objects():
  if isinstance(obj,types.FunctionType) and obj.__name__=='tick' and obj.__code__.co_filename.endswith('continue_region_drive.py'):
   g=obj.__globals__;rows.append({'phase':g.get('phase'),'route_index':g.get('route_index'),'recent_samples':g.get('samples',[])[-5:],'held':g.get('held'),'distance':g.get('distance')})
 Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate10Validation/continued-probe-live.json').write_text(json.dumps(rows,indent=2))
inspect()
