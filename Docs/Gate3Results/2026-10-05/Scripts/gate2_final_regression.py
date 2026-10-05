import unreal,time,json,os,shutil
base='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate2Validation/'
out='D:/GitHub/RVSurvival/RVSurvival/Docs/Gate3Results/2026-10-05/Gate2Regression/'
os.makedirs(out,exist_ok=True)
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
level.load_level('/Game/Maps/Gate2VehicleTest')
s=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.LevelEditorPlaySettings'));n=s.get_editor_property('NetworkEmulationSettings');n.set_editor_property('bIsNetworkEmulationEnabled',False);s.set_editor_property('NetworkEmulationSettings',n)
unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings')).set_editor_property('bThrottleCPUWhenNotForeground',False)
unreal.SystemLibrary.execute_console_command(unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world(),'t.MaxFPS 60')
exec(open(base+'fixture.py').read(),{'__name__':'__main__'})
phases=[('shared','run_multi.py',[('multi.json','shared_multi.json')]),('race','run_race.py',[('race.json','concurrent_seat_claim.json')]),('baseline','run_process.py',[('process2_host.json','separate_process_host.json'),('process2_client.json','separate_process_client.json')]),('network','run_process_network.py',[('process2_host.json','network_host.json'),('process2_client.json','network_client.json')]),('passenger','run_passenger_disconnect.py',[('passenger_disconnect_host.json','passenger_disconnect_host.json'),('passenger_disconnect_client.json','passenger_disconnect_client.json')])]
stage=0;started=0;transition=None

def launch():
    global started
    started=time.time()
    unreal.log('GATE2_FINAL_PHASE '+phases[stage][0])
    if phases[stage][0]=='shared':
        s.set_editor_property('PlayNumberOfClients',2);s.set_editor_property('RunUnderOneProcess',True);s.set_editor_property('AdditionalLaunchParameters','')
    exec(open(base+phases[stage][1]).read(),{'__name__':'__main__'})

def restore():
    s=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.LevelEditorPlaySettings'))
    s.set_editor_property('RunUnderOneProcess',True);s.set_editor_property('PlayNumberOfClients',2);s.set_editor_property('AdditionalLaunchParameters','')
    n=s.get_editor_property('NetworkEmulationSettings');n.set_editor_property('bIsNetworkEmulationEnabled',False);s.set_editor_property('NetworkEmulationSettings',n)
    unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings')).set_editor_property('bThrottleCPUWhenNotForeground',True)
    unreal.SystemLibrary.execute_console_command(unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world(),'t.MaxFPS 0')
    shutil.copyfile(base+'fixture.json',out+'fixture.json')
    unreal.log('GATE2_FINAL_SUITE_DONE')
    json.dump({'pass':True,'finished':time.time()},open(out+'summary.json','w'),indent=2)
    __import__('gc').collect()

def tick(dt):
    global stage,transition
    try:
        if transition is not None:
            if time.time()<transition:return
            transition=None
            if stage==len(phases):
                unreal.unregister_slate_post_tick_callback(h);restore();return
            launch();return
        phase,script,files=phases[stage]
        if phase=='regression' and time.time()-started<58:return
        if not all(os.path.exists(base+a) and os.path.getmtime(base+a)>started for a,b in files):return
        records=[json.load(open(base+a)) for a,b in files]
        rows=[r for data in records for r in (data['results'] if isinstance(data,dict) else data)]
        if not rows or not all(r['pass'] for r in rows):
            unreal.log_error('GATE2_FINAL_PHASE_FAILED '+phase+' '+str([r for r in rows if not r['pass']]))
            unreal.unregister_slate_post_tick_callback(h);return
        for a,b in files:shutil.copyfile(base+a,out+b)
        for name in ['RVSurvival.log','RVSurvival_2.log']:
            path='D:/GitHub/RVSurvival/RVSurvival/Saved/Logs/'+name
            if os.path.exists(path):
                lines=[s for s in open(path,encoding='utf-8',errors='replace') if 'GATE2_' in s or 'GATE1_' in s]
                open(out+phase+'_'+name,'w',encoding='utf-8').writelines(lines)
        unreal.log('GATE2_FINAL_PHASE_PASS '+phase+' '+str(len(rows)))
        level.editor_request_end_play();stage+=1;transition=time.time()+3
    except Exception as e:
        unreal.log_error('GATE2_FINAL_SUITE_ERROR '+str(e));unreal.unregister_slate_post_tick_callback(h)
h=unreal.register_slate_post_tick_callback(tick)
launch()
