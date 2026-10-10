import unreal,json,gc,sys
from pathlib import Path
out=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate10Validation')
def inspect():
 w=next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='WNY_PrototypeRegion' and unreal.GameplayStatics.get_game_mode(w));p=unreal.GameplayStatics.get_player_controller(w,0).get_controlled_pawn();inv=p.get_component_by_class(unreal.RVInventoryComponent)
 def items(c):return [{'id':unreal.GuidLibrary.conv_guid_to_string(i.id),'quantity':i.quantity,'condition':i.condition} for i in c.get_items()]
 before=json.loads((out/'normal-return-storage.json').read_text())['samples'][0]['items'];food=next(x for x in before if x['condition']<1)
 cargo=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVExteriorStoragePoint)[0];a=items(inv);b=items(cargo.container)
 (out/'normal-store-conservation.json').write_text(json.dumps({'pass':food in b and all(x['id']!=food['id'] for x in a),'evidence':'normal E/W/LMB/Tab/Down/T driven gas loop; transfer required perpendicular compartment approach','original_food':food,'player_after':a,'cargo_after':b,'feedback':inv.feedback},indent=2))
inspect()
for k in ['last_traceback','last_value','last_type','last_exc']:
 if hasattr(sys,k):setattr(sys,k,None)
gc.collect()
