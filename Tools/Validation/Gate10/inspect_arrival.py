import unreal,json
from pathlib import Path
def inspect():
 w=next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='WNY_PrototypeRegion' and unreal.GameplayStatics.get_player_controller(w,0) and unreal.GameplayStatics.get_game_mode(w))
 pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn();gm=unreal.GameplayStatics.get_game_mode(w)
 vehicles=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVInteriorMotorhome)
 Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate10Validation/arrival-runtime.json').write_text(json.dumps({'mode':gm.get_class().get_name(),'parent':str(gm.get_class().get_super_class()) if hasattr(gm.get_class(),'get_super_class') else '', 'enabled':gm.get_editor_property('bArriveAtMobileBase'),'pawn':p.get_class().get_name(),'position':str(p.get_actor_location()),'vehicles':[{'tags':[str(t) for t in a.tags],'position':str(a.get_actor_location())} for a in vehicles]},indent=2))
inspect()
