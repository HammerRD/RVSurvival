import unreal,json,time,os,shutil
B='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate3Validation/'
O='D:/GitHub/RVSurvival/RVSurvival/Docs/Gate4Results/Gate1Regression/'
os.makedirs(O,exist_ok=True);started=time.time()
unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings')).set_editor_property('bThrottleCPUWhenNotForeground',False)
from runner_runtime import load_runner
load_runner(B+'gate1_timeline.py')
def finish(dt):
 if time.time()-started<57:return
 rows=[]
 for n in ['single','multi']:
  p='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate1Validation/'+n+'.json'
  if not os.path.exists(p) or os.path.getmtime(p)<started:unreal.log_error('GATE3_GATE1_RESULT_MISSING '+n);unreal.unregister_slate_post_tick_callback(h);return
  d=json.load(open(p));rows+=d;shutil.copyfile(p,O+n+'.json')
 lines=[s for s in open('D:/GitHub/RVSurvival/RVSurvival/Saved/Logs/RVSurvival.log',encoding='utf-8',errors='replace') if 'GATE1_' in s or 'GATE2_GATE1_' in s]
 open(O+'results.log','w',encoding='utf-8').writelines(lines)
 ok=bool(rows) and all(r['pass'] for r in rows);json.dump({'pass':ok,'checks':len(rows),'failures':[r for r in rows if not r['pass']]},open(O+'summary.json','w'),indent=2)
 unreal.unregister_slate_post_tick_callback(h)
 log=unreal.log;quit_editor=unreal.SystemLibrary.quit_editor
 log('GATE3_GATE1_REGRESSION_DONE '+str(ok))
 from runner_runtime import release_runners
 log('GATE3_RELEASED_RUNNERS_GC_OK '+str(release_runners()))
 quit_editor()
h=unreal.register_slate_post_tick_callback(finish)





