import unreal,time,json,sys,os
sys.path.insert(0,'D:/GitHub/RVSurvival/RVSurvival/Saved/Gate3Validation')
from runner_runtime import load_runner
B='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate9_5Validation/'
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level('/Game/Maps/Gate9_5CombatRefinementTest')
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
s=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.LevelEditorPlaySettings'));s.set_editor_property('RunUnderOneProcess',False);s.set_editor_property('PlayNumberOfClients',2);s.set_editor_property('AdditionalLaunchParameters','-ExecCmds="py D:/GitHub/RVSurvival/RVSurvival/Saved/Gate9_5Validation/process_startup.py"')
n=s.get_editor_property('NetworkEmulationSettings');case=json.load(open(B+'case.json'));n.set_editor_property('bIsNetworkEmulationEnabled',case.get('network',False));o=n.get_editor_property('OutPackets');o.set_editor_property('MinLatency',100);o.set_editor_property('MaxLatency',100);o.set_editor_property('PacketLossPercentage',2);n.set_editor_property('OutPackets',o);s.set_editor_property('NetworkEmulationSettings',n)
s.set_editor_property('AdditionalLaunchParameters','-ExecCmds="py D:/GitHub/RVSurvival/RVSurvival/Saved/Gate9_5Validation/process_startup.py" -abslog="'+B+case['name']+'_child.log"')
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
   loaded=True;json.dump({'id':sid,'start':time.time()+3,'config':case},open(B+'session.json','w'));load_runner(B+case.get('runner','process_refinement.py'))
 if (loaded and all(os.path.exists(B+case['name']+'_'+r+'.json') and os.path.getmtime(B+case['name']+'_'+r+'.json')>start for r in ['server','client'])) or t>240:
  if t>240:unreal.log_error('REFINE_TIMEOUT')
  unreal.unregister_slate_post_tick_callback(h)
  from runner_runtime import release_runners
  # No Python actor/world wrappers may survive into editor world cleanup.
  stop=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play
  quit_editor=unreal.SystemLibrary.quit_editor
  register=unreal.register_slate_post_tick_callback;unregister=unreal.unregister_slate_post_tick_callback
  clock=time.time;due=clock()+4
  def exit_tick(dt):
   if clock()>due:unregister(exit_handle);quit_editor()
  release_runners();stop();exit_handle=register(exit_tick)
h=unreal.register_slate_post_tick_callback(tick)






