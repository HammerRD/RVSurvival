import unreal, json, math
worlds=[w for w in unreal.ObjectIterator(unreal.World) if '/Game/Maps/UEDPIE_' in w.get_path_name() and w.get_name()=='Gate1Test']
unreal.log('GATE1_WORLDS '+str([w.get_path_name() for w in worlds]))
worlds.sort(key=lambda w:w.get_path_name())
assert len(worlds)==2, 'Expected two PIE worlds'
server,client=worlds
host=unreal.GameplayStatics.get_player_controller(server,0)
remote=unreal.GameplayStatics.get_player_controller(client,0)
hp=host.get_controlled_pawn(); rp=remote.get_controlled_pawn()
cls=unreal.load_class(None,'/Script/RVSurvival.RVTestInteractable')
sc=unreal.GameplayStatics.get_all_actors_of_class(server,cls)[0]
cc=unreal.GameplayStatics.get_all_actors_of_class(client,cls)[0]
results=[]
def counts():return [sc.get_editor_property('interaction_count'),cc.get_editor_property('interaction_count')]
def check(name,ok,detail):
    row={'case':name,'pass':bool(ok),'detail':str(detail)};results.append(row);unreal.log('GATE1_MULTI_RESULT '+json.dumps(row))
def cmd(pc,s):unreal.SystemLibrary.execute_console_command(pc,s,pc)
def aim():
    spawns=unreal.GameplayStatics.get_all_actors_of_class(server,unreal.load_class(None,'/Script/RVSurvival.RVSurvivorCharacter'))
    for p in spawns:
        p.set_actor_location(unreal.Vector(-600,-510 if p==hp else -390,100),False,True)
    host.set_control_rotation(unreal.Rotator(yaw=14.04));remote.set_control_rotation(unreal.Rotator(yaw=-14.04))
events=[]
def at(t,f):events.append((t,f))
state={}
at(0,aim)
at(.5,lambda:check('reset_count',counts()==[0,0],counts()))
at(1,lambda:(state.update(h=hp.get_actor_location(),r=rp.get_actor_location()),cmd(host,'Input.+key S')))
at(1.2,lambda:cmd(host,'Input.-key S'))
at(1.5,lambda:check('host_moves_independently',(hp.get_actor_location()-state['h']).length()>5 and (rp.get_actor_location()-state['r']).length()<2,[hp.get_actor_location(),rp.get_actor_location()]))
at(2,lambda:(state.update(h=hp.get_actor_location(),r=rp.get_actor_location()),cmd(remote,'Input.+key S')))
at(2.2,lambda:cmd(remote,'Input.-key S'))
at(2.5,lambda:check('client_moves_independently',(rp.get_actor_location()-state['r']).length()>5 and (hp.get_actor_location()-state['h']).length()<2,[hp.get_actor_location(),rp.get_actor_location()]))
at(3,aim)
at(4,lambda:cmd(host,'Input.+key E'))
at(5.2,lambda:check('host_interacts_and_replicates',counts()==[1,1],counts()))
at(5.3,lambda:cmd(host,'Input.-key E'))
at(6,lambda:cmd(remote,'Input.+key E'))
at(7.3,lambda:check('remote_interacts_and_replicates',counts()==[2,2],counts()))
at(7.4,lambda:cmd(remote,'Input.-key E'))
at(8,lambda:(cmd(host,'Input.+key E'),cmd(remote,'Input.+key E')))
at(9.5,lambda:check('simultaneous_two_increments',counts()==[4,4],counts()))
at(10.5,lambda:check('both_continued_holds_no_duplicate',counts()==[4,4],counts()))
at(10.6,lambda:(cmd(host,'Input.-key E'),cmd(remote,'Input.-key E')))
at(12,lambda:cmd(remote,'Input.+key E'))
at(12.2,lambda:cmd(remote,'Input.-key E'))
at(13.5,lambda:check('remote_early_release',counts()==[4,4],counts()))
def finish():
    with open('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate1Validation/multi.json','w') as f:json.dump(results,f,indent=2)
    unreal.unregister_slate_post_tick_callback(handle);unreal.log('GATE1_MULTI_DONE')
at(15,finish)
elapsed=0;index=0
def tick(dt):
    global elapsed,index
    elapsed+=dt
    try:
        while index<len(events) and elapsed>=events[index][0]:
            fn=events[index][1];index+=1;fn()
    except Exception as e:
        unreal.log_error('GATE1_MULTI_ERROR '+str(e));unreal.unregister_slate_post_tick_callback(handle)
handle=unreal.register_slate_post_tick_callback(tick)
