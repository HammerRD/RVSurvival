import unreal,json,time,os,shutil
B='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate3Validation/'
O='D:/GitHub/RVSurvival/RVSurvival/Docs/Gate3Results/2026-10-05/'
started=time.time();phase=0
exec(open(B+'run_final_client.py').read(),{'__name__':'__main__'})
def tick(dt):
 global phase,started
 if phase==0:
  p=B+'final_material_client.json'
  if not os.path.exists(p) or os.path.getmtime(p)<started:return
  d=json.load(open(p));shutil.copyfile(p,O+'final_material_client.json')
  unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
  if not all(r['pass'] for r in d['results']):unreal.unregister_slate_post_tick_callback(h);unreal.log_error('GATE3_FINAL_CLIENT_FAILED');return
  phase=1;started=time.time();return
 if phase==1 and time.time()-started>3:
  unreal.unregister_slate_post_tick_callback(h)
  ns={'__name__':'__main__'};exec(open(B+'pipeline.py').read(),ns);ns['launch']()
h=unreal.register_slate_post_tick_callback(tick)
