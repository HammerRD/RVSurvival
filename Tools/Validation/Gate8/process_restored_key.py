"""Read-only bounded session for a real Windows F9 test after profile reload."""
import unreal,time,json,os
from pathlib import Path
B=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate8MechanicalRegression');s=json.loads((B/'session.json').read_text());start=s['start']
w=next(a for a in unreal.ObjectIterator(unreal.World) if a.get_name()=='Gate6FuelElectricalTest' and unreal.GameplayStatics.get_player_controller(a,0) and unreal.GameplayStatics.get_player_controller(a,0).get_controlled_pawn())
pc=unreal.GameplayStatics.get_player_controller(w,0);authority=unreal.GameplayStatics.get_game_mode(w) is not None;role='server' if authority else 'client'
def tick(dt):
 flag=B/'finish-restored-key.flag'
 if time.time()-start>100 or (flag.exists() and flag.stat().st_mtime>start):
  unreal.unregister_slate_post_tick_callback(handle)
  (B/(s['config']['name']+'_'+role+'.json')).write_text(json.dumps({'pid':os.getpid(),'role':role,'evidence_kind':'read-only session; actual Windows observation recorded separately','results':[]},indent=2))
handle=unreal.register_slate_post_tick_callback(tick)
