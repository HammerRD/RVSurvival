"""Saved WNY two-process listen-server probe, no legacy runner references."""
import unreal,time,json,runpy,gc,sys
from pathlib import Path
out=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate10Validation');start=time.time();handle=None;loaded=False;ending=None
case=json.loads((out/'process-case.json').read_text())
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level('/Game/Maps/WNY_PrototypeRegion')
editor_world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
for command in ['wp.Runtime.UseMakingVisibleTransactionRequests 1','wp.Runtime.UseMakingInvisibleTransactionRequests 1','LevelStreaming.DefaultAllowClientUseMakingVisibleTransactionRequests 1']:
 unreal.SystemLibrary.execute_console_command(editor_world,command,None)
editor_world=None
for path in unreal.EditorAssetLibrary.list_assets('/Game/World/WNY/Materials',recursive=False,include_folder=False):
 material=unreal.load_asset(path)
 if isinstance(material,unreal.Material):
  unreal.MaterialEditingLibrary.set_material_usage(material,unreal.MaterialUsage.MATUSAGE_INSTANCED_STATIC_MESHES)
  unreal.EditorAssetLibrary.save_loaded_asset(material,False)
material=None
assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.LevelEditorPlaySettings'))
settings.set_editor_property('RunUnderOneProcess',False);settings.set_editor_property('PlayNumberOfClients',2)
# Private PIE net-mode enum is configured in native saved settings before launch.
settings.set_editor_property('AdditionalLaunchParameters','-ExecCmds="wp.Runtime.UseMakingVisibleTransactionRequests 1,wp.Runtime.UseMakingInvisibleTransactionRequests 1,LevelStreaming.DefaultAllowClientUseMakingVisibleTransactionRequests 1,py D:/GitHub/RVSurvival/RVSurvival/Tools/Validation/Gate10/process_startup.py" -abslog="D:/GitHub/RVSurvival/RVSurvival/Saved/Gate10Validation/'+case['name']+'-child.log"')
network=settings.get_editor_property('NetworkEmulationSettings');network.set_editor_property('bIsNetworkEmulationEnabled',case.get('network',False));packets=network.get_editor_property('OutPackets');packets.set_editor_property('MinLatency',100);packets.set_editor_property('MaxLatency',100);packets.set_editor_property('PacketLossPercentage',2);network.set_editor_property('OutPackets',packets);settings.set_editor_property('NetworkEmulationSettings',network)
unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings')).set_editor_property('bThrottleCPUWhenNotForeground',False)
(out/'process-session.json').write_text(json.dumps({'id':start,'start':None,'config':case}))
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
def tick(dt):
 global handle,loaded,ending
 now=time.time()
 if ending:
  if now-ending>4:unreal.unregister_slate_post_tick_callback(handle);handle=None;unreal.SystemLibrary.quit_editor()
  return
 if not loaded:
  try:ready=json.loads((out/'process-ready.json').read_text())['id']==start
  except (OSError,ValueError,KeyError):ready=False
  if ready:
   loaded=True;(out/'process-session.json').write_text(json.dumps({'id':start,'start':now+4,'config':case}));runpy.run_path('D:/GitHub/RVSurvival/RVSurvival/Tools/Validation/Gate10/process_region.py')
 complete=loaded and all((out/(case['name']+'-'+role+'.json')).exists() and (out/(case['name']+'-'+role+'.json')).stat().st_mtime>start for role in ['server','client'])
 if complete or now-start>180:
  if not complete:(out/(case['name']+'-timeout.json')).write_text(json.dumps({'timeout':True,'ready':loaded}))
  for k in ['last_traceback','last_value','last_type','last_exc']:
   if hasattr(sys,k):setattr(sys,k,None)
  gc.collect();ending=now;unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
handle=unreal.register_slate_post_tick_callback(tick)
