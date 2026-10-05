import unreal,json
worlds=sorted([w for w in unreal.ObjectIterator(unreal.World) if '/Game/Maps/UEDPIE_' in w.get_path_name() and w.get_name()=='Gate2VehicleTest'],key=lambda w:w.get_path_name())
server,client=worlds;hpc=unreal.GameplayStatics.get_player_controller(server,0);cpc=unreal.GameplayStatics.get_player_controller(client,0)
vc=unreal.load_class(None,'/Script/RVSurvival.RVMotorhome');ec=unreal.load_class(None,'/Script/RVSurvival.RVVehicleEntryPoint');chc=unreal.load_class(None,'/Script/RVSurvival.RVSurvivorCharacter')
sv=unreal.GameplayStatics.get_all_actors_of_class(server,vc)[0];cv=unreal.GameplayStatics.get_all_actors_of_class(client,vc)[0]
hp=hpc.get_controlled_pawn();cp=cpc.get_controlled_pawn();sp=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(server,chc) if a!=hp)
entry=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(server,ec) if a.get_editor_property('Seat').get_editor_property('bDriverSeat'))
for p,pc,x in [(hp,hpc,-65),(sp,cpc,65)]:
    pos=entry.get_actor_location()+sv.get_actor_right_vector()*-180+sv.get_actor_forward_vector()*x;pos.z=92
    p.set_actor_location(pos,False,True);pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(pos+unreal.Vector(0,0,64),entry.get_actor_location()))
def key(pc,on):unreal.SystemLibrary.execute_console_command(pc,'Input.'+('+' if on else '-')+'key E',pc)
rows=[]
def result(name,ok,detail):row={'case':name,'pass':bool(ok),'detail':str(detail)};rows.append(row);unreal.log('GATE2_RACE '+json.dumps(row))
def verify():
    so=next(s for s in sv.get_seats() if s.get_editor_property('bDriverSeat')).get_editor_property('Occupant')
    co=next(s for s in cv.get_seats() if s.get_editor_property('bDriverSeat')).get_editor_property('Occupant')
    owned=[hpc.get_controlled_pawn()==sv,cpc.get_controlled_pawn()==cv]
    result('simultaneous_driver_claim_has_one_winner',sum(owned)==1 and so is not None and co is not None,[owned,so,co])
def leave():
    if hpc.get_controlled_pawn()==sv:key(hpc,True)
    elif cpc.get_controlled_pawn()==cv:key(cpc,True)
def finish():
    result('race_winner_exit_frees_driver',all(s.get_editor_property('Occupant') is None for s in sv.get_seats()),str(sv.get_seats()))
    json.dump(rows,open('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate2Validation/race.json','w'),indent=2)
    unreal.unregister_slate_post_tick_callback(handle)
def align():
    for p,pc in [(hp,hpc),(sp,cpc)]:pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p.get_actor_location()+unreal.Vector(0,0,64),entry.get_actor_location()))
events=[(.8,align),(1.5,lambda:(key(hpc,True),key(cpc,True))),(3,lambda:(key(hpc,False),key(cpc,False))),(3.5,verify),(4.5,leave),(4.8,lambda:(key(hpc,False),key(cpc,False))),(5.5,finish)]
t=0;i=0
def tick(dt):
    global t,i
    t+=dt
    try:
        while i<len(events) and t>=events[i][0]:f=events[i][1];i+=1;f()
    except Exception as e:unreal.log_error('GATE2_RACE_ERROR '+str(e));unreal.unregister_slate_post_tick_callback(handle)
handle=unreal.register_slate_post_tick_callback(tick)


