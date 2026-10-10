"""Scoped PIE diagnostics and initial RV-facing view. No persistent UObject globals."""
import unreal,json,gc,sys,traceback
from pathlib import Path

def inspect():
 world=next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='WNY_PrototypeRegion' and unreal.GameplayStatics.get_player_controller(w,0) and unreal.GameplayStatics.get_game_mode(w))
 pc=unreal.GameplayStatics.get_player_controller(world,0);pawn=pc.get_controlled_pawn()
 pc.set_control_rotation(unreal.Rotator(yaw=-90));unreal.SystemLibrary.execute_console_command(pc,'t.MaxFPS 60',pc)
 locations=[]
 for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.RVScavengeContainer):
  locations.append({'actor':a.get_name(),'items':len(a.container.get_items()),'searched':a.get_editor_property('bSearched')})
 zones=[{'actor':a.get_name(),'evaluated':a.get_editor_property('bEvaluated'),'outcome':str(a.outcome)} for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.RVRegionEncounterZone)]
 p=pawn.get_actor_location()
 record={'pawn_class':pawn.get_class().get_name(),'position':[p.x,p.y,p.z],'movement_mode':str(pawn.character_movement.movement_mode),'loaded_containers':locations,'zones':zones,'loot_lifecycle':dict(unreal.RVWorldContentLibrary.validate_loot_lifecycle(world,unreal.load_asset('/Game/World/WNY/Loot/DA_Medical')))}
 Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate10Validation/initial-pie-diagnostics.json').write_text(json.dumps(record,indent=2))
try:inspect()
except Exception:Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate10Validation/initial-pie-diagnostics-error.txt').write_text(traceback.format_exc())
finally:
 for name in ['last_traceback','last_value','last_type','last_exc']:
  if hasattr(sys,name):setattr(sys,name,None)
 gc.collect()

