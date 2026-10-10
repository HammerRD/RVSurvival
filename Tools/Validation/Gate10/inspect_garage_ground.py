"""Read only terrain transform and floor ray at the stalled garage approach."""
import unreal,json
from pathlib import Path
def inspect():
 w=next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='WNY_PrototypeRegion' and unreal.GameplayStatics.get_game_mode(w))
 pc=unreal.GameplayStatics.get_player_controller(w,0);v=pc.get_controlled_pawn();p=v.get_actor_location();rows=[]
 for dx,dy in [(0,0),(500,0),(-500,0),(0,500)]:
  x,y=p.x+dx,p.y+dy;hit=unreal.SystemLibrary.line_trace_single(w,unreal.Vector(x,y,3000),unreal.Vector(x,y,-4000),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,False,[v],unreal.DrawDebugTrace.NONE,True)
  rows.append({'xy':[x,y],'trace':str(hit)})
 lands=[{'class':a.get_class().get_name(),'transform':str(a.get_actor_transform()),'tags':[str(t) for t in a.tags]} for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.Landscape)]
 Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate10Validation/garage-runtime-ground.json').write_text(json.dumps({'vehicle_position':str(p),'landscape':lands,'rays':rows},indent=2))
inspect()
