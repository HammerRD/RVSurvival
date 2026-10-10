"""Bounded editor-generated native partitioned PCG; no world reload cleanup."""
import unreal,json,time,gc,traceback
from pathlib import Path
root=Path('D:/GitHub/RVSurvival/RVSurvival');out=root/'Saved/Gate10Validation'
started=time.time();handle=None

def configure():
 levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
 assert levels.load_level('/Game/Maps/WNY_PrototypeRegion')
 actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
 if any(a.actor_has_tag('WNYBiomeMilestone') for a in actors.get_all_level_actors()):
  raise RuntimeError('Biome milestone already exists: inspect saved state')
 trees=[unreal.load_asset('/Game/Megascans/3D_Plants/EuropeanHornbeam/Geometry/SimpleWind/SM_EuropeanHornbeam_'+name) for name in ['Field_01','Forest_01','Sapling_01']]
 fern=unreal.load_asset('/Game/Megascans/3D_Plants/BeechFern/SM_BeechFern_01')
 rock=unreal.load_asset('/Game/Megascans/3D_Assets/ForestRockSlab/SM_ForestRockSlab_01')
 assert all(trees) and fern and rock
 graphs=[unreal.RVWorldContentLibrary.create_biome_graph('/Game/World/WNY/PCG/PCG_Deciduous',trees,.002,True),
  unreal.RVWorldContentLibrary.create_biome_graph('/Game/World/WNY/PCG/PCG_Undergrowth',[fern],.01,False),
  unreal.RVWorldContentLibrary.create_biome_graph('/Game/World/WNY/PCG/PCG_Rocks',[rock],.00015,True)]
 assert all(graphs)
 for graph in graphs:assert unreal.EditorAssetLibrary.save_loaded_asset(graph)
 for index,x in enumerate(range(-160000,160001,20000)):
  for side,y in enumerate([-17000,85000]):
   for layer,graph in enumerate(graphs):
    patch=actors.spawn_actor_from_class(unreal.RVBiomePatch,unreal.Vector(x,y,0))
    patch.set_actor_label('WNY %s %02d %d'%(['deciduous','undergrowth','rocks'][layer],index,side))
    patch.tags=['WNYBiomeMilestone'];patch.get_editor_property('bounds').set_box_extent(unreal.Vector(8000,5000,20000))
    component=patch.get_editor_property('dressing');component.set_editor_property('seed',1977+index*31+side*7+layer)
    component.set_graph(graph)
 assert levels.save_current_level() and unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
 for patch in actors.get_all_level_actors():
  if isinstance(patch,unreal.RVBiomePatch):patch.get_editor_property('dressing').generate(True)

def finish(error=None):
 global handle
 if handle is not None:unreal.unregister_slate_post_tick_callback(handle);handle=None
 try:
  levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
  world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
  stats=dict(unreal.RVWorldContentLibrary.get_dressing_stats(world))
  assert levels.save_current_level() and unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
  (out/'biome-generation.json').write_text(json.dumps({'saved':True,'stats':stats,'error':error,'elapsed_s':time.time()-started},indent=2))
 finally:gc.collect();unreal.SystemLibrary.quit_editor()

def tick(delta):
 try:
  world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
  stats=dict(unreal.RVWorldContentLibrary.get_dressing_stats(world));world=None
  if time.time()-started>20 and stats['Pending']==0 and stats['Instances']>0:finish()
  elif time.time()-started>240:finish('Generation timeout; do not count as acceptance')
 except Exception:finish(traceback.format_exc())

try:configure();handle=unreal.register_slate_post_tick_callback(tick)
except Exception:
 (out/'biome-generation-error.txt').write_text(traceback.format_exc());traceback.print_exc();finish(traceback.format_exc())
