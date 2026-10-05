import unreal,json,time
base='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate2Validation/'
session=time.time();json.dump({'id':session},open(base+'session2.json','w'))
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.LevelEditorPlaySettings'))
settings.set_editor_property('PlayNumberOfClients',2);settings.set_editor_property('RunUnderOneProcess',False)
settings.set_editor_property('AdditionalLaunchParameters','-ExecCmds="py D:/GitHub/RVSurvival/RVSurvival/Saved/Gate2Validation/start_client.py"')
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
elapsed=0
def start(dt):
    global elapsed
    elapsed+=dt
    try:ready=json.load(open(base+'ready2.json'))['session']==session
    except:ready=False
    if ready:
        unreal.unregister_slate_post_tick_callback(h)
        exec(open('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate2Validation/process.py').read(),{'__name__':'__main__'})
h=unreal.register_slate_post_tick_callback(start)
