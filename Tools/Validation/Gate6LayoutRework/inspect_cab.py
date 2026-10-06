"""Read-only live cab/ray inspection; all world references are function-scoped."""
import unreal,json
from pathlib import Path
def inspect():
 w=next(a for a in unreal.ObjectIterator(unreal.World) if a.get_name()=='Gate6FuelElectricalTest' and 'UEDPIE_' in a.get_path_name())
 pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn()
 rv=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSystemsMotorhome)[0]
 def local(point):
  q=rv.get_actor_transform().inverse_transform_location(point);return [q.x,q.y,q.z]
 camera=p.get_component_by_class(unreal.CameraComponent)
 capsule=p.get_component_by_class(unreal.CapsuleComponent)
 components=[]
 for c in rv.get_components_by_class(unreal.PrimitiveComponent):
  if any(s in c.get_name().lower() for s in ['cab','front','firewall','dash']):
   components.append({'name':c.get_name(),'center':local(c.get_world_location()),'bounds':str(unreal.SystemLibrary.get_component_bounds(c))})
 return {'camera':local(camera.get_world_location()),'capsule_radius':capsule.get_scaled_capsule_radius(),'capsule_half':capsule.get_scaled_capsule_half_height(),'components':components,'trace_api':unreal.SystemLibrary.line_trace_single.__doc__}
Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate6LayoutRework/cab-inspection.json').write_text(json.dumps(inspect(),indent=2),encoding='utf-8')
