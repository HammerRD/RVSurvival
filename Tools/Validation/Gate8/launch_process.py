import unreal,time,json,sys,os
sys.path.insert(0,'D:/GitHub/RVSurvival/RVSurvival/Saved/Gate3Validation')
from runner_runtime import load_runner,release_runners
B='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate8Validation/'
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level('/Game/Maps/Gate8MedicalTest')
assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
s=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.LevelEditorPlaySettings'));s.set_editor_property('RunUnderOneProcess',False);s.set_editor_property('PlayNumberOfClients',2);s.set_editor_property('AdditionalLaunchParameters','-ExecCmds="py D:/GitHub/RVSurvival/RVSurvival/Saved/Gate8Validation/process_startup.py"')
n=s.get_editor_property('NetworkEmulationSettings');case=json.load(open(B+'case.json'));n.set_editor_property('bIsNetworkEmulationEnabled',case.get('network',False));o=n.get_editor_property('OutPackets');o.set_editor_property('MinLatency',100);o.set_editor_property('MaxLatency',100);o.set_editor_property('PacketLossPercentage',2);n.set_editor_property('OutPackets',o);s.set_editor_property('NetworkEmulationSettings',n)
s.set_editor_property('AdditionalLaunchParameters','-ExecCmds="py D:/GitHub/RVSurvival/RVSurvival/Saved/Gate8Validation/process_startup.py" -abslog="'+B+case['name']+'_child.log"')
unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings')).set_editor_property('bThrottleCPUWhenNotForeground',False)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
t=0;loaded=False;ending=None;start=time.time();sid=start
json.dump({'id':sid,'start':None,'config':case},open(B+'session.json','w'))
def tick(dt):
 global t,loaded,ending
 t+=dt
 if t>6 and not loaded:
  try:ready=json.load(open(B+'ready.json'))['id']==sid
  except (OSError,ValueError,KeyError):ready=False
  if ready:
   loaded=True;json.dump({'id':sid,'start':time.time()+3,'config':case},open(B+'session.json','w'))
   try:load_runner(B+'process_refinement.py')
   except Exception:
    import traceback;traceback.print_exc()
    release_runners();unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play();ending=time.time()+4
 if loaded and not ending and all(os.path.exists(B+case['name']+'_'+r+'.json') and os.path.getmtime(B+case['name']+'_'+r+'.json')>start for r in ['server','client']):
  release_runners();unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play();ending=time.time()+4
 if t>240 and not ending:
  unreal.log_error('REFINE_TIMEOUT');release_runners();unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play();ending=time.time()+4
 if ending and time.time()>ending:
  unreal.unregister_slate_post_tick_callback(h);q=unreal.SystemLibrary.quit_editor
  # release helper imported at module scope
  release_runners();q()
h=unreal.register_slate_post_tick_callback(tick)




