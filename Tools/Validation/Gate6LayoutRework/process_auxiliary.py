"""Rear seating, moving pantry UI, exterior contention and ladder real-input paths.
Only initial/isolated exterior approach fixtures and item seeding use authority helpers.
No seat, rest, door, transfer or climb gameplay RPC shortcut is called.
"""
import unreal,json,time,os
from pathlib import Path
B=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate6LayoutRework')
session=json.loads((B/'session.json').read_text());config=session['config'];start=session['start']
w=next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='Gate6FuelElectricalTest' and unreal.GameplayStatics.get_player_controller(w,0) and unreal.GameplayStatics.get_player_controller(w,0).get_controlled_pawn())
authority=unreal.GameplayStatics.get_game_mode(w) is not None
pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn()
other=next(c for c in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSurvivorCharacter) if c!=p)
hp=p if authority else other;cp=other if authority else p
isdriver=authority==(config['driver']=='host');dp=p if isdriver else other;wp=other if isdriver else p
v=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSystemsMotorhome)[0]
driver=next(s for s in v.get_seats() if s.get_editor_property('bDriverSeat'))
passenger=next(s for s in v.get_seats() if not s.get_editor_property('bDriverSeat') and not s.get_editor_property('bInteriorOnly'))
front=v.get_editor_property('DinetteFrontSeat');rear=v.get_editor_property('DinetteRearSeat')
entries=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVVehicleEntryPoint)
def entry(seat,outside):return next(a for a in entries if a.get_editor_property('Seat')==seat and (abs(v.get_actor_transform().inverse_transform_location(a.get_actor_location()).y)>100)==outside)
de=entry(driver,True);pe=entry(passenger,True);fe=entry(front,False);re=entry(rear,False)
door=v.get_editor_property('HouseDoor')
exitpoint=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVInteriorAccessPoint) if not a.get_editor_property('bEnter'))
pantry=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVStoragePoint) if str(a.get_editor_property('Container').get_editor_property('DisplayName'))=='Pantry')
exterior=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVExteriorStoragePoint) if str(a.get_editor_property('DoorPartName'))=='Art_RV_Van_Compartment_01')
ladder=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVLadder)[0]
events=[];idx=0;results=[];samples=[];active=True;nextsample=0;input_frame=0;pulses={}
def at(t,fn):events.append((t,fn))
def check(name,ok,detail=''):
    row={'case':name,'pass':bool(ok),'detail':str(detail)};results.append(row);unreal.log('AUX_NET '+json.dumps(row))
def cmd(text):unreal.SystemLibrary.execute_console_command(pc,text,pc)
def key(k,on):cmd('Input.'+('+' if on else '-')+'key '+k)
def tap(t,k,role=None):
    def press():
        if role is None or (role=='driver' and isdriver) or (role=='walker' and not isdriver) or (role=='host' and authority) or (role=='client' and not authority):
            unreal.RVInteriorMotorhome.dispatch_development_key(pc,k,True);pulses[k]=(time.time()+.15,input_frame+3)
    at(t,press)
def local(c):
    q=v.get_actor_transform().inverse_transform_location(c.get_actor_location());return [q.x,q.y,q.z]
def aim(a):
    point=a.get_editor_property('DoorCollision').get_world_location() if isinstance(a,unreal.RVInteractiveDoor) else a.get_actor_location()
    pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p.get_actor_location()+unreal.Vector(0,0,p.get_editor_property('BaseEyeHeight')),point))
def inventory(c):return c.get_component_by_class(unreal.RVInventoryComponent)
def quantity(component):return sum(item.quantity for item in component.get_items())
def seed(component,definition):
    item=unreal.RVItemInstance();item.set_editor_property('Id',unreal.GuidLibrary.new_guid());item.set_editor_property('Definition',unreal.load_asset('/Game/Items/DA_'+definition));item.set_editor_property('Condition',.62)
    component.add_authority(item)
def place(c,xyz):
    if authority:c.set_actor_location(v.get_actor_transform().transform_location(unreal.Vector(*xyz)),False,True)
def walking(c):return c.get_editor_property('SeatedVehicle') is None and c.get_component_by_class(unreal.CharacterMovementComponent).get_editor_property('MovementMode')==unreal.MovementMode.MOVE_WALKING
def setup():
    cmd('t.MaxFPS 60');cmd('t.IdleWhenNotForeground 0')
    if authority:
        for character,a,side in [(dp,de,-1),(wp,pe,1)]:
            q=v.get_actor_transform().inverse_transform_location(a.get_actor_location());place(character,(q.x,q.y+side*125,100))
        seed(inventory(wp),'Water')
at(0,setup);at(1,lambda:aim(de if isdriver else pe));at(1.2,lambda:key('E',True));at(2.1,lambda:key('E',False))
at(3.5,lambda:check('normal_E_initial_seats',driver.get_editor_property('Occupant')==dp and passenger.get_editor_property('Occupant')==wp))
tap(4,'Three','walker');at(5.5,lambda:check('normal_3_standing',walking(wp)))
at(6,lambda:key('W',True) if isdriver else None)
at(7,lambda:aim(fe) if not isdriver else None);at(7.2,lambda:key('E',True) if not isdriver else None);at(8.1,lambda:key('E',False) if not isdriver else None)
at(9,lambda:check('moving_front_bench_native_E',front.get_editor_property('Occupant')==wp and v.get_velocity().length()>150,local(wp)))
tap(9.5,'E','walker');at(10.8,lambda:check('moving_front_bench_stand',walking(wp) and wp.get_component_by_class(unreal.RVPassengerReferenceFrameComponent).get_editor_property('ReferenceFrame')==v,local(wp)))
at(11,lambda:aim(re) if not isdriver else None);at(11.2,lambda:key('E',True) if not isdriver else None);at(12.1,lambda:key('E',False) if not isdriver else None)
at(13,lambda:check('moving_rear_bench_native_E',rear.get_editor_property('Occupant')==wp,local(wp)))
tap(13.5,'E','walker');at(14.8,lambda:check('moving_rear_bench_stand',walking(wp) and wp.get_component_by_class(unreal.RVPassengerReferenceFrameComponent).get_editor_property('ReferenceFrame')==v,local(wp)))
at(15,lambda:aim(pantry) if not isdriver else None);at(15.2,lambda:key('E',True) if not isdriver else None);at(16.1,lambda:key('E',False) if not isdriver else None)
def pantry_view_check():
    if authority or not isdriver:
        check('moving_pantry_native_E',inventory(wp).get_editor_property('OpenContainer')==pantry.get_editor_property('Container'))
    else:
        # OpenContainer is intentionally owner-only; shared contents below are public.
        check('other_player_pantry_view_is_private',inventory(wp).get_editor_property('OpenContainer') is None)
at(17,pantry_view_check)
at(17,lambda:key('A',True) if isdriver else None)
tap(17.5,'T','walker');at(19,lambda:check('moving_turn_transfer_to_pantry_native_T',quantity(pantry.get_editor_property('Container'))==1 and quantity(inventory(wp))==0))
at(19,lambda:key('A',False) if isdriver else None)
tap(19.5,'Tab','walker');tap(20.5,'T','walker')
at(22,lambda:check('moving_transfer_back_native_Tab_T',quantity(pantry.get_editor_property('Container'))==0 and quantity(inventory(wp))==1 and abs(inventory(wp).get_items()[0].condition-.62)<.001,{'pantry':quantity(pantry.get_editor_property('Container')),'player':quantity(inventory(wp)),'feedback':inventory(wp).get_editor_property('Feedback'),'open':str(inventory(wp).get_editor_property('OpenContainer'))}))
tap(22.5,'I','walker')
at(23,lambda:key('W',False) if isdriver else None);at(23.1,lambda:key('S',True) if isdriver else None);at(29,lambda:key('S',False) if isdriver else None)
at(29.2,lambda:key('SpaceBar',True) if isdriver else None)
at(34,lambda:key('SpaceBar',False) if isdriver else None)
at(35,lambda:check('parked_before_exterior',v.get_velocity().length()<10,v.get_velocity().length()))
tap(35.5,'Three','driver');at(37,lambda:check('normal_3_driver_aisle',walking(dp)))
at(37.5,lambda:aim(door) if isdriver else None);at(37.7,lambda:key('E',True) if isdriver else None);at(38.6,lambda:key('E',False) if isdriver else None)
at(39.5,lambda:check('door_open_shared_state',door.get_editor_property('bOpen')))
def walker_front():
    if not isdriver:pc.set_control_rotation(unreal.Rotator(yaw=v.get_actor_rotation().yaw));key('W',True)
at(40,walker_front);at(40.8,lambda:key('W',False) if not isdriver else None)
at(42,lambda:aim(exitpoint));at(42.2,lambda:key('E',True));at(43.1,lambda:key('E',False))
at(44.5,lambda:check('normal_E_side_exit_both_players',walking(dp) and walking(wp) and abs(local(dp)[1])>170 and abs(local(wp)[1])>170,{'driver':local(dp),'walker':local(wp)}))
def exterior_approach():
    if authority:
        q=v.get_actor_transform().inverse_transform_location(exterior.get_actor_location());side=1 if q.y>0 else -1
        place(hp,(q.x-45,side*300,75));place(cp,(q.x+45,side*300,75));seed(exterior.get_editor_property('Container'),'Tool')
at(46,exterior_approach);at(47,lambda:aim(exterior));at(47.2,lambda:key('E',True));at(48.1,lambda:key('E',False))
at(49.5,lambda:check('shared_exterior_native_E',inventory(p).get_editor_property('OpenContainer')==exterior.get_editor_property('Container'),{'expected':str(exterior.get_editor_property('Container')),'actual':str(inventory(p).get_editor_property('OpenContainer')),'feedback':inventory(p).get_editor_property('Feedback')}))
tap(50,'Tab','driver') # driver UI was fresh; walker remains on container panel from pantry Tab.
tap(51,'T')
def conserved():
    records=[item for c in [inventory(hp),inventory(cp),exterior.get_editor_property('Container')] for item in c.get_items() if str(item.definition.get_editor_property('CatalogId'))=='Tool']
    moved=any(str(item.definition.get_editor_property('CatalogId'))=='Tool' for c in [inventory(hp),inventory(cp)] for item in c.get_items())
    check('shared_exterior_contention_no_duplicate_native_T',moved and sum(item.quantity for item in records)==1 and len({unreal.GuidLibrary.conv_guid_to_string(item.id) for item in records})==len(records),[str(item.id) for item in records])
at(53,conserved);tap(53.5,'I')
def ladder_approach():
    if authority:
        q=v.get_actor_transform().inverse_transform_location(de.get_actor_location());place(hp,(q.x,q.y-125,100));place(cp,(-520,75,75))
at(55,ladder_approach);at(56,lambda:aim(de if authority else ladder));at(56.2,lambda:key('E',True));at(57.1,lambda:key('E',False))
at(58.5,lambda:check('native_E_client_ladder_host_driver',ladder.get_editor_property('Occupant')==cp and driver.get_editor_property('Occupant')==hp,local(cp)))
at(59,lambda:key('W',True))
at(61.2,lambda:key('W',False) if not authority else None)
def top_check():
    q=local(cp);height=cp.get_actor_location().z-ladder.bottom_world().z if hasattr(ladder,'bottom_world') else q[2]-ladder.get_editor_property('BottomLocal').z
    check('native_W_controlled_ladder_top',ladder.get_editor_property('Occupant')==cp and 155<height<195,{'position':q,'height':height})
    check('occupied_ladder_prevents_driving',v.get_velocity().length()<10,v.get_velocity().length())
at(62.5,top_check);tap(63,'E','client');at(64,lambda:check('top_has_no_unvalidated_roof_exit',ladder.get_editor_property('Occupant')==cp))
at(64.5,lambda:key('S',True) if not authority else None);at(66.7,lambda:key('S',False) if not authority else None)
at(66.8,lambda:key('W',False) if authority else None);tap(67.5,'E','client')
at(69,lambda:check('native_S_E_bottom_exit_restores_world_movement',ladder.get_editor_property('Occupant') is None and walking(cp) and str(cp.get_component_by_class(unreal.CapsuleComponent).get_collision_enabled()).find('QUERY_AND_PHYSICS')>=0,local(cp)))
at(69.2,lambda:key('W',True) if authority else None);at(70.2,lambda:key('W',False) if authority else None)
at(70.3,lambda:check('ladder_exit_releases_drive_lock',v.get_velocity().length()>10,v.get_velocity().length()))
at(70.4,lambda:key('SpaceBar',True) if authority else None)
def walk_away():
    if not authority:pc.set_control_rotation(unreal.Rotator(yaw=v.get_actor_rotation().yaw+180));key('W',True)
at(70.5,walk_away);at(70.8,lambda:key('W',False) if not authority else None)
at(72,lambda:check('ladder_world_walk_away',walking(cp) and local(cp)[0]<-480,local(cp)))
def finish():
    global active
    if not active:return
    for k in ['E','W','S','A','T','Tab','I','Three','SpaceBar']:
        key(k,False);unreal.RVInteriorMotorhome.dispatch_development_key(pc,k,False)
    role='server' if authority else 'client'
    (B/(config['name']+'_'+role+'.json')).write_text(json.dumps({'pid':os.getpid(),'role':role,'config':config,'results':results,'samples':samples},indent=2),encoding='utf-8')
    active=False;unreal.unregister_slate_post_tick_callback(h)
    from runner_runtime import release_runners
    release_runners()
at(74,finish);events.sort(key=lambda e:e[0])
def tick(dt):
    global idx,nextsample,hp,cp,dp,wp,input_frame
    if not active:return
    input_frame+=1
    if not authority:
        remote=next((c for c in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSurvivorCharacter) if c!=p),None)
        if remote:hp=remote;cp=p;dp=p if isdriver else remote;wp=remote if isdriver else p
    t=time.time()-start
    if t<0:return
    try:
        for k,(deadline,frame) in list(pulses.items()):
            if time.time()>=deadline and input_frame>=frame:unreal.RVInteriorMotorhome.dispatch_development_key(pc,k,False);del pulses[k]
        while idx<len(events) and t>=events[idx][0] and not pulses:
            fn=events[idx][1];idx+=1;terminating=fn.__name__=='finish';fn()
            if terminating:return
            if not active:return
        if t>=nextsample:
            nextsample=t+.1;samples.append({'t':t,'host':local(hp),'client':local(cp),'speed':v.get_velocity().length(),'ladder':str(ladder.get_editor_property('Occupant')),'inventory_feedback':inventory(wp).get_editor_property('Feedback'),'open_container':str(inventory(wp).get_editor_property('OpenContainer'))})
    except Exception as e:check('exception',False,repr(e));finish()
h=unreal.register_slate_post_tick_callback(tick)
