import unreal,shutil
base='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate2Validation/'
out='D:/GitHub/RVSurvival/RVSurvival/Docs/Gate2Results/2026-10-05/'
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
source=open(base+'final_suite.py').read()
exec('def restore():'+source.split('def restore():',1)[1].split('def tick(dt):',1)[0],globals())
t=0
def verify(dt):
    global t
    t+=dt
    if t>2:
        unreal.unregister_slate_post_tick_callback(h)
        restore()
        unreal.log('GATE2_CORRECTED_CLEANUP_PASS')
h=unreal.register_slate_post_tick_callback(verify)
unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(unreal.Vector(-750,-950,450),unreal.MathLibrary.find_look_at_rotation(unreal.Vector(-750,-950,450),unreal.Vector(0,0,140)))
