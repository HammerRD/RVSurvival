import unreal,json,time,os,shutil
from runner_runtime import load_runner
B='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate3Validation/'
O='D:/GitHub/RVSurvival/RVSurvival/Docs/Gate3Results/2026-10-05/'
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level('/Game/Maps/Gate3MovingInteriorTest')
unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings')).set_editor_property('bThrottleCPUWhenNotForeground',False)
json.dump({'name':'owned_runner_host','driver':'host','network':False},open(B+'case.json','w'));started=time.time();transition=None
load_runner(B+'run_suite.py')
def finish(dt):
 global transition
 p=B+'owned_runner_host.json'
 if not transition:
  if not os.path.exists(p) or os.path.getmtime(p)<started:return
  d=json.load(open(p));shutil.copyfile(p,O+'owned_runner_host.json');unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
  if not all(r['pass'] for r in d['results']):unreal.log_error('GATE3_OWNED_RUNNER_FAILED');unreal.unregister_slate_post_tick_callback(h);return
  transition=time.time()+4;return
 if time.time()<transition:return
 unreal.unregister_slate_post_tick_callback(h)
 log=unreal.log;quit_editor=unreal.SystemLibrary.quit_editor
 from runner_runtime import release_runners
 log('GATE3_OWNED_HOST_PASS_AND_CLEANUP '+str(release_runners()));quit_editor()
h=unreal.register_slate_post_tick_callback(finish)
