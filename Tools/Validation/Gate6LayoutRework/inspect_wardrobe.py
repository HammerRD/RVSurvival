"""Read-only vendor mesh vertices; no level load or asset mutation."""
import unreal,json
from pathlib import Path
def inspect():
 mesh=unreal.load_asset('/Game/RV/Meshes/SM_RV_Interior')
 regions={
  'wardrobe':((-160,-125,155),(-60,-40,320)),
  'rear_cushion':((-100,-120,120),(-30,-40,145)),
 }
 return {name:[[p.x,p.y,p.z] for p in unreal.RVInteriorMotorhome.inspect_art_vertices(mesh,unreal.Vector(*bounds[0]),unreal.Vector(*bounds[1]))] for name,bounds in regions.items()}
Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate6LayoutRework/wardrobe-vertices.json').write_text(json.dumps(inspect()),encoding='utf-8')
unreal.SystemLibrary.quit_editor()
