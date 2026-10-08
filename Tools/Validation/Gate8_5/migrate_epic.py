"""Supported dependency-aware Unreal migration of installed Epic humanoid assets."""
import unreal,json
from pathlib import Path
root=Path('D:/GitHub/RVSurvival/RVSurvival');base='/Game/Characters/Mannequins'
packages=[base+'/Meshes/SKM_Manny_Simple',base+'/Anims/Unarmed/MM_Idle',base+'/Anims/Unarmed/Jump/MM_Jump',base+'/Anims/Unarmed/Jump/MM_Fall_Loop',base+'/Anims/Unarmed/Jump/MM_Land']
for gait in ['Walk','Jog']:
 for direction in ['Fwd','Bwd','Left','Right','Fwd_Left','Fwd_Right','Bwd_Left','Bwd_Right']:
  packages.append(base+'/Anims/Unarmed/'+gait+'/MF_Unarmed_'+gait+'_'+direction)
try:
 registry=unreal.AssetRegistryHelpers.get_asset_registry();registry.search_all_assets(True)
 assert all(unreal.load_asset(p) is not None for p in packages)
 unreal.AssetToolsHelpers.get_asset_tools().migrate_packages(packages,str(root/'Content'),unreal.MigrationOptions())
 files=sorted(str(p.relative_to(root)).replace('\\','/') for p in (root/'Content/Characters').rglob('*.uasset'))
 assert files
 (root/'Docs/Gate8_5Results/epic-migration.json').write_text(json.dumps({'source':'UE5.8 installed Characters shared template','requested_packages':packages,'migrated_files':files},indent=2))
finally:unreal.SystemLibrary.quit_editor()
