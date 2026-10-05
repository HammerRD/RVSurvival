import unreal,json
B='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate3Validation/'
exec(open(B+'suite.py').read().split('for pc in [host,client]:cmd')[0],globals())
assert role=='host'
state={}
for pc in [host,client]:cmd(pc,'t.MaxFPS 60');cmd(pc,'t.IdleWhenNotForeground 0')
at(0,setup);at(.6,lambda:move_y(10));at(2.9,stop_walk)
at(1,lambda:key(driver,'E',True));at(2,lambda:key(driver,'E',False))
at(3,lambda:check('natural_entry_before_disconnect',frame_ok(),local(wv,wp)))
at(3.2,lambda:move(-145));at(6,stop_walk);at(7,lambda:key(host,'W',True))
at(10,lambda:aim_station('Medical'))
at(10.1,lambda:check('moving_station_prompt_before_disconnect', 'Medical' in str(wp.get_component_by_class(unreal.load_class(None,'/Script/RVSurvival.RVInteractionComponent')).get_prompt()) and frame_ok() and sv.get_velocity().length()>1000,local(wv,wp)))
at(10.2,lambda:key(client,'E',True));at(10.4,lambda:cmd(client,'disconnect'))
at(14,lambda:check('standing_passenger_destroyed',not unreal.SystemLibrary.is_valid(sp) and len(unreal.GameplayStatics.get_all_actors_of_class(sw,CC))==1,'remaining='+str(len(unreal.GameplayStatics.get_all_actors_of_class(sw,CC)))))
at(14.1,lambda:check('disconnect_hold_no_late_completion',ss['Medical'].get_editor_property('InteractionCount')==station_initial['Medical'],ss['Medical'].get_editor_property('InteractionCount')))
at(14.2,lambda:check('driver_and_vehicle_survive',unreal.SystemLibrary.is_valid(sv) and host.get_controlled_pawn()==sv and all(not s.get_editor_property('Occupant') for s in sv.get_seats() if not s.get_editor_property('bDriverSeat')),'seat cleanup'))
at(14.3,lambda:(key(host,'W',False),key(host,'S',True)))
at(17.3,lambda:(key(host,'S',False),key(host,'SpaceBar',True)))
at(19,lambda:key(host,'E',True));at(19.2,lambda:key(host,'E',False))
at(20,lambda:check('driver_exit_after_standing_disconnect',host.get_controlled_pawn()==hp and all(not s.get_editor_property('Occupant') for s in sv.get_seats()),'possession'))
at(20.2,lambda:key(host,'SpaceBar',False))
at(21,lambda:(state.update(pos=hp.get_actor_location()),key(host,'W',True)));at(21.5,lambda:key(host,'W',False))
at(22,lambda:check('outside_walking_after_disconnect',host.get_controlled_pawn()==hp and hp.get_component_by_class(unreal.CharacterMovementComponent).get_editor_property('movement_mode')==unreal.MovementMode.MOVE_WALKING and (hp.get_actor_location()-state['pos']).length()>50,hp.get_actor_location()))
at(22.2,lambda:(state.update(z=hp.get_actor_location().z),key(host,'SpaceBar',True)))
at(22.4,lambda:check('outside_jump_after_disconnect',hp.get_actor_location().z>state['z']+20,hp.get_actor_location()))
at(22.5,lambda:key(host,'SpaceBar',False))
def finish():
 for k in ['W','S','A','D','E','SpaceBar']:key(host,k,False)
 json.dump(results,open(B+'standing_disconnect.json','w'),indent=2)
 unreal.unregister_slate_post_tick_callback(handle);unreal.log('GATE3_DISCONNECT_DONE')
at(24,finish);events=[(t+3 if t>=19 else t,f) for t,f in events];at(21,lambda:check('fully_stopped_before_exit',sv.get_velocity().length()<150,sv.get_velocity()));events.sort(key=lambda e:e[0]);elapsed=0;idx=0
def tick(dt):
 global elapsed,idx
 elapsed+=dt
 try:
  while idx<len(events) and elapsed>=events[idx][0]:f=events[idx][1];idx+=1;f()
  if target is not None and elapsed<10.4:
   axis,value=target;d=value-local(wv,wp)[axis];walk_key('W',d>8 if axis==0 else d< -8);walk_key('S',d< -8 if axis==0 else d>8)
 except Exception as e:unreal.log_error('GATE3_DISCONNECT_ERROR '+str(e));finish()
handle=unreal.register_slate_post_tick_callback(tick)
