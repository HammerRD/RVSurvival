import unreal,json
from runner_runtime import load_runner
B='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate4Validation/'
def ready(dt):
 try:
  w=next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='Gate4InventoryTest' and unreal.GameplayStatics.get_player_controller(w,0) and unreal.GameplayStatics.get_player_controller(w,0).get_controlled_pawn())
  if len(unreal.GameplayStatics.get_all_actors_of_class(w,unreal.load_class(None,'/Script/RVSurvival.RVSurvivorCharacter')))<2:return
  points=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.load_class(None,'/Script/RVSurvival.RVStoragePoint'))
  if len(points)!=6 or any(str(a.get_editor_property('Container').get_editor_property('DisplayName'))=='Player storage' for a in points):return
  s=json.load(open(B+'process_session.json'));json.dump({'id':s['id']},open(B+'process_ready.json','w'))
  if not s.get('start'):return
  unreal.unregister_slate_post_tick_callback(h);load_runner(B+'process_moving.py')
 except (StopIteration,OSError,ValueError):return
h=unreal.register_slate_post_tick_callback(ready)

