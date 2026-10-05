import unreal, math, json
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
pc = unreal.GameplayStatics.get_player_controller(world, 0)
pawn = pc.get_controlled_pawn()
target = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.load_class(None, '/Script/RVSurvival.RVTestInteractable'))[0]
target.set_actor_rotation(unreal.Rotator(yaw=180), False)
results=[]
def count(): return target.get_editor_property('interaction_count')
def cmd(s): unreal.SystemLibrary.execute_console_command(world,s,pc)
def aim():
    pawn.set_actor_location(unreal.Vector(-600,-450,100),False,True)
    pc.set_control_rotation(unreal.Rotator())
def check(name,ok,detail):
    row={'case':name,'pass':bool(ok),'detail':str(detail)}
    results.append(row); unreal.log('GATE1_RESULT '+json.dumps(row))
events=[]
def at(t,fn): events.append((t,fn))
state={}
at(0,aim)
at(.3,lambda:check('reset_count',count()==0,count()))
for i,(key,axis,sign) in enumerate([('W','x',1),('S','x',-1),('D','y',1),('A','y',-1)]):
    start=1+i*.7
    at(start,lambda key=key:(state.update(pos=pawn.get_actor_location()),cmd('Input.+key '+key)))
    at(start+.25,lambda key=key:cmd('Input.-key '+key))
    at(start+.5,lambda key=key,axis=axis,sign=sign:check('movement_'+key,(getattr(pawn.get_actor_location(),axis)-getattr(state['pos'],axis))*sign>1,pawn.get_actor_location()))
at(4,aim)
at(4.3,lambda:(state.update(z=pawn.get_actor_location().z),cmd('Input.+key SpaceBar')))
at(4.5,lambda:check('jump',pawn.get_actor_location().z>state['z']+10,pawn.get_actor_location()))
at(4.6,lambda:cmd('Input.-key SpaceBar'))
at(5.5,lambda:(state.update(yaw=pc.get_control_rotation().yaw),cmd('Input.+key MouseX 1')))
at(5.7,lambda:cmd('Input.-key MouseX'))
at(5.8,lambda:check('mouse_yaw',abs(pc.get_control_rotation().yaw-state['yaw'])>1,pc.get_control_rotation()))
at(6,lambda:(state.update(pitch=pc.get_control_rotation().pitch),cmd('Input.+key MouseY 1')))
at(6.2,lambda:cmd('Input.-key MouseY'))
at(6.3,lambda:check('mouse_pitch',abs(pc.get_control_rotation().pitch-state['pitch'])>1,pc.get_control_rotation()))
at(7,aim)
at(7.4,lambda:cmd('Input.+key E'))
at(7.7,lambda:check('hold_before_half_second',count()==0,count()))
at(8.1,lambda:check('hold_completion',count()==1,count()))
at(9,lambda:check('continued_hold_no_repeat',count()==1,count()))
at(9.1,lambda:cmd('Input.-key E'))
at(10,lambda:cmd('Input.+key E'))
at(10.2,lambda:cmd('Input.-key E'))
at(10.9,lambda:check('early_release',count()==1,count()))
at(12,lambda:cmd('Input.+key E'))
at(12.2,lambda:pc.set_control_rotation(unreal.Rotator(yaw=90)))
at(12.8,lambda:check('look_away_cancel',count()==1,count()))
at(12.9,lambda:cmd('Input.-key E'))
at(13.3,aim)
at(14,lambda:cmd('Input.+key E'))
at(14.2,lambda:pawn.set_actor_location(unreal.Vector(-1000,-450,100),False,True))
at(14.8,lambda:check('out_of_range_cancel',count()==1,count()))
at(14.9,lambda:cmd('Input.-key E'))
at(15.3,aim)
def occlude():
    blocker=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.StaticMeshActor) if a.get_actor_label()=='Gate1Occluder')
    blocker.set_actor_location(unreal.Vector(-480,-450,160),False,True)
    mesh=blocker.get_component_by_class(unreal.StaticMeshComponent)
    mesh.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Cube'))
    mesh.set_collision_profile_name('BlockAll')
    state['blocker']=blocker
at(16,lambda:cmd('Input.+key E'))
at(16.2,occlude)
at(16.8,lambda:check('line_of_sight_cancel',count()==1,count()))
at(16.9,lambda:cmd('Input.-key E'))
def finish():
    with open('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate1Validation/single.json','w') as f: json.dump(results,f,indent=2)
    unreal.unregister_slate_post_tick_callback(handle)
    unreal.log('GATE1_SINGLE_DONE')
at(18,finish)
elapsed=0.0
index=0
def tick(dt):
    global elapsed,index
    elapsed+=dt
    try:
        while index<len(events) and elapsed>=events[index][0]:
            fn=events[index][1]; index+=1; fn()
    except Exception as e:
        unreal.log_error('GATE1_TEST_ERROR '+str(e)); unreal.unregister_slate_post_tick_callback(handle)
handle=unreal.register_slate_post_tick_callback(tick)
