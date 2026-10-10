import unreal,json,sys,gc,traceback
from pathlib import Path
def inspect():
 w=next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='WNY_PrototypeRegion' and unreal.GameplayStatics.get_game_mode(w) and unreal.GameplayStatics.get_player_controller(w,0));pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn();eye=p.get_actor_eyes_view_point()[0];rows=[]
 for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVInfected):
  mesh=a.get_component_by_class(unreal.SkeletalMeshComponent);r={'actor':a.get_name(),'profile':a.profile.get_path_name(),'vitality':a.vitality,'position':str(a.get_actor_location()),'head':str(mesh.get_socket_location('head')),'collision':str(mesh.get_collision_enabled()),'rays':[]}
  for name,target in [('head',mesh.get_socket_location('head')),('torso',a.get_actor_location()+unreal.Vector(0,0,20))]:
   result=unreal.SystemLibrary.line_trace_single(w,eye,target,unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[p],unreal.DrawDebugTrace.NONE,True)
   hit=result if isinstance(result,unreal.HitResult) else next((v for v in result if isinstance(v,unreal.HitResult)),None) if isinstance(result,tuple) else None
   r['rays'].append({'target':name,'result':str(hit.to_tuple()) if hit else str(result)})
  rows.append(r)
 Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate10Validation/infected-trace-diagnosis.json').write_text(json.dumps(rows,indent=2))
try:inspect()
except Exception:Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate10Validation/infected-trace-error.txt').write_text(traceback.format_exc())
finally:
 for name in ['last_traceback','last_value','last_type','last_exc']:
  if hasattr(sys,name):setattr(sys,name,None)
 gc.collect()


