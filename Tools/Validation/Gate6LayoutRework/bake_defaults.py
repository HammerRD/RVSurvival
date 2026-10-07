"""Bake tested project-side configuration only. Current level is already loaded.
No world reload, no vendor asset writes; reacquire placed actors after Blueprint compile.
"""
import unreal,json
from pathlib import Path
def bake():
 levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
 assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
 actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
 rv=next(a for a in actors.get_all_level_actors() if isinstance(a,unreal.RVSystemsMotorhome))
 path='/Game/Vehicles/Gate6/BP_ClassCSystemsMotorhome'
 bp=unreal.load_asset(path);cdo=unreal.get_default_object(unreal.EditorAssetLibrary.load_blueprint_class(path))
 for prop in ['Stations','InteriorCollision','PowerPanelLocation']:
  cdo.set_editor_property(prop,rv.get_editor_property(prop))
 for prop in ['DinetteFrontSeat','DinetteRearSeat']:
  for field in ['bEnabled','RelativeLocation','StandingAisleLocation']:
   cdo.get_editor_property(prop).set_editor_property(field,rv.get_editor_property(prop).get_editor_property(field))
 unreal.BlueprintEditorLibrary.compile_blueprint(bp)
 assert unreal.EditorAssetLibrary.save_loaded_asset(bp,False)
 # Compile can replace the placed actor. Do not reuse its old wrapper.
 del rv,cdo,bp
 rv=next(a for a in actors.get_all_level_actors() if isinstance(a,unreal.RVSystemsMotorhome))
 rv.refresh_configuration()
 assert levels.save_current_level()
 assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
 return {'saved':True,'blueprint':path,'actor_count':len(actors.get_all_level_actors()),'stations':[str(d.name) for d in rv.get_editor_property('Stations')],'vendor_modified':False}
Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate6LayoutRework/defaults-baked.json').write_text(json.dumps(bake(),indent=2),encoding='utf-8')
unreal.SystemLibrary.quit_editor()
