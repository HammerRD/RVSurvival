"""Separate-process real input-path checks. RPCs are never called as control shortcuts.
Initial approach placement is fixture-only; all transitions are normal E/V/1/2/3/Z/R inputs.
The runner is released before PIE stops, using the established runner_runtime lifecycle.
"""
import unreal,json,time,os
from pathlib import Path
B=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate6LayoutRework')
session=json.loads((B/'session.json').read_text());config=session['config'];start=session['start']
w=next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='Gate6FuelElectricalTest' and unreal.GameplayStatics.get_player_controller(w,0) and unreal.GameplayStatics.get_player_controller(w,0).get_controlled_pawn())
authority=unreal.GameplayStatics.get_game_mode(w) is not None
pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn()
other=next(c for c in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSurvivorCharacter) if c!=p)
v=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSystemsMotorhome)[0]
driver=next(s for s in v.get_seats() if s.get_editor_property('bDriverSeat'))
passenger=next(s for s in v.get_seats() if not s.get_editor_property('bDriverSeat') and not s.get_editor_property('bInteriorOnly'))
isdriver=authority==(config['driver']=='host')
dp=p if isdriver else other;wp=other if isdriver else p
entries=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVVehicleEntryPoint)
de=next(a for a in entries if a.get_editor_property('Seat')==driver and abs(v.get_actor_transform().inverse_transform_location(a.get_actor_location()).y)>100)
pe=next(a for a in entries if a.get_editor_property('Seat')==passenger and abs(v.get_actor_transform().inverse_transform_location(a.get_actor_location()).y)>100)
door=v.get_editor_property('HouseDoor')
bed=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVRestPoint) if str(a.get_editor_property('DisplayName'))=='Rear bed')
events=[];idx=0;results=[];samples=[];active=True;nextsample=0;bad_seated=0;below_floor=0;observer_camera=None;input_frame=0;pulses={}
def at(t,fn):events.append((t,fn))
def check(name,ok,detail=''):
    row={'case':name,'pass':bool(ok),'detail':str(detail)};results.append(row);unreal.log('LAYOUT_NET '+json.dumps(row))
def cmd(text):unreal.SystemLibrary.execute_console_command(pc,text,pc)
def key(k,on):cmd('Input.'+('+' if on else '-')+'key '+k)
def tap(t,k,for_driver=None):
    def press():
        if for_driver is None or isdriver==for_driver:
            unreal.RVInteriorMotorhome.dispatch_development_key(pc,k,True);pulses[k]=(time.time()+.15,input_frame+3)
    at(t,press)
def local(c):
    q=v.get_actor_transform().inverse_transform_location(c.get_actor_location());return [q.x,q.y,q.z]
def aim(a):
    point=a.get_editor_property('DoorCollision').get_world_location() if isinstance(a,unreal.RVInteractiveDoor) else a.get_actor_location()
    pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p.get_actor_location()+unreal.Vector(0,0,p.get_editor_property('BaseEyeHeight')),point))
def setup():
    cmd('t.MaxFPS 60');cmd('t.IdleWhenNotForeground 0');cmd('rv.Needs.AllowDebug 1')
    if authority:
        for character,entry,side in [(dp,de,-1),(wp,pe,1)]:
            q=v.get_actor_transform().inverse_transform_location(entry.get_actor_location())
            character.set_actor_location(v.get_actor_transform().transform_location(unreal.Vector(q.x,q.y+side*125,100)),False,True)
def occupants(d,pas):return driver.get_editor_property('Occupant')==d and passenger.get_editor_property('Occupant')==pas
def walking(character):
    m=character.get_component_by_class(unreal.CharacterMovementComponent)
    return character.get_editor_property('SeatedVehicle') is None and m.get_editor_property('MovementMode')==unreal.MovementMode.MOVE_WALKING and local(character)[2]>140
at(0,setup);at(1,lambda:aim(de if isdriver else pe));at(1.3,lambda:key('E',True));at(2.2,lambda:key('E',False))
at(3.5,lambda:check('normal_E_host_client_seats',occupants(dp,wp)))
tap(4,'Two',True);tap(4,'One',False)
at(5.5,lambda:check('normal_1_2_occupied_seat_rejection',occupants(dp,wp)))
tap(6,'Three',False)
at(7.5,lambda:check('normal_3_passenger_to_aisle',walking(wp),local(wp)))
for n in range(20):
    t=8+n*2.2;tap(t,'V',True)
    at(t+.75,lambda n=n:check('normal_V_driver_to_passenger_'+str(n+1),occupants(None,dp),local(dp)))
    tap(t+1,'One',True)
    at(t+1.85,lambda n=n:check('normal_1_return_driver_'+str(n+1),occupants(dp,None),local(dp)))
at(52.5,lambda:wp.get_component_by_class(unreal.RVPassengerReferenceFrameComponent).reset_diagnostics())
at(53,lambda:key('W',True) if isdriver else None)
at(58,lambda:check('host_or_client_driving',v.get_velocity().length()>150,v.get_velocity().length()))
tap(58.2,'V',True)
at(59.5,lambda:check('moving_V_rejected_without_release',occupants(dp,None),local(dp)))
def walk_rear():
    if not isdriver:pc.set_control_rotation(unreal.Rotator(yaw=v.get_actor_rotation().yaw+180));key('W',True)
at(60,walk_rear);at(61.5,lambda:key('W',False) if not isdriver else None)
at(62.5,lambda:check('moving_walk_to_actual_bed_foot',walking(wp) and -145<local(wp)[0]<-80 and abs(local(wp)[1])<35,local(wp)))
at(63,lambda:key('A',True) if isdriver else None);at(65,lambda:key('A',False) if isdriver else None)
at(64,lambda:check('gentle_turn_passenger_floor',walking(wp),local(wp)))
at(66,lambda:key('W',False) if isdriver else None);at(66.1,lambda:key('S',True) if isdriver else None)
at(72,lambda:key('S',False) if isdriver else None);at(72.2,lambda:key('SpaceBar',True) if isdriver else None)
at(79,lambda:check('braked_before_bed',v.get_velocity().length()<50,v.get_velocity().length()))
def movement_diagnostics():
    frame=wp.get_component_by_class(unreal.RVPassengerReferenceFrameComponent)
    detail={name:frame.get_editor_property(name) for name in ['CorrectionCount','MaxCorrectionCm','MaxLocalStepCm','FrameChanges','BaseChanges']}
    check('moving_corrections_within_existing_gate3_bound',detail['MaxCorrectionCm']<=(75 if config.get('network') else 30),detail)
at(79.5,movement_diagnostics)
at(79.3,lambda:key('SpaceBar',False) if isdriver else None)
tap(79.6,'V',True)
at(81.2,lambda:check('recently_stopped_native_V_passenger',occupants(None,dp),local(dp)))
tap(81.5,'One',True)
at(83,lambda:check('recently_stopped_native_1_driver',occupants(dp,None),local(dp)))
def observer_view():
    global observer_camera
    if not isdriver:return
    # Test-only native camera; never changes a character transform or possession.
    position=v.get_actor_transform().transform_location(unreal.Vector(-115,0,245))
    rotation=unreal.MathLibrary.find_look_at_rotation(position,v.get_actor_transform().transform_location(unreal.Vector(-245,48,202)))
    observer_camera=unreal.RVInteriorMotorhome.create_development_observer_camera(w,position,rotation)
    assert observer_camera is not None
    pc.set_view_target_with_blend(observer_camera,0)
def observer_restore():
    global observer_camera
    if observer_camera:
        pc.set_view_target_with_blend(pc.get_controlled_pawn(),0);observer_camera.destroy_actor();observer_camera=None
at(86.6,observer_view)
at(86.95,lambda:cmd('shot filename='+str(B/(config['name']+('_server' if authority else '_client')+'_bed.png')).replace('\\','/')+' -nosuffix'))
at(88,observer_restore)
for n in range(4):
    t=85+n*7
    at(t,lambda:aim(bed) if not isdriver else None)
    at(t+.2,lambda:key('E',True) if not isdriver else None);at(t+1.1,lambda:key('E',False) if not isdriver else None)
    at(t+1.8,lambda n=n:check('normal_E_bed_reserved_'+str(n),bed.get_editor_property('Occupant')==wp.get_editor_property('PlayerState'),local(wp)))
    tap(t+2,'Z',False)
    at(t+3.5,lambda n=n:check('normal_Z_sleep_'+str(n),wp.get_editor_property('PlayerState').get_component_by_class(unreal.RVNeedsComponent).get_editor_property('State').rest_mode==unreal.RVRestMode.SLEEPING,str(wp.get_editor_property('PlayerState').get_component_by_class(unreal.RVNeedsComponent).get_editor_property('State').rest_mode)))
    tap(t+4,'R' if n%2==0 else 'E',False)
    at(t+6,lambda n=n:check('normal_R_E_safe_wake_'+str(n),walking(wp) and bed.get_editor_property('Occupant') is None,local(wp)))
def finish():
    global active
    if not active:return
    observer_restore()
    for k in ['E','W','S','A','V','One','Two','Three','Z','R','SpaceBar']:
        key(k,False);unreal.RVInteriorMotorhome.dispatch_development_key(pc,k,False)
    check('zero_seated_walking_or_falling_samples',bad_seated==0,bad_seated)
    check('zero_interior_below_floor_samples',below_floor==0,below_floor)
    role='server' if authority else 'client'
    (B/(config['name']+'_'+role+'.json')).write_text(json.dumps({'pid':os.getpid(),'role':role,'config':config,'results':results,'samples':samples},indent=2),encoding='utf-8')
    active=False;unreal.unregister_slate_post_tick_callback(h)
    from runner_runtime import release_runners
    release_runners() # release all temporary world/actor wrappers before PIE teardown
at(114,finish);events.sort(key=lambda e:e[0])
def tick(dt):
    global idx,nextsample,bad_seated,below_floor,dp,wp,input_frame
    if not active:return
    input_frame+=1
    # Reacquire remote characters if native relevancy recreated a wrapper.
    if not authority:
        remote=next((c for c in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSurvivorCharacter) if c!=p),None)
        if remote:dp=p if isdriver else remote;wp=remote if isdriver else p
    t=time.time()-start
    if t<0:return
    try:
        for k,(deadline,frame) in list(pulses.items()):
            if time.time()>=deadline and input_frame>=frame:unreal.RVInteriorMotorhome.dispatch_development_key(pc,k,False);del pulses[k]
        # A stalled frame must not dispatch a key and its observation/next key
        # before PlayerTick has had several opportunities to process it.
        while idx<len(events) and t>=events[idx][0] and not pulses:
            fn=events[idx][1];idx+=1;terminating=fn.__name__=='finish';fn()
            if terminating:return # runner globals have been cleared
            if not active:return
        if t>7 and t>=nextsample:
            nextsample=t+.04
            row={'t':t,'speed':v.get_velocity().length(),'driver':local(dp),'walker':local(wp),'rest':str(wp.get_editor_property('PlayerState').get_component_by_class(unreal.RVNeedsComponent).get_editor_property('State').rest_mode)}
            for c in [dp,wp]:
                mode=c.get_component_by_class(unreal.CharacterMovementComponent).get_editor_property('MovementMode')
                if c.get_editor_property('SeatedVehicle') and mode!=unreal.MovementMode.MOVE_NONE:bad_seated+=1
                if local(c)[2]<120:below_floor+=1
            samples.append(row)
    except Exception as e:check('exception',False,repr(e));finish()
h=unreal.register_slate_post_tick_callback(tick)
