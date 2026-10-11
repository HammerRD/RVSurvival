"""Gate 10 closure: one-player PIE (no save), RV streaming-prewarm timing, uncapped frame-time sample, native encounter bookkeeping validation, then stop PIE and quit."""
import unreal,time,json,gc,sys,traceback
from pathlib import Path
out=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate10Validation');docs=Path('D:/GitHub/RVSurvival/RVSurvival/Docs/Gate10Results')
started=time.time();phase=0;handle=None;receipt={'evidence':'one-player PIE on the saved WNY map; no map or asset save'};frames=[];marks={}
def pie_world():
 for w in unreal.ObjectIterator(unreal.World):
  if w.get_name()=='WNY_PrototypeRegion' and unreal.GameplayStatics.get_game_mode(w):return w
 return None
def ready(w):
 pc=unreal.GameplayStatics.get_player_controller(w,0) if w else None
 return bool(pc and pc.get_controlled_pawn())
def streaming(w):
 # World Partition cells are not exposed to Python; streamed-in actors and landscape proxies show the prewarm instead.
 return {'loaded':len(unreal.GameplayStatics.get_all_actors_of_class(w,unreal.Actor)),'landscape_proxies':len(unreal.GameplayStatics.get_all_actors_of_class(w,unreal.LandscapeStreamingProxy))}
def finish():
 global handle
 receipt['frame_ms']=None
 if frames:
  s=sorted(frames);receipt['frame_ms']={'samples':len(s),'median':round(s[len(s)//2],2),'p95':round(s[int(len(s)*.95)],2),'p99':round(s[int(len(s)*.99)],2),'max':round(s[-1],2),'mean':round(sum(s)/len(s),2)}
 (out/'closure-checks.json').write_text(json.dumps(receipt,indent=2));docs.joinpath('closure-checks.json').write_text(json.dumps(receipt,indent=2))
 for k in ['last_traceback','last_value','last_type','last_exc']:
  if hasattr(sys,k):setattr(sys,k,None)
 gc.collect()
def tick(dt):
 global phase,handle
 try:
  t=time.time()-started
  if phase==0 and t>5:
   phase=10;assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level('/Game/Maps/WNY_PrototypeRegion')
   settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.LevelEditorPlaySettings'));settings.set_editor_property('RunUnderOneProcess',True);settings.set_editor_property('PlayNumberOfClients',1);settings=None
   unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings')).set_editor_property('bThrottleCPUWhenNotForeground',False)
   marks['begin_play_request']=time.time();unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play();phase=1
  elif phase==1:
   w=pie_world()
   if w and 'world' not in marks:marks['world']=time.time()
   if ready(w):
    marks['pawn']=time.time();receipt['pie_start_to_player_s']=round(marks['pawn']-marks['begin_play_request'],2);receipt['streaming_at_player']=streaming(w)
    pc=unreal.GameplayStatics.get_player_controller(w,0);unreal.SystemLibrary.execute_console_command(w,'t.MaxFPS 0',pc);pc=None;phase=2
   w=None
   if t>240:raise RuntimeError('PIE player not ready in 240 s')
  elif phase==2:
   # Prewarm: wait until the streamed cell count stops changing for 5 s (or 60 s).
   w=pie_world();s=streaming(w);w=None
   if marks.get('last_count')!=s['loaded']:marks['last_count']=s['loaded'];marks['changed']=time.time()
   if time.time()-marks['changed']>5 or time.time()-marks['pawn']>60:
    receipt['prewarm_settled_after_player_s']=round(marks['changed']-marks['pawn'],2);receipt['streaming_settled']=s;marks['sample']=time.time();phase=3
  elif phase==3:
   frames.append(dt*1000)
   if time.time()-marks['sample']>60:
    w=pie_world();receipt['encounter_bookkeeping']=dict(unreal.RVWorldContentLibrary.validate_encounter_bookkeeping(w));w=None
    receipt['encounter_pass']=bool(receipt['encounter_bookkeeping']) and all(v.startswith('true') for v in receipt['encounter_bookkeeping'].values())
    finish();phase=4;marks['end']=time.time()
  elif phase==4 and time.time()-marks['end']>2:phase=5;unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play();marks['end']=time.time()
  elif phase==5 and time.time()-marks['end']>8:phase=6;unreal.unregister_slate_post_tick_callback(handle);handle=None;gc.collect();unreal.SystemLibrary.quit_editor()
 except Exception:
  receipt['error']=traceback.format_exc();finish();phase=4;marks['end']=time.time()
handle=unreal.register_slate_post_tick_callback(tick)
