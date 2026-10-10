"""Create and save a native World Partition/Landscape seed. No PIE or reload loop."""
import unreal, json, gc, traceback
from pathlib import Path
ROOT=Path('D:/GitHub/RVSurvival/RVSurvival')
OUT=ROOT/'Saved/Gate10Validation';OUT.mkdir(parents=True,exist_ok=True)

def build():
    levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    assets=unreal.EditorAssetLibrary
    destination='/Game/Maps/WNY_PrototypeRegion'
    if assets.does_asset_exist(destination):
        raise RuntimeError('Region already exists: inspect saved checkpoint; do not overwrite')
    world=unreal.EditorLoadingAndSavingUtils.new_map_from_template('/Engine/Maps/Templates/OpenWorld',True)
    assert world
    assert unreal.EditorLoadingAndSavingUtils.save_map(world,destination)
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    # Remove only the template landscape in this newly saved project-side seed.
    template_terrain=[a for a in actors.get_all_level_actors() if isinstance(a,unreal.LandscapeProxy)]
    for actor in template_terrain:actors.destroy_actor(actor)
    template_terrain=None;actor=None
    terrain=unreal.RVWorldContentLibrary.create_region_landscape(world,16,400.)
    assert terrain
    assert levels.save_current_level()
    assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    return {'map':destination,'terrain_span_m':4032,'components_per_axis':16,'vertex_spacing_cm':400,'saved':True,'acceptance':'IN PROGRESS; no playable-loop validation yet'}

try:(OUT/'world-foundation.json').write_text(json.dumps(build(),indent=2))
except Exception:
    (OUT/'world-foundation-error.txt').write_text(traceback.format_exc());traceback.print_exc()
finally:
    gc.collect();unreal.SystemLibrary.quit_editor()
