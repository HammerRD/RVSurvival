import unreal,json,math
worlds=sorted([w for w in unreal.ObjectIterator(unreal.World) if '/Game/Maps/UEDPIE_' in w.get_path_name() and w.get_name()=='Gate3MovingInteriorTest'],key=lambda w:w.get_path_name())
server,client=worlds
host=unreal.GameplayStatics.get_player_controller(server,0);remote=unreal.GameplayStatics.get_player_controller(client,0)
vc=unreal.load_class(None,'/Script/RVSurvival.RVInteriorMotorhome');ec=unreal.load_class(None,'/Script/RVSurvival.RVVehicleEntryPoint');chc=unreal.load_class(None,'/Script/RVSurvival.RVSurvivorCharacter')
sv=unreal.GameplayStatics.get_all_actors_of_class(server,vc)[0];cv=unreal.GameplayStatics.get_all_actors_of_class(client,vc)[0]
hp=host.get_controlled_pawn();rp=remote.get_controlled_pawn()
sp=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(server,chc) if a!=hp)
chp=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(client,chc) if a!=rp)
results=[];state={};events=[];diags=[];sample_acc=0
m=sv.get_component_by_class(unreal.load_class(None,'/Script/RVSurvival.RVVehicleMovementComponent'))
def cmd(pc,s):unreal.SystemLibrary.execute_console_command(pc,s,pc)
def key(pc,k,on):cmd(pc,'Input.'+('+' if on else '-')+'key '+k)
def check(name,ok,detail):
    row={'case':name,'pass':bool(ok),'detail':str(detail)};results.append(row);unreal.log('GATE3_INTEGRATION_RESULT '+json.dumps(row))
def seats(v):return {s.get_name():s.get_editor_property('Occupant') for s in v.get_seats()}
def occupied(v):return {k:(o.get_name() if o else None) for k,o in seats(v).items()}
def agree():
    ss,cs=seats(sv),seats(cv)
    return all(cs[k]==({hp:chp,sp:rp}.get(o) if o else None) for k,o in ss.items())
def aim(pc,driver):
    entry=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(server,ec) if a.get_editor_property('Seat').get_editor_property('bDriverSeat')==driver)
    p=hp if pc==host else sp
    side=sv.get_actor_right_vector()*(-180 if driver else 180)
    pos=entry.get_actor_location()+side;pos.z=92;p.set_actor_location(pos,False,True)
    pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(pos+unreal.Vector(0,0,64),entry.get_actor_location()))
def at(t,f):events.append((t,f))
def enter(t,pc,driver):
    at(t,lambda:aim(pc,driver));at(t+1,lambda:key(pc,'E',True));at(t+2,lambda:key(pc,'E',False))
def exit(t,pc):at(t,lambda:key(pc,'E',True));at(t+.2,lambda:key(pc,'E',False))
def sample():return [sv.get_actor_location(),cv.get_actor_location(),sv.get_velocity(),occupied(sv),occupied(cv)]
def replicate(name):check(name,agree() and (sv.get_actor_location()-cv.get_actor_location()).length()<100,sample())
at(0,lambda:check('fresh_seats_empty',all(o is None for o in seats(sv).values()) and agree(),sample()))
enter(1,host,True)
at(3.5,lambda:check('host_driver_possession',host.get_controlled_pawn()==sv and seats(sv)['DriverSeat']==hp and agree(),sample()))
enter(4,remote,True)
at(6.6,lambda:check('occupied_driver_rejected',remote.get_controlled_pawn()==rp and seats(sv)['DriverSeat']==hp and agree(),sample()))
enter(7,remote,False)
at(9.6,lambda:check('client_passenger_host_driver',remote.get_controlled_pawn()==rp and seats(sv)['PassengerSeat']==sp and agree(),sample()))
at(10,lambda:(state.update(pos=sv.get_actor_location(),yaw=sv.get_actor_rotation().yaw),key(host,'W',True)))
exit(11,host)
at(11.4,lambda:check('moving_exit_rejected',host.get_controlled_pawn()==sv,sv.get_velocity()))
at(12,lambda:key(host,'D',True))
at(13,lambda:key(host,'D',False))
at(13.5,lambda:check('host_acceleration_steering',(sv.get_actor_location()-state['pos']).length()>300 and abs(sv.get_actor_rotation().yaw-state['yaw'])>1,sample()))
at(13.6,lambda:replicate('host_drive_replicated'))
at(13.7,lambda:check('client_passenger_attached',(rp.get_actor_location()-cv.get_actor_location()).length()<250 and (sp.get_actor_location()-sv.get_actor_location()).length()<250,[rp.get_actor_location(),sp.get_actor_location()]))
at(14,lambda:(key(host,'W',False),key(host,'SpaceBar',True)))
at(19,lambda:check('host_handbrake_stops',sv.get_velocity().length()<150,sv.get_velocity()))
at(19.2,lambda:replicate('stopped_vehicle_converges'))
exit(20,remote)
at(21,lambda:check('client_passenger_exit_frees_seat',seats(sv)['PassengerSeat'] is None and remote.get_controlled_pawn()==rp and agree(),sample()))
exit(22,host)
at(23,lambda:check('host_exit_restores_character',host.get_controlled_pawn()==hp and all(o is None for o in seats(sv).values()) and hp.get_actor_location().z>85 and agree(),[hp.get_actor_location(),sample()]))
at(23.2,lambda:key(host,'SpaceBar',False))
# Keep the real stopped RV in place for the role exchange; no artificial physics teleport.
enter(24,remote,True)
at(26.6,lambda:check('remote_driver_possession',remote.get_controlled_pawn()==cv and seats(sv)['DriverSeat']==sp and agree(),sample()))
enter(27,host,False)
at(29.6,lambda:check('host_passenger_client_driver',host.get_controlled_pawn()==hp and seats(sv)['PassengerSeat']==hp and agree(),sample()))
at(30,lambda:(state.update(pos=sv.get_actor_location(),yaw=sv.get_actor_rotation().yaw),key(remote,'W',True)))
at(31,lambda:key(remote,'A',True));at(32,lambda:key(remote,'A',False))
at(33.5,lambda:check('client_acceleration_steering',(sv.get_actor_location()-state['pos']).length()>300 and abs(sv.get_actor_rotation().yaw-state['yaw'])>1,sample()))
at(33.6,lambda:replicate('client_drive_replicated'))
at(33.7,lambda:check('host_passenger_attached',(hp.get_actor_location()-sv.get_actor_location()).length()<250,[hp.get_actor_location(),sv.get_actor_location()]))
at(34,lambda:(key(remote,'W',False),key(remote,'SpaceBar',True)))
at(39,lambda:check('client_handbrake_stops',sv.get_velocity().length()<150,sv.get_velocity()))
exit(40,host)
at(41,lambda:check('host_passenger_exit',seats(sv)['PassengerSeat'] is None and agree(),sample()))
at(42,lambda:(key(remote,'SpaceBar',False),state.update(pos=sv.get_actor_location()),key(remote,'S',True)))
at(45,lambda:key(remote,'S',False))
at(45.2,lambda:check('client_reverse',(sv.get_actor_location()-state['pos']).length()>150,sample()))
at(45.3,lambda:key(remote,'SpaceBar',True))
at(50,lambda:replicate('reverse_and_stop_replicated'))
exit(51,remote)
at(52,lambda:check('client_exit_restores_character',remote.get_controlled_pawn()==rp and all(o is None for o in seats(sv).values()) and agree() and rp.get_actor_location().z>85,[rp.get_actor_location(),sample()]))
at(52.2,lambda:key(remote,'SpaceBar',False))
enter(53,host,True)
blockers=sorted([a for a in unreal.GameplayStatics.get_all_actors_of_class(server,unreal.StaticMeshActor) if a.get_actor_label().startswith('Gate2_ExitBlocker')],key=lambda a:a.get_actor_label())
def block():
    offsets=[unreal.Vector(253,-300,0),unreal.Vector(153,-300,0),unreal.Vector(353,-300,0),unreal.Vector(-450,0,0),unreal.Vector(0,-350,0),unreal.Vector(0,350,0)]
    state['blocks']=[a.get_actor_location() for a in blockers];state['block_modes']=[a.get_component_by_class(unreal.StaticMeshComponent).get_collision_enabled() for a in blockers]
    for a in blockers:a.get_component_by_class(unreal.StaticMeshComponent).set_collision_enabled(unreal.CollisionEnabled.QUERY_ONLY)
    for a,off in zip(blockers,offsets):
        p=sv.get_actor_transform().transform_location(off);p.z=125;a.set_actor_location(p,False,True)
def unblock():
    for a,p,mode in zip(blockers,state['blocks'],state['block_modes']):
        a.set_actor_location(p,False,True);a.get_component_by_class(unreal.StaticMeshComponent).set_collision_enabled(mode)
at(56,block);exit(57,host)
at(58,lambda:check('blocked_exits_retain_seat',host.get_controlled_pawn()==sv and seats(sv)['DriverSeat']==hp,sample()))
at(59,unblock);exit(60,host)
at(61,lambda:check('clear_exit_after_block_removed',host.get_controlled_pawn()==hp and seats(sv)['DriverSeat'] is None and agree(),sample()))
def finish():
    for pc in [host,remote]:
        for k in ['E','W','S','A','D','SpaceBar']:key(pc,k,False)
    with open('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate3Validation/integration_regression.json','w') as f:json.dump(results,f,indent=2)
    json.dump(diags,open('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate3Validation/integration_drivetrain.json','w'),indent=2)
    unreal.unregister_slate_post_tick_callback(handle);unreal.log('GATE3_INTEGRATION_MULTI_DONE')
at(62,finish)
events.sort(key=lambda e:e[0]);elapsed=0;idx=0
def tick(dt):
    global elapsed,idx,sample_acc
    elapsed+=dt;sample_acc+=dt
    try:
        while idx<len(events) and elapsed>=events[idx][0]:f=events[idx][1];idx+=1;f()
        if sample_acc>.1:
            sample_acc=0;diags.append({'t':elapsed,'velocity':str(sv.get_velocity()),'speed':sv.get_velocity().length(),'forward_speed':m.get_forward_speed(),'gear':m.get_current_gear(),'target_gear':m.get_target_gear(),'rpm':m.get_engine_rotation_speed(),'throttle':m.get_throttle_input(),'brake':m.get_brake_input(),'handbrake':m.get_handbrake_input(),'rotation':str(sv.get_actor_rotation()),'wheel_states':[str(unreal.ChaosWheeledVehicleMovementComponent.break_wheel_status(m.get_wheel_state(i))) for i in range(4)]})
    except Exception as e:
        unreal.log_error('GATE3_INTEGRATION_MULTI_ERROR '+str(e));finish()
handle=unreal.register_slate_post_tick_callback(tick)






