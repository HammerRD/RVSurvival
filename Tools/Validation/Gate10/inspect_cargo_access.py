import unreal,json,gc,sys
from pathlib import Path
def inspect():
 w=next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='WNY_PrototypeRegion' and unreal.GameplayStatics.get_game_mode(w))
 pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn();v=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVInteriorMotorhome)[0]
 rows=[]
 for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVExteriorStoragePoint):
  q=a.get_actor_location();ray=unreal.SystemLibrary.line_trace_single(w,p.get_actor_eyes_view_point()[0],q,unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,False,[p],unreal.DrawDebugTrace.NONE,True)
  hit=ray.to_tuple() if ray else None
  rows.append({'name':a.get_name(),'label':str(a.container.display_name),'location':str(q),'local':str(v.get_actor_transform().inverse_transform_location(q)),'distance':q.distance(p.get_actor_eyes_view_point()[0]),'hit_actor':hit[9].get_name() if hit and hit[9] else '', 'hit_component':hit[10].get_name() if hit and hit[10] else '', 'contents':[unreal.GuidLibrary.conv_guid_to_string(i.id) for i in a.container.get_items()]})
 i=p.get_component_by_class(unreal.RVInventoryComponent)
 Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate10Validation/cargo-access.json').write_text(json.dumps({'player':str(p.get_actor_location()),'feedback':i.feedback,'rows':rows},indent=2))
inspect()
for k in ['last_traceback','last_value','last_type','last_exc']:
 if hasattr(sys,k):setattr(sys,k,None)
gc.collect()
