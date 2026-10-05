import unreal,json,time
base='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate2Validation/'
world=next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='Gate2VehicleTest' and unreal.GameplayStatics.get_player_controller(w,0) and unreal.GameplayStatics.get_player_controller(w,0).get_controlled_pawn())
pc=unreal.GameplayStatics.get_player_controller(world,0);pawn=pc.get_controlled_pawn()
host=unreal.GameplayStatics.get_game_mode(world) is not None;role='host' if host else 'client'
if not host:json.dump({'session':json.load(open(base+'session2.json'))['id']},open(base+'ready2.json','w'))
vc=unreal.load_class(None,'/Script/RVSurvival.RVMotorhome');ec=unreal.load_class(None,'/Script/RVSurvival.RVVehicleEntryPoint');chc=unreal.load_class(None,'/Script/RVSurvival.RVSurvivorCharacter')
v=unreal.GameplayStatics.get_all_actors_of_class(world,vc)[0]
results=[];samples={};state={};events=[];index=0;start_time=None
unreal.SystemLibrary.execute_console_command(world,'t.MaxFPS 60',pc)
try:initial_id=json.load(open(base+'schedule2.json')).get('id')
except:initial_id=None
def cmd(s):unreal.SystemLibrary.execute_console_command(world,s,pc)
def key(k,on):cmd('Input.'+('+' if on else '-')+'key '+k)
def seats():return {s.get_name():s.get_editor_property('Occupant') for s in v.get_seats()}
def snap(name):
    pos=v.get_actor_location();vel=v.get_velocity()
    samples[name]={'proxy_gravity_enabled':v.get_component_by_class(unreal.SkeletalMeshComponent).is_gravity_enabled(),'position':[pos.x,pos.y,pos.z],'velocity':[vel.x,vel.y,vel.z],'seats':{k:bool(o) for k,o in seats().items()},'pawn':pc.get_controlled_pawn().get_class().get_name() if pc.get_controlled_pawn() else None}
    unreal.log('GATE2_PROCESS_SAMPLE '+role+' '+name+' '+json.dumps(samples[name]))
def check(name,ok,detail):
    row={'case':name,'pass':bool(ok),'detail':str(detail)};results.append(row);unreal.log('GATE2_PROCESS_RESULT '+role+' '+json.dumps(row))
def phase_aim(driver,who):
    if host:
        target=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world,chc) if (a==pawn)==(who=='host'))
        entry=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world,ec) if a.get_editor_property('Seat').get_editor_property('bDriverSeat')==driver)
        pos=entry.get_actor_location()+v.get_actor_right_vector()*(-180 if driver else 180);pos.z=92
        target.set_actor_location(pos,False,True)
    if role==who:
        state['aim_driver']=driver
def align():
    if 'aim_driver' not in state:return
    driver=state.pop('aim_driver')
    entry=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world,ec) if a.get_editor_property('Seat').get_editor_property('bDriverSeat')==driver)
    # Aim from the intended fixture pose, not a client pose still awaiting a
    # CharacterMovement correction after the server teleports it between doors.
    pos=entry.get_actor_location()+v.get_actor_right_vector()*(-180 if driver else 180)
    pos.z=pawn.get_actor_location().z
    pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(pos+unreal.Vector(0,0,64),entry.get_actor_location()))
def at(t,f):events.append((t,f))
def enter(t,driver,who):
    at(t,lambda:phase_aim(driver,who));at(t+.8,align)
    at(t+1.2,lambda:key('E',True) if role==who else None);at(t+2.3,lambda:key('E',False) if role==who else None)
def exit(t,who):at(t,lambda:key('E',True) if role==who else None);at(t+.3,lambda:key('E',False) if role==who else None)
at(0,lambda:(check('fresh_empty',all(o is None for o in seats().values()),seats()),snap('fresh')))
enter(1,True,'host')
at(4,lambda:(check('host_driver',bool(seats()['DriverSeat']) and ((pc.get_controlled_pawn()==v)==host),seats()),snap('host_driver')))
enter(5,True,'client')
at(8,lambda:check('occupied_driver_rejects_client',bool(seats()['DriverSeat']) and (host or pc.get_controlled_pawn()==pawn),seats()))
enter(9,False,'client')
at(12,lambda:(check('host_driver_client_passenger',all(bool(o) for o in seats().values()),seats()),snap('both_host_driving')))
at(13,lambda:(state.update(pos=v.get_actor_location()),key('W',True) if host else None))
at(16,lambda:(check('host_drives',(v.get_actor_location()-state['pos']).length()>300,v.get_actor_location()),snap('host_drive')))
at(17,lambda:(key('W',False),key('SpaceBar',True)) if host else None)
at(22,lambda:(check('host_stops',v.get_velocity().length()<150,v.get_velocity()),snap('host_stopped')))
exit(23,'client');exit(25,'host')
at(26,lambda:(check('both_exit_free',all(o is None for o in seats().values()) and pc.get_controlled_pawn()==pawn,seats()),snap('both_exited')))
def reset():
    if not host:return
    v.get_component_by_class(unreal.load_class(None,'/Script/RVSurvival.RVVehicleMovementComponent')).stop_movement_immediately()
    v.set_actor_location(unreal.Vector(0,0,90),False,True);v.set_actor_rotation(unreal.Rotator(),True)
at(26.2,lambda:key('SpaceBar',False) if host else None);at(26.3,reset)
enter(28,True,'client')
at(31,lambda:(check('client_driver',bool(seats()['DriverSeat']) and ((pc.get_controlled_pawn()==v)==(not host)),seats()),snap('client_driver')))
enter(32,False,'host')
at(35,lambda:(check('client_driver_host_passenger',all(bool(o) for o in seats().values()),seats()),snap('both_client_driving')))
at(36,lambda:(state.update(pos=v.get_actor_location()),key('W',True) if not host else None))
at(39,lambda:(check('client_drives',(v.get_actor_location()-state['pos']).length()>300,v.get_actor_location()),snap('client_drive')))
at(40,lambda:(key('W',False),key('SpaceBar',True)) if not host else None)
at(45,lambda:(check('client_stops',v.get_velocity().length()<150,v.get_velocity()),snap('client_stopped')))
exit(46,'host')
at(47,lambda:check('passenger_exit_frees_seat',seats()['PassengerSeat'] is None,seats()))
def finish():
    json.dump({'results':results,'samples':samples},open(base+'process2_'+role+'.json','w'),indent=2)
    unreal.unregister_slate_post_tick_callback(handle);unreal.log('GATE2_PROCESS_DONE '+role)
if not host:
    at(48,lambda:(finish(),cmd('disconnect')))
else:
    at(50,lambda:(check('driver_disconnect_frees_seat_keeps_vehicle',unreal.SystemLibrary.is_valid(v) and all(o is None for o in seats().values()),seats()),snap('driver_disconnected')))
    enter(51,True,'host')
    at(54,lambda:check('host_reuses_disconnected_driver_seat',pc.get_controlled_pawn()==v and seats()['DriverSeat']==pawn,seats()))
    exit(55,'host');at(56,lambda:check('reused_seat_exits',pc.get_controlled_pawn()==pawn and all(o is None for o in seats().values()),seats()));at(57,finish)
    now=time.time();start_time=now+12;json.dump({'id':now,'start':start_time},open(base+'schedule2.json','w'))
events.sort(key=lambda e:e[0])
def tick(dt):
    global index,start_time
    try:
        if start_time is None:
            try:s=json.load(open(base+'schedule2.json'))
            except:return
            if s['id']==initial_id:return
            start_time=s['start']
        elapsed=time.time()-start_time
        while index<len(events) and elapsed>=events[index][0]:f=events[index][1];index+=1;f()
    except Exception as e:unreal.log_error('GATE2_PROCESS_ERROR '+role+' '+str(e));finish()
handle=unreal.register_slate_post_tick_callback(tick)
unreal.log('GATE2_PROCESS_READY '+role)


