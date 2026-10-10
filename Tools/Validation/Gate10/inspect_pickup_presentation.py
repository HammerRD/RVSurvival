import unreal,json,sys,gc
from pathlib import Path
def inspect():
 w=next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='WNY_PrototypeRegion' and unreal.GameplayStatics.get_game_mode(w) and unreal.GameplayStatics.get_player_controller(w,0));pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn();rows=[]
 for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVWorldItem):
  if a.get_actor_location().distance(p.get_actor_location())>3000:continue
  mesh=a.get_component_by_class(unreal.StaticMeshComponent);origin,extent,radius=unreal.SystemLibrary.get_component_bounds(mesh)
  rows.append({'definition':a.item.definition.get_path_name(),'pivot':str(a.get_actor_location()),'bounds':str(origin),'extent':str(extent),'collision':str(mesh.get_collision_enabled()),'simple_collision_count':unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem).get_simple_collision_count(mesh.get_editor_property('StaticMesh'))})
 inv=p.get_component_by_class(unreal.RVInventoryComponent);i=p.get_component_by_class(unreal.RVInteractionComponent)
 Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate10Validation/pickup-presentation-diagnosis.json').write_text(json.dumps({'trace':i.debug_trace_description(),'prompt':str(i.get_prompt()),'feedback':inv.feedback,'meshes':rows},indent=2))
for name in ['last_traceback','last_value','last_type','last_exc']:
 if hasattr(sys,name):setattr(sys,name,None)
gc.collect()
try:inspect()
finally:
 for name in ['last_traceback','last_value','last_type','last_exc']:
  if hasattr(sys,name):setattr(sys,name,None)
 gc.collect()

