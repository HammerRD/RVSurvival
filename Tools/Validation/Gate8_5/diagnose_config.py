import unreal,json
from pathlib import Path
r={}
for path in ['/Game/Characters/RV/BP_RVHumanoid','/Game/Characters/RV/BP_Gate8_5GameMode']:
 c=unreal.EditorAssetLibrary.load_blueprint_class(path);o=unreal.get_default_object(c)
 if 'GameMode' in path:r[path]=str(o.get_editor_property('DefaultPawnClass'))
 else:
  v=o.get_component_by_class(unreal.RVCharacterPresentationComponent);r[path]=str(v.get_editor_property('Profile'))
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();r['world']=world.get_name();r['gm']=str(world.get_world_settings().get_editor_property('DefaultGameMode'))
Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate8_5Validation/config-diagnostic.json').write_text(json.dumps(r,indent=2))
unreal.SystemLibrary.quit_editor()
