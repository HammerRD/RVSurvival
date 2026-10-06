import unreal,json
B='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate5Refinement/'
w=next(w for w in unreal.ObjectIterator(unreal.World) if 'UEDPIE_' in w.get_path_name() and w.get_name()=='Gate5SurvivalTest')
pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn();v=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVInteriorMotorhome)[0];m=p.get_component_by_class(unreal.CharacterMovementComponent);f=p.get_component_by_class(unreal.RVPassengerReferenceFrameComponent);cap=p.get_component_by_class(unreal.CapsuleComponent)
t=0;idx=0;acc=0;rows=[];checks=[];target=None;held=False;events=[];original_radius=cap.get_unscaled_capsule_radius();original_speed=m.get_editor_property('MaxWalkSpeed')
def pos():q=v.get_actor_transform().inverse_transform_location(p.get_actor_location());return [q.x,q.y,q.z]
def check(n,ok,d=''):r={'case':n,'pass':bool(ok),'detail':str(d)};checks.append(r);unreal.log('REFINE '+json.dumps(r))
def key(k,on):unreal.SystemLibrary.execute_console_command(pc,'Input.'+('+' if on else '-')+'key '+k,pc)
def stop():
 global target,held
 target=None
 if held:key('W',False);held=False
def nav(axis,val):
 global target
 stop();target=(axis,val)
def aim(a):stop();pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p.get_actor_location()+unreal.Vector(0,0,64),a.get_actor_location()))
def place(x,y):stop();p.set_actor_location(v.get_actor_transform().transform_location(unreal.Vector(x,y,110)),False,True)
def frame():return f.get_editor_property('ReferenceFrame')==v
access=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVInteriorAccessPoint);outside=next(a for a in access if a.get_editor_property('bEnter'));inside=next(a for a in access if not a.get_editor_property('bEnter'))
seats=v.get_seats();driver=next(s for s in seats if s.get_editor_property('bDriverSeat'));passenger=next(s for s in seats if not s.get_editor_property('bDriverSeat'))
ep=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVVehicleEntryPoint) if a.get_editor_property('Seat')==driver and abs(v.get_actor_transform().inverse_transform_location(a.get_actor_location()).y)<100)
def at(t,f):events.append((t,f))
at(0,lambda:(check('real_stepwell_layout',len(access)==2),check('step_height',m.get_editor_property('MaxStepHeight')>0,m.get_editor_property('MaxStepHeight')),place(92.4,300)))
at(.5,lambda:nav(1,0));at(4,lambda:(stop(),check('natural_visible_step_entry',frame() and abs(pos()[1])<30,pos())))
at(4.2,lambda:nav(0,-195));at(6.4,lambda:(stop(),check('walk_to_rear',pos()[0]<-175 and frame(),pos())))
at(6.6,lambda:nav(0,130));at(8.8,lambda:(stop(),check('walk_back_to_entry_aisle',pos()[0]>115 and frame(),pos())))
at(9,lambda:nav(0,92.4));at(9.5,lambda:nav(1,300));at(12,lambda:(stop(),check('natural_side_door_exit',not frame() and pos()[1]>220,pos()),check('outside_dimensions_restored',abs(cap.get_unscaled_capsule_radius()-original_radius)<.01 and abs(m.get_editor_property('MaxWalkSpeed')-original_speed)<.01)))
at(13,lambda:aim(outside));at(13.3,lambda:key('E',True));at(14.2,lambda:key('E',False));at(14.7,lambda:check('interaction_entry_clear_aisle',frame() and abs(pos()[1])<10 and 110<pos()[0]<150,pos()))
at(15,lambda:nav(0,-195));at(17.2,lambda:(stop(),check('entry_then_rear_not_trapped',frame() and pos()[0]<-175,pos())))
at(17.4,lambda:nav(0,130));at(19.6,lambda:(stop(),check('rear_return_to_door',frame() and pos()[0]>115,pos())))
at(20,lambda:aim(inside));at(20.3,lambda:key('E',True));at(21.2,lambda:key('E',False));at(21.7,lambda:check('interaction_exit_safe_ground',not frame() and pos()[1]>220,pos()))
at(22,lambda:aim(outside));at(22.3,lambda:key('E',True));at(23.2,lambda:key('E',False));at(24,lambda:aim(ep));at(24.3,lambda:key('E',True));at(25.2,lambda:key('E',False));at(25.7,lambda:check('standing_inside_to_driver',pc.get_controlled_pawn()==v and driver.get_editor_property('Occupant')==p))
at(26,lambda:pc.request_switch_seat('PassengerSeat'));at(27,lambda:check('driver_to_passenger',pc.get_controlled_pawn()==p and driver.get_editor_property('Occupant') is None and passenger.get_editor_property('Occupant')==p))
at(28,lambda:pc.request_switch_seat('DriverSeat'));at(29,lambda:check('passenger_to_driver',pc.get_controlled_pawn()==v and passenger.get_editor_property('Occupant') is None and driver.get_editor_property('Occupant')==p))
at(30,lambda:pc.request_switch_seat('InvalidSeat'));at(31,lambda:check('invalid_seat_keeps_occupancy',pc.get_controlled_pawn()==v and driver.get_editor_property('Occupant')==p))
at(32,lambda:pc.request_switch_seat('PassengerSeat'));at(33,lambda:key('V',True));at(33.2,lambda:key('V',False));at(34,lambda:check('native_V_cycles_back_to_driver',pc.get_controlled_pawn()==v and driver.get_editor_property('Occupant')==p))
at(35,lambda:key('E',True));at(35.3,lambda:key('E',False));at(36,lambda:check('normal_seat_exit_after_switch',pc.get_controlled_pawn()==p and pc.get_editor_property('SeatedVehicle') is None and driver.get_editor_property('Occupant') is None))

# Exterior shell checks use native movement against the saved query-only approximations.
at(37,lambda:place(500,0));at(37.5,lambda:nav(0,300))
at(40.5,lambda:(stop(),check('front_shell_blocks_walk_through',pos()[0]>435 and not frame(),pos())))
at(41,lambda:place(310,300));at(41.5,lambda:nav(1,0))
at(44.5,lambda:(stop(),check('right_cab_shell_blocks_walk_through',pos()[1]>130 and not frame(),pos())))
at(45,lambda:nav(0,455));at(46.5,lambda:(stop(),check('walk_around_nose_clearance',pos()[0]>440 and not frame(),pos())))
at(47,lambda:nav(1,-205));at(49,lambda:(stop(),check('walk_across_front_outside',pos()[1]<-180 and not frame(),pos())))
at(49.5,lambda:nav(0,310));at(51,lambda:(stop(),check('left_cab_outside_movement',290<pos()[0]<330 and not frame(),pos())))
at(.25,lambda:(pc.set_control_rotation(unreal.Rotator(pitch=-20,yaw=v.get_actor_rotation().yaw-90)),unreal.SystemLibrary.execute_console_command(pc,'shot filename=D:/GitHub/RVSurvival/RVSurvival/Saved/Gate5Refinement/entry-step.png -nosuffix',pc)))
events.sort(key=lambda a:a[0])

def tick(dt):
 global t,idx,acc,held
 t+=dt;acc+=dt
 try:
  while idx<len(events) and t>=events[idx][0]:events[idx][1]();idx+=1
  if target:
   axis,val=target;d=val-pos()[axis];on=abs(d)>5
   yaw=v.get_actor_rotation().yaw+(0 if axis==0 and d>0 else 180 if axis==0 else 90 if d>0 else -90);pc.set_control_rotation(unreal.Rotator(yaw=yaw))
   if on!=held:key('W',on);held=on
  if acc>.1:
   acc=0;rows.append({'t':t,'pos':pos(),'frame':frame(),'radius':cap.get_unscaled_capsule_radius(),'mode':str(m.get_editor_property('MovementMode')),'base':str(f.get_editor_property('CurrentBase'))})
  if t>53:stop();unreal.unregister_slate_post_tick_callback(h);json.dump({'results':checks,'samples':rows},open(B+'single-final.json','w'),indent=2)
 except Exception as e:
  check('exception',False,repr(e));stop();unreal.unregister_slate_post_tick_callback(h);json.dump({'results':checks,'samples':rows},open(B+'single-final.json','w'),indent=2)
h=unreal.register_slate_post_tick_callback(tick)
