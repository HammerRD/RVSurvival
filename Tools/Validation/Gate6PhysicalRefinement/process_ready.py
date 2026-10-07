import unreal,json
from runner_runtime import load_runner
B='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate6PhysicalRefinement/'
def tick(dt):
 try:
  w=next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='Gate6FuelElectricalTest' and unreal.GameplayStatics.get_player_controller(w,0) and unreal.GameplayStatics.get_player_controller(w,0).get_controlled_pawn())
  chars=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSurvivorCharacter)
  if len(chars)!=2 or any(c.get_editor_property('PlayerState') is None for c in chars):return
  doors=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVExteriorStoragePoint)
  if len(doors)!=7 or any(str(a.get_editor_property('Container').get_editor_property('DisplayName'))=='Player storage' for a in doors):return
  if len(unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVResourcePoint))!=2:return
  vehicles=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSystemsMotorhome)
  if len(vehicles)!=1:return
  house=vehicles[0].get_editor_property('HouseDoor')
  if house is None or house.get_editor_property('DoorMesh') is None:return
  entries=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVVehicleEntryPoint)
  if len(entries)<4 or any(a.get_editor_property('Seat') is None for a in entries):return
  s=json.load(open(B+'session.json'));json.dump({'id':s['id']},open(B+'ready.json','w'))
  if not s['start']:return
  unreal.unregister_slate_post_tick_callback(h);load_runner(B+'process_refinement.py')
 except (StopIteration,OSError,ValueError):return
h=unreal.register_slate_post_tick_callback(tick)


