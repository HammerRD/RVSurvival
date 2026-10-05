import unreal,json,time,os,shutil
B='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate3Validation/'
O='D:/GitHub/RVSurvival/RVSurvival/Docs/Gate3Results/2026-10-05/'
phases=[('disconnect',None,['standing_disconnect.json']),('integration','run_integration.py',['integration_regression.json']),('final_material_host','run_suite.py',['final_material_host.json']),('final_material_network_client','run_process.py',['final_material_network_client_server.json','final_material_network_client_client.json'])]
stage=1;started=time.time();transition=None
def launch():
 global started
 n,script,files=phases[stage];config={'name':n,'driver':'client' if 'network_client' in n else 'host','network':'network_client' in n};json.dump(config,open(B+'case.json','w'));started=time.time()
 if n=='integration':
  exec(open(B+'play_settings.py').read(),{'__name__':'__main__'})
  s=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.LevelEditorPlaySettings'));s.set_editor_property('RunUnderOneProcess',True);s.set_editor_property('AdditionalLaunchParameters','')
 exec(open(B+script).read(),{'__name__':'__main__'})
def tick(dt):
 global stage,transition
 try:
  if transition:
   if time.time()<transition:return
   transition=None
   if stage==len(phases):unreal.unregister_slate_post_tick_callback(h);unreal.log('GATE3_POST_PIPELINE_DONE');return
   launch();return
  n,script,files=phases[stage];paths=[B+f for f in files]
  if not all(os.path.exists(p) and os.path.getmtime(p)>started for p in paths):return
  ds=[json.load(open(p)) for p in paths];rows=[r for d in ds for r in (d['results'] if isinstance(d,dict) else d)];failures=[r for r in rows if not r['pass']]
  if len(ds)==2:
   ns={};exec(open(B+'pipeline.py').read().split('def tick(dt):')[0],ns);pair=ns['paired'](*ds);json.dump(pair,open(O+n+'_paired.json','w'),indent=2)
   if not pair['pass']:failures.append(pair)
  for p in paths:shutil.copyfile(p,O+os.path.basename(p))
  unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
  if failures:
   unreal.unregister_slate_post_tick_callback(h);unreal.log_error('GATE3_POST_PIPELINE_FAILED '+n+' '+str(failures));return
  unreal.log('GATE3_POST_PIPELINE_PASS '+n+' '+str(len(rows)));stage+=1;transition=time.time()+3
 except Exception as e:unreal.unregister_slate_post_tick_callback(h);unreal.log_error('GATE3_POST_PIPELINE_ERROR '+str(e))
h=unreal.register_slate_post_tick_callback(tick)

launch()

