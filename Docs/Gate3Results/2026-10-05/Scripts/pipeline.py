import unreal,json,time,os,math,shutil
B='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate3Validation/'
O='D:/GitHub/RVSurvival/RVSurvival/Docs/Gate3Results/2026-10-05/'
os.makedirs(O,exist_ok=True)
phases=[('process_host_driver','host',False),('process_client_driver','client',False),('network_host_driver','host',True),('network_client_driver','client',True)]
stage=0;started=time.time();transition=None
def launch():
 global started
 n,r,net=phases[stage];json.dump({'name':n,'driver':r,'network':net},open(B+'case.json','w'));started=time.time()
 exec(open(B+'run_process.py').read(),{'__name__':'__main__'})
def paired(a,b):
 role=a['config']['driver'];net=a['config'].get('network');limit=75 if net else 30
 own=a if role=='client' else b;obs=b if role=='client' else a
 ss=[r for r in own['samples'] if 37<r['t']<116];oo=obs['samples'];j=0;errors=[];visual=[]
 for s in ss:
  while j+1<len(oo) and abs(oo[j+1]['t']-s['t'])<abs(oo[j]['t']-s['t']):j+=1
  errors.append(math.dist(s['local'],oo[j]['local']));visual.append(math.dist(s['local'],oo[j]['visual']))
 result={'different_processes':a['process_id']!=b['process_id'],'server_pid':a['process_id'],'client_pid':b['process_id'],'station_counts_agree':a['station_counts']==b['station_counts'],'max_capsule_error_cm':max(errors),'max_visual_error_cm':max(visual),'samples':len(ss),'limit_cm':limit}
 result['pass']=result['different_processes'] and result['station_counts_agree'] and max(errors)<limit and max(visual)<limit
 return result
def tick(dt):
 global stage,transition
 try:
  if transition:
   if time.time()<transition:return
   transition=None
   if stage==len(phases):unreal.unregister_slate_post_tick_callback(h);unreal.log('GATE3_PIPELINE_DONE');return
   launch();return
  n,r,net=phases[stage];paths=[B+n+'_server.json',B+n+'_client.json']
  if not all(os.path.exists(p) and os.path.getmtime(p)>started for p in paths):return
  a,b=[json.load(open(p)) for p in paths];pair=paired(a,b);json.dump(pair,open(O+n+'_paired.json','w'),indent=2)
  for p in paths:shutil.copyfile(p,O+os.path.basename(p))
  failures=[x for d in [a,b] for x in d['results'] if not x['pass']]
  unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
  if failures or not pair['pass']:
   unreal.unregister_slate_post_tick_callback(h);unreal.log_error('GATE3_PIPELINE_FAILED '+n+' '+str(failures)+' '+str(pair));return
  unreal.log('GATE3_PIPELINE_PASS '+n+' '+str(pair));stage+=1;transition=time.time()+3
 except Exception as e:unreal.unregister_slate_post_tick_callback(h);unreal.log_error('GATE3_PIPELINE_ERROR '+str(e))
h=unreal.register_slate_post_tick_callback(tick)
unreal.log('GATE3_PIPELINE_MONITORING_CURRENT_PROCESS_RUN')
