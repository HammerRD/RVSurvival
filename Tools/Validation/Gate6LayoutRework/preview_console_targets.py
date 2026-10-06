"""In-place PIE authoring preview only; no player movement or gameplay RPC.
Persistent configuration is saved separately by configure_layout.py in a fresh editor.
"""
import unreal,json
from pathlib import Path
def preview():
 w=next(a for a in unreal.ObjectIterator(unreal.World) if a.get_name()=='Gate6FuelElectricalTest' and 'UEDPIE_' in a.get_path_name())
 for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVInteriorStation):
  name=str(a.get_editor_property('StationName'))
  if name in ['Navigation','Power']:a.set_actor_relative_location(unreal.Vector(224,0,141) if name=='Navigation' else unreal.Vector(224,14,126),False,True)
 for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVResourcePoint):
  if not a.get_editor_property('bFuelFill'):a.set_actor_relative_location(unreal.Vector(224,-14,126),False,True)
 return {'preview_only':True,'vendor_changes':False,'persistent_script':'configure_layout.py'}
Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate6LayoutRework/console-preview.json').write_text(json.dumps(preview()),encoding='utf-8')
