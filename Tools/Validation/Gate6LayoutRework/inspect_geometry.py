import unreal,json
from pathlib import Path
def inspect():
 w=next(a for a in unreal.ObjectIterator(unreal.World) if a.get_name()=='Gate6FuelElectricalTest' and 'UEDPIE_' in a.get_path_name())
 v=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSystemsMotorhome)[0]
 mesh=unreal.load_asset('/Game/RV/Meshes/SM_RV_Interior')
 points=unreal.RVInteriorMotorhome.inspect_art_surfaces(mesh)
 doors=[{'name':p.get_name(),'mesh':p.get_editor_property('StaticMesh').get_name(),'visible':p.is_visible(),'hidden':p.get_editor_property('bHiddenInGame')} for p in v.get_components_by_class(unreal.StaticMeshComponent) if p.get_editor_property('StaticMesh') and 'Door_Back' in p.get_editor_property('StaticMesh').get_name()]
 return {'horizontal_surfaces':[[p.x,p.y,p.z] for p in points],'transient_tracked_door':str(v.find_visual_part('Art_RV_Van_Door_Back')),'owned_original_doors':doors}
Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate6LayoutRework/interior-surfaces.json').write_text(json.dumps(inspect()),encoding='utf-8')
