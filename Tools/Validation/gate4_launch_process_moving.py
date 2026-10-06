import unreal,json,time,os
from runner_runtime import load_runner
B='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate4Validation/'
config=json.load(open(B+'moving_process_case.json'));sid=time.time();started=time.time()
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level('/Game/Maps/Gate4InventoryTest')
s=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.LevelEditorPlaySettings'))
s.set_editor_property('PlayNumberOfClients',2);s.set_editor_property('RunUnderOneProcess',False)
s.set_editor_property('AdditionalLaunchParameters','-ExecCmds="py D:/GitHub/RVSurvival/RVSurvival/Saved/Gate4Validation/process_moving_startup.py"')
n=s.get_editor_property('NetworkEmulationSettings');n.set_editor_property('bIsNetworkEmulationEnabled',bool(config.get('network')))
o=n.get_editor_property('OutPackets');o.set_editor_property('MinLatency',100);o.set_editor_property('MaxLatency',100);o.set_editor_property('PacketLossPercentage',2);n.set_editor_property('OutPackets',o);s.set_editor_property('NetworkEmulationSettings',n)
unreal.log('GATE4_NETWORK_CONFIG '+str(n))
unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings')).set_editor_property('bThrottleCPUWhenNotForeground',False)
json.dump({'id':sid,'start':None,'config':config},open(B+'process_session.json','w'))
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
loaded=False;ending=None

def tick(dt):
 global loaded,ending
 if not loaded:
  try:ready=json.load(open(B+'process_ready.json'))['id']==sid
  except (OSError,ValueError,KeyError):ready=False
  if ready:
   loaded=True;json.dump({'id':sid,'start':time.time()+3,'config':config},open(B+'process_session.json','w'));load_runner(B+'process_moving.py')
 paths=[B+config['name']+'_'+role+'.json' for role in ['server','client']]
 if loaded and not ending and all(os.path.exists(p) and os.path.getmtime(p)>started for p in paths):
  unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play();ending=time.time()+4
 if ending and time.time()>ending:
  unreal.unregister_slate_post_tick_callback(h);quit=unreal.SystemLibrary.quit_editor
  from runner_runtime import release_runners
  release_runners();quit()
h=unreal.register_slate_post_tick_callback(tick)

