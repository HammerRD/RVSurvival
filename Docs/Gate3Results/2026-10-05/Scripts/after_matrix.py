import unreal,json,time,os,shutil
B='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate3Validation/'
O='D:/GitHub/RVSurvival/RVSurvival/Docs/Gate3Results/2026-10-05/'
phases=[('soak_host','host',True,'run_soak.py'),('soak_client','client',True,'run_soak.py'),('standing_disconnect','host',False,'run_disconnect.py')]
stage=0;started=0;transition=None
def launch():
 global started
 n,r,net,script=phases[stage];json.dump({'name':n,'driver':r,'network':net},open(B+'case.json','w'));started=time.time()
 exec(open(B+script).read(),{'__name__':'__main__'})
def tick(dt):
 global stage,transition
 if transition:
  if time.time()<transition:return
  transition=None
  if stage==len(phases):
   unreal.unregister_slate_post_tick_callback(h);json.dump({'pass':True,'finished_utc':time.time()},open(B+'after_matrix_done.json','w'));unreal.log('GATE3_AFTER_MATRIX_DONE');return
  launch();return
 n=phases[stage][0];p=B+n+'.json'
 if not os.path.exists(p) or os.path.getmtime(p)<started:return
 d=json.load(open(p));rows=d['results'] if isinstance(d,dict) else d;shutil.copyfile(p,O+n+'.json')
 unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
 if not rows or not all(r['pass'] for r in rows):
  unreal.unregister_slate_post_tick_callback(h);unreal.log_error('GATE3_AFTER_MATRIX_FAILED '+n+' '+str([r for r in rows if not r['pass']]));return
 unreal.log('GATE3_AFTER_MATRIX_PASS '+n);stage+=1;transition=time.time()+3
h=unreal.register_slate_post_tick_callback(tick);launch()
