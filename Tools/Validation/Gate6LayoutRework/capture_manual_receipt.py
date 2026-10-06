"""Supplementary read-only snapshot after visual/native-control audit, not a substitute for it."""
import unreal,json
from pathlib import Path
def capture():
 w=next(a for a in unreal.ObjectIterator(unreal.World) if a.get_name()=='Gate6FuelElectricalTest' and 'UEDPIE_' in a.get_path_name())
 pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn()
 rv=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSystemsMotorhome)[0]
 def local(a):
  q=rv.get_actor_transform().inverse_transform_location(a.get_actor_location());return [q.x,q.y,q.z]
 storage=[]
 for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVStoragePoint):
  if isinstance(a,unreal.RVExteriorStoragePoint):continue
  c=a.get_editor_property('Container')
  storage.append({'name':str(c.get_editor_property('DisplayName')),'local':local(a),'kg':c.get_editor_property('MaxWeightKg'),'litres':c.get_editor_property('MaxVolumeLitres')})
 stations=[{'name':str(a.get_editor_property('StationName')),'local':local(a),'completed':a.get_editor_property('InteractionCount')} for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVInteriorStation)]
 originals=[{'name':c.get_name(),'visible':c.is_visible(),'hidden':c.get_editor_property('bHiddenInGame')} for c in rv.get_components_by_class(unreal.StaticMeshComponent) if c.get_editor_property('StaticMesh') and 'Door_Back' in c.get_editor_property('StaticMesh').get_name()]
 return {'visual_audit_required':True,'stations':stations,'storage':storage,'original_door_parts':originals,'house_door_open':rv.get_editor_property('HouseDoor').get_editor_property('bOpen'),'player':local(p),'mode':str(p.get_component_by_class(unreal.CharacterMovementComponent).get_editor_property('MovementMode')),'capsule':str(p.get_component_by_class(unreal.CapsuleComponent).get_collision_enabled())}
Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate6LayoutRework/manual-spatial-receipt.json').write_text(json.dumps(capture(),indent=2),encoding='utf-8')
