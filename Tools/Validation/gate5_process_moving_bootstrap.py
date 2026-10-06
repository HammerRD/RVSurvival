import unreal,json
from runner_runtime import load_runner
B='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate5Validation/'
def ready(dt):
 try:
  w=next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='Gate5SurvivalTest' and unreal.GameplayStatics.get_player_controller(w,0) and unreal.GameplayStatics.get_player_controller(w,0).get_controlled_pawn())
  if len(unreal.GameplayStatics.get_all_actors_of_class(w,unreal.load_class(None,'/Script/RVSurvival.RVSurvivorCharacter')))<2:return
  points=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.load_class(None,'/Script/RVSurvival.RVStoragePoint'))
  if len(points)!=7 or any(str(a.get_editor_property('Container').get_editor_property('DisplayName'))=='Player storage' for a in points):return
  stations=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.load_class(None,'/Script/RVSurvival.RVInteriorStation'))
  if len(stations)!=6 or {str(a.get_editor_property('StationName')) for a in stations}!={'Workbench','Medical','Kitchen','Storage','Power','Navigation'}:return
  characters=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSurvivorCharacter)
  if any(a.get_editor_property('PlayerState') is None for a in characters):return
  rest=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVRestPoint)
  if len(rest)!=2 or {str(a.get_editor_property('DisplayName')) for a in rest}!={'Rear bed','Dinette rest'}:return
  s=json.load(open(B+'process_session.json'));json.dump({'id':s['id']},open(B+'process_ready.json','w'))
  if not s.get('start'):return
  unreal.unregister_slate_post_tick_callback(h);load_runner(B+'process_moving.py')
 except (StopIteration,OSError,ValueError):return
h=unreal.register_slate_post_tick_callback(ready)


