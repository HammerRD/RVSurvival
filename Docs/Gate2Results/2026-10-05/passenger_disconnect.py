import unreal,json,time
base='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate2Validation/'
exec(open(base+'process.py').read().split('at(0,lambda:')[0],globals())
at(0,lambda:check('fresh_seats',all(o is None for o in seats().values()),seats()))
enter(1,True,'host')
at(4,lambda:check('host_driver',bool(seats()['DriverSeat']),seats()))
enter(5,False,'client')
at(8,lambda:check('remote_passenger',all(bool(o) for o in seats().values()),seats()))
def finish():
    json.dump(results,open(base+'passenger_disconnect_'+role+'.json','w'),indent=2)
    unreal.unregister_slate_post_tick_callback(handle)
    unreal.log('GATE2_PASSENGER_DONE '+role)
if not host:
    at(9,lambda:(finish(),cmd('disconnect')))
else:
    at(11,lambda:check('passenger_disconnect_frees_only_passenger',unreal.SystemLibrary.is_valid(v) and seats()['DriverSeat']==pawn and seats()['PassengerSeat'] is None,seats()))
    exit(12,'host')
    at(14,lambda:check('host_exit_after_passenger_disconnect',pc.get_controlled_pawn()==pawn and all(o is None for o in seats().values()),seats()))
    at(15,lambda:(state.update(walk=pawn.get_actor_location()),key('W',True)))
    at(15.5,lambda:key('W',False))
    at(16,lambda:check('walking_input_restored_after_seats',(pawn.get_actor_location()-state['walk']).length()>50,pawn.get_actor_location()))
    at(17,lambda:(state.update(z=pawn.get_actor_location().z),key('SpaceBar',True)))
    at(17.2,lambda:check('jump_input_restored_after_seats',pawn.get_actor_location().z>state['z']+20,pawn.get_actor_location()))
    at(17.3,lambda:key('SpaceBar',False))
    at(19,finish)
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
    except Exception as e:unreal.log_error('GATE2_PASSENGER_ERROR '+str(e));finish()
handle=unreal.register_slate_post_tick_callback(tick)
