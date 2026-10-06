import unreal,json,time,os
B='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate5Refinement/'
session=json.load(open(B+'session.json'));config=session['config'];start=session['start']
w=next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='Gate5SurvivalTest' and unreal.GameplayStatics.get_player_controller(w,0) and unreal.GameplayStatics.get_player_controller(w,0).get_controlled_pawn())
authority=unreal.GameplayStatics.get_game_mode(w) is not None;own=unreal.GameplayStatics.get_player_controller(w,0);p=own.get_controlled_pawn();other=next(c for c in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSurvivorCharacter) if c!=p);hp=p if authority else other;cp=other if authority else p
v=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVInteriorMotorhome)[0];driver=next(s for s in v.get_seats() if s.get_editor_property('bDriverSeat'));passenger=next(s for s in v.get_seats() if not s.get_editor_property('bDriverSeat'))
entries=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVVehicleEntryPoint);de=next(e for e in entries if e.get_editor_property('Seat')==driver and abs(v.get_actor_transform().inverse_transform_location(e.get_actor_location()).y)>100);pe=next(e for e in entries if e.get_editor_property('Seat')==passenger and abs(v.get_actor_transform().inverse_transform_location(e.get_actor_location()).y)>100)
doors=sorted(unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVExteriorStoragePoint),key=lambda a:str(a.get_editor_property('DoorPartName')))
access=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVInteriorAccessPoint);outside=next(a for a in access if a.get_editor_property('bEnter'));inside=next(a for a in access if not a.get_editor_property('bEnter'))
hi=hp.get_component_by_class(unreal.RVInventoryComponent);ci=cp.get_component_by_class(unreal.RVInventoryComponent);inv=hi if authority else ci;hn=hp.get_editor_property('PlayerState').get_editor_property('Needs');cn=cp.get_editor_property('PlayerState').get_editor_property('Needs');needs=hn if authority else cn
results=[];samples=[];events=[];idx=0;active=True;next_sample=0;ids={};dropid=None

def guid(g):return unreal.GuidLibrary.conv_guid_to_string(g)
def check(n,ok,d=''):results.append({'case':n,'pass':bool(ok),'detail':str(d)});unreal.log('REFINE_NET '+json.dumps(results[-1]))
def cmd(s):unreal.SystemLibrary.execute_console_command(own,s,own)
def key(k,on):cmd('Input.'+('+' if on else '-')+'key '+k)
def aim(a):own.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p.get_actor_location()+unreal.Vector(0,0,64),a.get_actor_location()))
def place(ch,point,side):
 if authority:
  q=point.get_actor_location()+v.get_actor_right_vector()*side;q.z=90;ch.set_actor_location(q,False,True)
def add(c,name,qty=1,condition=.65):
 a=unreal.RVItemInstance();a.set_editor_property('Id',unreal.GuidLibrary.new_guid());a.set_editor_property('Definition',unreal.load_asset('/Game/Items/DA_'+name));a.set_editor_property('Quantity',qty);a.set_editor_property('Condition',condition);st=unreal.RVItemStateEntry();st.set_editor_property('Key','Refinement');st.set_editor_property('Value','preserve');a.set_editor_property('CustomState',[st]);c.add_authority(a);return a.id
def qty(c,name=None):return sum(a.quantity for a in c.get_items() if name is None or str(a.definition.get_editor_property('CatalogId'))==name)
def occupied(s,c):return s.get_editor_property('Occupant')==c
def seat_check(n,who_driver,who_passenger):
 check(n,driver.get_editor_property('Occupant')==who_driver and passenger.get_editor_property('Occupant')==who_passenger,{'driver':str(driver.get_editor_property('Occupant')),'passenger':str(passenger.get_editor_property('Occupant'))})
def own_possession(n,driver_mode):check(n,own.get_controlled_pawn()==(v if driver_mode else p))
def setup():
 if authority:
  place(hp,de,-180);place(cp,pe,180);cmd('rv.Needs.AllowDebug 1');hn.debug_set_values(20,30,40);cn.debug_set_values(40,50,60);hn.debug_set_time_scale(0);cn.debug_set_time_scale(0)
 check('seven_unique_independent_doors',len(doors)==7 and len({str(d.get_editor_property('DoorPartName')) for d in doors})==7)
def prepare_door(i):
 d=doors[i]
 if authority:
  sign=-1 if v.get_actor_transform().inverse_transform_location(d.get_actor_location()).y<0 else 1
  for ch,xoff in [(hp,-45),(cp,45)]:
   q=d.get_actor_location()+v.get_actor_right_vector()*sign*145+v.get_actor_forward_vector()*xoff;q.z=90;ch.set_actor_location(q,False,True)
def open_check(i):check('open_specific_door_%02d'%(i+1),inv.get_editor_property('OpenContainer')==doors[i].get_editor_property('Container'))
def remember(i):ids[i]=doors[i].get_editor_property('Container').get_items()[0].id
def withdraw(i):inv.request_transfer(ids[i],1,False)
def winner_check(i):
 total=qty(hi)+qty(ci)+qty(doors[i].get_editor_property('Container'))
 check('no_duplicate_contention_%02d'%(i+1),qty(doors[i].get_editor_property('Container'))==0 and sum(a.quantity for c in [hi,ci] for a in c.get_items() if guid(a.id)==guid(ids[i]))==1,{'total':total})
def return_winner(i):
 if any(guid(a.id)==guid(ids[i]) for a in inv.get_items()):inv.request_transfer(ids[i],1,True)
def restored(i):
 a=doors[i].get_editor_property('Container').get_items()
 check('return_state_preserved_%02d'%(i+1),len(a)==1 and guid(a[0].id)==guid(ids[i]) and abs(a[0].condition-.65)<.001 and len(a[0].custom_state)==1)
 inv.request_close_container()
def seed_storage():
 if authority:
  add(doors[0].get_editor_property('Container'),'Food')
  for index,d in enumerate(doors[1:],start=1):add(d.get_editor_property('Container'),'EnginePart' if index==2 else 'Tool')
 prepare_door(0)
def food_check():
 a=hn.get_editor_property('State').nutrition;b=cn.get_editor_property('State').nutrition
 check('only_owner_consumes_final_shared_food',qty(hi,'Food')+qty(ci,'Food')==0 and qty(doors[0].get_editor_property('Container'))==0 and ((abs(a-45)<.01 and abs(b-40)<.01) or (abs(a-20)<.01 and abs(b-65)<.01)),(a,b))
def signatures():return [[(guid(x.id),x.quantity,round(x.condition,3)) for x in d.get_editor_property('Container').get_items()] for d in doors]
def check_all():check('all_compartments_independent_after_contention',qty(doors[0].get_editor_property('Container'))==0 and all(qty(d.get_editor_property('Container'))==1 for d in doors[1:]),signatures())
def drop_prepare():
 if authority:add(ci,'Water',1,.76)
def drop_request():
 global dropid
 dropid=next(x.id for x in ci.get_items() if str(x.definition.get_editor_property('CatalogId'))=='Water')
 if not authority:inv.request_drop(dropid,1)
def find_drop():return next((a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVWorldItem) if guid(a.get_editor_property('Item').id)==guid(dropid)),None)
def drop_check():
 a=find_drop();check('dropped_item_replicates',a is not None and abs(a.get_editor_property('Item').condition-.76)<.001)
 if authority and a:
  q=a.get_actor_location()+unreal.Vector(-110,0,88);hp.set_actor_location(q,False,True);aim(a)
def pickup_drop(on):
 if authority:
  if on:
   a=find_drop()
   if a:aim(a)
  key('E',on)
def repick_check():
 items=[a for a in hi.get_items() if guid(a.id)==guid(dropid)]
 check('drop_repicked_guid_condition',find_drop() is None and len(items)==1 and abs(items[0].condition-.76)<.001)
def client_door_setup():
 if authority:
  place(cp,outside,100);hp.set_actor_location(unreal.Vector(600,-500,90),False,True)
def client_door_check(entered):
 f=cp.get_component_by_class(unreal.RVPassengerReferenceFrameComponent);q=v.get_actor_transform().inverse_transform_location(cp.get_actor_location())
 check('client_remote_door_'+('entry' if entered else 'exit'),(f.get_editor_property('ReferenceFrame')==v if entered else f.get_editor_property('ReferenceFrame') is None) and (abs(q.y)<10 if entered else q.y>220),[q.x,q.y,q.z])
def sample():samples.append({'client_position':str(cp.get_actor_location()),'client_local':str(v.get_actor_transform().inverse_transform_location(cp.get_actor_location())),'own_prompt':str(p.get_component_by_class(unreal.RVInteractionComponent).get_prompt()),'control':str(own.get_control_rotation()),'speed':v.get_velocity().length(),'t':round(time.time()-start,3),'seats':[str(driver.get_editor_property('Occupant')),str(passenger.get_editor_property('Occupant'))],'containers':signatures(),'host_items':[(guid(a.id),a.quantity) for a in hi.get_items()],'client_items':[(guid(a.id),a.quantity) for a in ci.get_items()]})
def finish_client():
 global active
 if authority:return
 sample();json.dump({'pid':os.getpid(),'authority':False,'config':config,'results':results,'samples':samples},open(B+config['name']+'_client.json','w'),indent=2)
 active=False;unreal.unregister_slate_post_tick_callback(h);controller=own;execute=unreal.SystemLibrary.execute_console_command
 from runner_runtime import release_runners
 release_runners();execute(controller,'disconnect',controller)
def finish_server():
 global active
 if not authority:return
 check('disconnect_frees_switched_seat_preserves_RV',driver.get_editor_property('Occupant') is None and passenger.get_editor_property('Occupant') is None and unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVInteriorMotorhome)==[v])
 check_all();sample();active=False;unreal.unregister_slate_post_tick_callback(h);json.dump({'pid':os.getpid(),'authority':True,'config':config,'results':results,'samples':samples},open(B+config['name']+'_server.json','w'),indent=2)
def at(t,f):events.append((t,f))
cmd('t.MaxFPS 60');cmd('t.IdleWhenNotForeground 0')
at(0,setup);at(.5,lambda:aim(de if authority else pe));at(.85,lambda:key('E',True));at(1.85,lambda:key('E',False));at(3,lambda:(seat_check('host_driver_client_passenger',hp,cp),own_possession('initial_possession',authority)))
at(4,lambda:own.request_switch_seat('PassengerSeat' if authority else 'DriverSeat'));at(5,lambda:(seat_check('occupied_swap_rejected',hp,cp),check('occupied_feedback','occupied' in own.get_editor_property('SeatFeedback').lower())))
at(6,lambda:key('E',True) if not authority else None);at(6.3,lambda:key('E',False) if not authority else None);at(7,lambda:seat_check('passenger_exit_frees_seat',hp,None))
at(8,lambda:own.request_switch_seat('PassengerSeat') if authority else None);at(9,lambda:(seat_check('host_switch_to_passenger',None,hp),own_possession('host_passenger_possession',False) if authority else None))
at(10,lambda:place(cp,de,-180));at(10.5,lambda:aim(de) if not authority else None);at(10.85,lambda:key('E',True) if not authority else None);at(11.85,lambda:key('E',False) if not authority else None);at(12.3,lambda:(seat_check('client_driver_host_passenger',cp,hp),own_possession('swapped_possession',not authority)))
at(13,lambda:own.request_switch_seat('DriverSeat' if authority else 'PassengerSeat'));at(14,lambda:seat_check('occupied_swapped_rejected',cp,hp))
at(15,lambda:key('E',True) if authority else None);at(15.3,lambda:key('E',False) if authority else None);at(16,lambda:seat_check('host_passenger_exit_frees',cp,None))
at(17,lambda:own.request_switch_seat('PassengerSeat') if not authority else None);at(18,lambda:seat_check('client_driver_to_passenger',None,cp));at(19,lambda:own.request_switch_seat('DriverSeat') if not authority else None);at(20,lambda:seat_check('client_passenger_to_driver',cp,None))
at(21,lambda:key('W',True) if not authority else None);at(24,lambda:check('client_drives_after_switch',v.get_velocity().length()>250,v.get_velocity().length()));at(25,lambda:(key('W',False),key('S',True)) if not authority else None);at(28,lambda:(key('S',False),key('SpaceBar',True)) if not authority else None)
at(31.5,lambda:key('SpaceBar',False) if not authority else None);at(32,lambda:key('V',True) if not authority else None);at(32.2,lambda:key('V',False) if not authority else None);at(33,lambda:seat_check('client_native_V_driver_to_passenger',None,cp));at(34,lambda:key('V',True) if not authority else None);at(34.2,lambda:key('V',False) if not authority else None);at(35,lambda:seat_check('client_native_V_passenger_to_driver',cp,None));at(36,lambda:key('E',True) if not authority else None);at(36.3,lambda:key('E',False) if not authority else None);at(37,lambda:seat_check('both_seats_released',None,None))
# Test new door transition on a genuine remote client before cargo transactions.
at(37.2,client_door_setup);at(37.6,lambda:aim(outside) if not authority else None);at(37.95,lambda:key('E',True) if not authority else None);at(38.95,lambda:key('E',False) if not authority else None);at(39.4,lambda:client_door_check(True));at(39.7,lambda:aim(inside) if not authority else None);at(40.05,lambda:key('E',True) if not authority else None);at(41.05,lambda:key('E',False) if not authority else None);at(41.5,lambda:client_door_check(False))
at(44,seed_storage);at(44.7,lambda:(remember(0),aim(doors[0])));at(45.05,lambda:key('E',True));at(46.05,lambda:key('E',False));at(46.5,lambda:open_check(0));at(47,lambda:withdraw(0));at(48,lambda:winner_check(0));at(49,lambda:needs.request_consume(ids[0]));at(50,food_check);at(50.5,inv.request_close_container)
for i in range(1,7):
 t=51+(i-1)*4
 at(t,lambda i=i:prepare_door(i));at(t+.35,lambda i=i:(remember(i),aim(doors[i])));at(t+.7,lambda:key('E',True));at(t+1.5,lambda:key('E',False));at(t+1.9,lambda i=i:(open_check(i),withdraw(i)));at(t+2.6,lambda i=i:(winner_check(i),return_winner(i)));at(t+3.5,lambda i=i:restored(i))
at(76,check_all);at(77,drop_prepare);at(78,drop_request);at(79,drop_check);at(79.5,lambda:pickup_drop(True));at(80.5,lambda:pickup_drop(False));at(81,repick_check)
at(82,lambda:place(cp,pe,180));at(82.5,lambda:aim(pe) if not authority else None);at(82.85,lambda:key('E',True) if not authority else None);at(83.85,lambda:key('E',False) if not authority else None);at(84.5,lambda:seat_check('client_seated_before_disconnect',None,cp));at(85,finish_client);at(89,finish_server)
events.sort(key=lambda a:a[0])
# Extend the test with true remote interior seat entry and numeric control.
interior_driver=next(a for a in entries if a.get_editor_property('Seat')==driver and abs(v.get_actor_transform().inverse_transform_location(a.get_actor_location()).y)<100)
events=[(t+7 if t>=44 else t,f) for t,f in events]
at(42,client_door_setup);at(42.35,lambda:aim(outside) if not authority else None);at(42.7,lambda:key('E',True) if not authority else None);at(43.7,lambda:key('E',False) if not authority else None);at(43.95,lambda:(client_door_check(True),aim(interior_driver) if not authority else None));at(44.3,lambda:key('E',True) if not authority else None);at(45.3,lambda:key('E',False) if not authority else None);at(45.8,lambda:seat_check('client_standing_interior_driver_entry',cp,None));at(46.1,lambda:key('Two',True) if not authority else None);at(46.3,lambda:key('Two',False) if not authority else None);at(47,lambda:seat_check('client_numeric_passenger_switch',None,cp));at(48,lambda:key('E',True) if not authority else None);at(48.3,lambda:key('E',False) if not authority else None);at(49,lambda:seat_check('interior_entry_switch_exit_releases',None,None))
events.sort(key=lambda a:a[0])

def tick(dt):
 global idx,next_sample
 if not active:return
 t=time.time()-start
 if t<0:return
 try:
  while idx<len(events) and t>=events[idx][0]:
   f=events[idx][1];idx+=1;terminating=f==finish_client and not authority;f()
   if terminating:return
   if not active:return
  if t>=next_sample:sample();next_sample=t+.25
 except Exception as e:
  check('exception',False,repr(e));finish_server() if authority else finish_client()
h=unreal.register_slate_post_tick_callback(tick)
