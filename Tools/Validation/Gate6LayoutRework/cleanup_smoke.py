"""Fresh-editor smoke test of bounded manual runners and pre-Stop release."""
import time, unreal
from pathlib import Path
root = Path('D:/GitHub/RVSurvival/RVSurvival')
exec(compile((root/'Tools/Validation/Gate6LayoutRework/launch_manual.py').read_text(), 'launch_manual.py', 'exec'))
started = time.time()
phase = 0

def cleanup_tick(dt):
    global phase
    elapsed = time.time() - started
    if phase == 0 and elapsed > 18:
        # Separate exec namespace prevents the cleanup from unregistering this
        # smoke callback; runner callbacks are owned by their real modules.
        exec(compile((root/'Tools/Validation/Gate6LayoutRework/finish_manual.py').read_text(), 'finish_manual.py', 'exec'), {})
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
        phase = 1
    elif phase == 1 and elapsed > 23:
        assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
        unreal.unregister_slate_post_tick_callback(smoke_handle)
        unreal.log('FINAL_MANUAL_CLEANUP_SMOKE_PASS')
        unreal.SystemLibrary.quit_editor()

smoke_handle = unreal.register_slate_post_tick_callback(cleanup_tick)
