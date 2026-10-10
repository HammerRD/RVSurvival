"""Align garage roadside trio to saved extended pad, then native PCG refresh."""
import unreal,time,json,gc,traceback,sys
from pathlib import Path
out=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate10Validation');start=time.time();phase=0;handle=None
def apply():
 levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert levels.load_level('/Game/Maps/WNY_PrototypeRegion')
 w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert unreal.RVWorldContentLibrary.set_region_authoring_loaded(w,True)
 actors={a.get_actor_label():a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()}
 land=next(a for a in actors.values() if isinstance(a,unreal.Landscape));assert land.actor_has_tag('WNYGarageApproachV2')
 rows=[]
 if not land.actor_has_tag('WNYGaragePropsV2'):
  car=actors['Abandoned trail vehicle 1'];delta=18-car.get_actor_location().z
  for label in ['Abandoned trail vehicle 1','Abandoned vehicle body collision 1','Trail vehicle cargo 1']:
   a=actors[label];a.modify();q=a.get_actor_location();a.set_actor_location(q+unreal.Vector(0,0,delta),False,False);rows.append({'label':label,'delta_z':delta})
  land.modify();land.tags=list(land.tags)+['WNYGaragePropsV2']
 assert levels.save_current_level() and unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
 assert unreal.RVWorldContentLibrary.set_region_authoring_loaded(w,False)
 (out/'garage-prop-alignment.json').write_text(json.dumps({'saved':True,'moved':rows},indent=2))
def tick(dt):
 global phase,handle
 if phase==0 and time.time()-start>5:
  phase=10
  try:apply()
  except Exception:
   (out/'garage-prop-alignment-error.txt').write_text(traceback.format_exc());phase=99
  for k in ['last_traceback','last_value','last_type','last_exc']:
   if hasattr(sys,k):setattr(sys,k,None)
  gc.collect()
  if phase!=99:phase=1
 elif phase in (1,99):
  okay=phase==1;unreal.unregister_slate_post_tick_callback(handle);handle=None;phase=2
  if okay:exec(compile(Path('D:/GitHub/RVSurvival/RVSurvival/Tools/Validation/Gate10/regenerate_loaded_biome.py').read_text(),'regenerate_loaded_biome.py','exec'),{})
  else:unreal.SystemLibrary.quit_editor()
handle=unreal.register_slate_post_tick_callback(tick)
