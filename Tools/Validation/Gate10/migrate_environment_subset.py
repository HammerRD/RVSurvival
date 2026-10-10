"""Run in a read-only-content audit project; native AssetTools migrates dependencies."""
import unreal,json,traceback,hashlib
from pathlib import Path
root=Path('D:/GitHub/RVSurvival/RVSurvival');out=root/'Saved/Gate10Validation'
source=Path('D:/Epic Games/Samples/ElectricDreamsEnv/Content')
seeds=[
 '/Game/Megascans/3D_Plants/EuropeanHornbeam/Geometry/SimpleWind/SM_EuropeanHornbeam_Field_01',
 '/Game/Megascans/3D_Plants/EuropeanHornbeam/Geometry/SimpleWind/SM_EuropeanHornbeam_Forest_01',
 '/Game/Megascans/3D_Plants/EuropeanHornbeam/Geometry/SimpleWind/SM_EuropeanHornbeam_Sapling_01',
 '/Game/Megascans/3D_Plants/BeechFern/SM_BeechFern_01',
 '/Game/Megascans/3D_Assets/ForestRockSlab/SM_ForestRockSlab_01']
try:
 registry=unreal.AssetRegistryHelpers.get_asset_registry();registry.search_all_assets(True)
 closure=set(seeds);queue=list(seeds)
 options=unreal.AssetRegistryDependencyOptions(include_hard_package_references=True,include_soft_package_references=True)
 while queue:
  for dep in registry.get_dependencies(queue.pop(),options):
   dep=str(dep)
   if dep.startswith('/Game/') and dep not in closure:closure.add(dep);queue.append(dep)
 files=[]
 for package in sorted(closure):
  f=source/(package[6:]+'.uasset')
  if not f.exists():raise RuntimeError('Missing sample dependency '+package)
  files.append({'package':package,'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
 assert sum(f['bytes'] for f in files)<2*1024**3,'Subset exceeded 2GiB review budget'
 (out/'environment-migration-plan.json').write_text(json.dumps({'seeds':seeds,'files':files},indent=2))
 migration=unreal.MigrationOptions();migration.set_editor_property('prompt',False)
 migration.set_editor_property('asset_conflict',unreal.AssetMigrationConflict.SKIP)
 unreal.AssetToolsHelpers.get_asset_tools().migrate_packages(seeds,str(root/'Content'),migration)
 for entry in files:
  f=root/'Content'/(entry['package'][6:]+'.uasset')
  assert f.exists(),str(f)
  original=source/(entry['package'][6:]+'.uasset')
  assert hashlib.sha256(original.read_bytes()).hexdigest()==entry['sha256'],'Source changed'
 (out/'environment-migration.json').write_text(json.dumps({'migrated':True,'seeds':seeds,'package_count':len(files),'bytes':sum(f['bytes'] for f in files),'source_unchanged':True},indent=2))
except Exception:
 (out/'environment-migration-error.txt').write_text(traceback.format_exc());traceback.print_exc()
