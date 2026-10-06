import unreal,json
from runner_runtime import load_runner
B='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate5Refinement/'
def tick(dt):
 try:
  w=next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='Gate5SurvivalTest' and unreal.GameplayStatics.get_player_controller(w,0) and unreal.GameplayStatics.get_player_controller(w,0).get_controlled_pawn())
  chars=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSurvivorCharacter)
  if len(chars)!=2 or any(c.get_editor_property('PlayerState') is None for c in chars):return
  doors=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVExteriorStoragePoint)
  if len(doors)!=7 or any(str(a.get_editor_property('Container').get_editor_property('DisplayName'))=='Player storage' for a in doors):return
  if len(unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVInteriorAccessPoint))!=2:return
  s=json.load(open(B+'session.json'));json.dump({'id':s['id']},open(B+'ready.json','w'))
  if not s['start']:return
  unreal.unregister_slate_post_tick_callback(h);load_runner(B+'process.py')
 except (StopIteration,OSError,ValueError):return
h=unreal.register_slate_post_tick_callback(tick)
