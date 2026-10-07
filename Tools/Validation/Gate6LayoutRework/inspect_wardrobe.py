"""Read-only vendor mesh vertices; no level load or asset mutation."""
import unreal,json
from pathlib import Path
def inspect():
 regions={
  'wardrobe':((-160,-125,155),(-60,-40,320)),
  'rear_cushion':((-100,-120,110),(-30,-40,165)),
 }
 return {meshname+'_'+name:[[p.x,p.y,p.z] for p in unreal.RVInteriorMotorhome.inspect_art_vertices(unreal.load_asset('/Game/RV/Meshes/'+meshname),unreal.Vector(*bounds[0]),unreal.Vector(*bounds[1]))] for meshname in ['SM_RV_Interior','SM_RV_Van'] for name,bounds in regions.items()}
Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate6LayoutRework/wardrobe-vertices.json').write_text(json.dumps(inspect()),encoding='utf-8')
unreal.SystemLibrary.quit_editor()
