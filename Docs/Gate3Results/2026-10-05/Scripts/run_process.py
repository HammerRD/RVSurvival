from runner_runtime import load_runner
import unreal,json,time
B='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate3Validation/'
load_runner(B+'play_settings.py')
sid=time.time();config=json.load(open(B+'case.json'));json.dump({'id':sid,'start':None,'config':config},open(B+'process_session.json','w'))
s=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.LevelEditorPlaySettings'));s.set_editor_property('PlayNumberOfClients',2);s.set_editor_property('RunUnderOneProcess',False);s.set_editor_property('AdditionalLaunchParameters','-ExecCmds="py D:/GitHub/RVSurvival/RVSurvival/Saved/Gate3Validation/process_startup.py"')
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
def start(dt):
 try:ready=json.load(open(B+'process_ready.json'))['id']==sid
 except:ready=False
 if not ready:return
 unreal.unregister_slate_post_tick_callback(h);json.dump({'id':sid,'start':time.time()+3,'config':config},open(B+'process_session.json','w'));load_runner(B+'process_suite.py')
h=unreal.register_slate_post_tick_callback(start)


