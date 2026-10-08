import unreal,json,gc
from pathlib import Path
folder='/Game/Characters/RV'
profile=unreal.load_asset(folder+'/DA_MannyPresentation')
bp=unreal.load_asset(folder+'/BP_RVHumanoid');c=unreal.EditorAssetLibrary.load_blueprint_class(folder+'/BP_RVHumanoid');o=unreal.get_default_object(c);v=o.get_editor_property('CharacterPresentation')
bp.modify();o.modify();v.modify();v.set_editor_property('Profile',profile)
assert unreal.EditorAssetLibrary.save_loaded_asset(bp,False)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert levels.load_level('/Game/Maps/Gate8_5CharacterTest')
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();settings=w.get_world_settings();settings.modify();settings.set_editor_property('DefaultGameMode',unreal.EditorAssetLibrary.load_blueprint_class(folder+'/BP_Gate8_5GameMode'))
assert unreal.EditorLoadingAndSavingUtils.save_map(w,'/Game/Maps/Gate8_5CharacterTest')
settings=None;w=None;v=None;o=None;c=None;bp=None;profile=None;gc.collect()
unreal.SystemLibrary.quit_editor()

