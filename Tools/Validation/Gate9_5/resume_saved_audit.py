"""Saved-state audit and native timed fixture; project-side map only."""
import unreal,json,gc,traceback
from pathlib import Path
root=Path('D:/GitHub/RVSurvival/RVSurvival');out=root/'Docs/Gate9_5Results'
def run():
 levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert levels.load_level('/Game/Maps/Gate9_5CombatRefinementTest');actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
 counter=next((a for a in actors.get_all_level_actors() if a.get_actor_label()=='Gate9_5TimedCounter'),None)
 if not counter:
  counter=actors.spawn_actor_from_class(unreal.RVTestInteractable,unreal.Vector(-1600,600,120));counter.set_actor_label('Gate9_5TimedCounter');counter.get_component_by_class(unreal.StaticMeshComponent).set_mobility(unreal.ComponentMobility.MOVABLE);counter.set_actor_scale3d(unreal.Vector(.3,.3,.3))
 heavy=[]
 for path in unreal.EditorAssetLibrary.list_assets('/Game/Items',True,False):
  d=unreal.load_asset(path)
  if isinstance(d,unreal.RVItemDefinition) and d.get_editor_property('bRequiresPhysicalCarry'):
   d.modify();d.set_editor_property('PickupSeconds',.5);assert unreal.EditorAssetLibrary.save_loaded_asset(d,False);heavy.append(path)
 assets=[]
 for folder in ['/Game/Combat/Gate9_5','/Game/Characters/RV/Gate9_5','/Game/ThirdParty/Xeradev/M1911','/Game/ThirdParty/RED2000/Crowbar']:
  for path in unreal.EditorAssetLibrary.list_assets(folder,True,False):
   a=unreal.load_asset(path);assert a,path;assets.append(path)
 for name in ['NonRigged_M1911','NonRigged_M1911_Magazine']:
  mesh=unreal.load_asset('/Game/ThirdParty/Xeradev/M1911/'+name);task=unreal.AssetExportTask();task.object=mesh;task.filename=str(root/'Saved/Gate9_5Assets'/f'{name}.obj');task.automated=True;task.prompt=False;task.replace_identical=True;task.exporter=unreal.StaticMeshExporterOBJ();unreal.Exporter.run_asset_export_task(task)
 assert levels.save_current_level()
 return {'assets_load':assets,'heavy_hold_definitions':heavy,'map_saved':True,'timed_fixture':'Gate9_5TimedCounter'}
try:(out/'resume-saved-audit.json').write_text(json.dumps(run(),indent=2))
except Exception:(out/'resume-saved-audit-error.txt').write_text(traceback.format_exc());traceback.print_exc()
finally:gc.collect();unreal.SystemLibrary.quit_editor()
