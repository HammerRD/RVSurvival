"""Native editor cleanup after releasing all managed test-module references."""
def end_play_then_quit(callback):
 import unreal,time
 unreal.unregister_slate_post_tick_callback(callback)
 stop=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play
 quit_editor=unreal.SystemLibrary.quit_editor
 register=unreal.register_slate_post_tick_callback;unregister=unreal.unregister_slate_post_tick_callback
 clock=time.time;due=clock()+4
 def exit_tick(dt):
  if clock()>due:unregister(handle);quit_editor()
 from runner_runtime import release_runners
 release_runners();stop();handle=register(exit_tick)
