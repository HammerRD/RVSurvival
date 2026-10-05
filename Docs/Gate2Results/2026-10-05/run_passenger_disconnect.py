import unreal,json,time
base='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate2Validation/'
session=time.time();json.dump({'id':session},open(base+'session2.json','w'))
s=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.LevelEditorPlaySettings'))
n=s.get_editor_property('NetworkEmulationSettings');n.set_editor_property('bIsNetworkEmulationEnabled',False);s.set_editor_property('NetworkEmulationSettings',n)
s.set_editor_property('PlayNumberOfClients',2);s.set_editor_property('RunUnderOneProcess',False)
s.set_editor_property('AdditionalLaunchParameters','-ExecCmds="py D:/GitHub/RVSurvival/RVSurvival/Saved/Gate2Validation/start_passenger_client.py"')
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
def ready(dt):
    try:ok=json.load(open(base+'ready2.json'))['session']==session
    except:ok=False
    if ok:
        unreal.unregister_slate_post_tick_callback(h)
        exec(open(base+'passenger_disconnect.py').read(),{'__name__':'__main__'})
h=unreal.register_slate_post_tick_callback(ready)
