import unreal,json
from pathlib import Path
def inspect():
 w=next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='WNY_PrototypeRegion' and unreal.GameplayStatics.get_game_mode(w) and unreal.GameplayStatics.get_player_controller(w,0));pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn();h=pc.player_state.get_component_by_class(unreal.RVHealthComponent)
 rows={'player_position':str(p.get_actor_location()),'life':str(h.life_state),'injuries':[{'kind':str(i.kind),'region':str(i.region),'severity':i.severity} for i in h.injuries],'infected':[{'position':str(a.get_actor_location()),'distance_cm':a.get_actor_location().distance(p.get_actor_location())} for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVInfected)]}
 Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate10Validation/return-downed-diagnosis.json').write_text(json.dumps(rows,indent=2))
inspect()
