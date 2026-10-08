import unreal,json
from pathlib import Path
root=Path('D:/GitHub/RVSurvival/RVSurvival');base='/Game/Characters/Mannequins/Anims/Pistol'
packages=[base+'/Aim/AO_Pistol']+[base+'/'+n for n in ['MF_Pistol_Idle_ADS','MM_Pistol_Fire_Montage','MM_Pistol_Reload']]
for gait in ['Walk','Jog']:
 for direction in ['Fwd','Bwd','Left','Right','Fwd_Left','Fwd_Right','Bwd_Left','Bwd_Right']:
  packages.append(base+'/'+gait+'/MF_Pistol_'+gait+'_'+direction)
try:
 unreal.AssetRegistryHelpers.get_asset_registry().search_all_assets(True)
 assert all(unreal.load_asset(p) for p in packages)
 unreal.AssetToolsHelpers.get_asset_tools().migrate_packages(packages,str(root/'Content'),unreal.MigrationOptions())
 (root/'Docs/Gate9Results/epic-pistol-migration.json').write_text(json.dumps({'source':'installed UE5.8 Epic template','packages':packages},indent=2))
finally:unreal.SystemLibrary.quit_editor()
