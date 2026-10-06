import unreal,json,time,os
B='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate5Validation/'
w=next(w for w in unreal.ObjectIterator(unreal.World) if 'UEDPIE_' in w.get_path_name() and w.get_name()=='Gate5SurvivalTest');pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn();n=pc.get_editor_property('PlayerState').get_editor_property('Needs');inv=p.get_component_by_class(unreal.RVInventoryComponent)
ext=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVStoragePoint) if str(a.get_editor_property('Container').get_editor_property('DisplayName'))=='External storage');storage=ext.get_editor_property('Container');bed=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVRestPoint) if str(a.get_editor_property('DisplayName'))=='Rear bed')
results=[];events=[];idx=0;t=0;ids=set();current={};cycles=[];rest_cycles=[];clock_before=0
unreal.SystemLibrary.execute_console_command(w,'rv.Needs.AllowDebug 1',pc);n.debug_set_time_scale(0)
def check(name,ok,detail=''):results.append({'case':name,'pass':bool(ok),'detail':str(detail)});unreal.log('GATE5_STRESS '+json.dumps(results[-1]))
def at(t,f):events.append((t,f))
def key(k,on):unreal.SystemLibrary.execute_console_command(w,'Input.'+('+' if on else '-')+'key '+k,pc)
def aim(a):pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p.get_actor_location()+unreal.Vector(0,0,64),a.get_actor_location()))
def seed(target,name):
 item=unreal.RVItemInstance();item.set_editor_property('Id',unreal.GuidLibrary.new_guid());item.set_editor_property('Definition',unreal.load_asset('/Game/Items/DA_'+name));item.set_editor_property('Condition',.47)
 data=unreal.RVItemStateEntry();data.set_editor_property('Key','Batch');data.set_editor_property('Value','SurvivalStress');item.set_editor_property('CustomState',[data]);target.add_authority(item)
 identity=unreal.GuidLibrary.conv_guid_to_string(item.id);assert identity not in ids;ids.add(identity);current[name]=item.id
 return item.id
def begin_cycle():n.debug_set_values(5,5,40);seed(storage,'Food')
def food_verify():
 assert len(storage.get_items())==0 and len(inv.get_items())==0 and abs(n.get_editor_property('State').nutrition-30)<.01
 seed(inv,'Water')
def cycle_verify(index):
 s=n.get_editor_property('State');good=len(inv.get_items())==0 and len(storage.get_items())==0 and abs(s.nutrition-30)<.01 and abs(s.hydration-40)<.01
 cycles.append({'cycle':index,'pass':good});assert good
 # Replay an already consumed GUID: must not recreate or consume another record.
 n.request_consume(current['Food'])
def arrange_external():p.set_actor_location(ext.get_actor_location()+unreal.Vector(-140,0,62),False,True);aim(ext)
def begin_rest():
 p.set_actor_location(bed.get_attach_parent_actor().get_actor_transform().transform_location(unreal.Vector(-180,0,195)),False,True);aim(bed);n.debug_set_values(40,40,80)
def enter_sleep():assert n.get_editor_property('State').rest_mode==unreal.RVRestMode.RESTING;n.request_rest_mode(unreal.RVRestMode.SLEEPING)
def sleep_verify():
 assert n.get_editor_property('State').rest_mode==unreal.RVRestMode.SLEEPING;n.debug_advance_time(3600);s=n.get_editor_property('State');assert abs(s.fatigue-55)<.01 and s.nutrition<40 and s.hydration<40;n.request_rest_mode(unreal.RVRestMode.AWAKE)
def wake_verify(index):
 good=n.get_editor_property('State').rest_mode==unreal.RVRestMode.AWAKE and bed.get_editor_property('Occupant') is None and p.get_component_by_class(unreal.CharacterMovementComponent).get_max_speed()>0
 rest_cycles.append({'cycle':index,'pass':good});assert good

def begin_day():
 global clock_before
 n.debug_set_values(90,90,10);clock_before=n.get_editor_property('State').simulated_seconds;n.debug_set_time_scale(3600)
def day_verify():
 n.debug_set_time_scale(0);s=n.get_editor_property('State');elapsed=s.simulated_seconds-clock_before
 check('accelerated_day_through_real_component_ticks',85000<elapsed<89000 and s.nutrition==0 and s.hydration==0 and s.fatigue==100 and 1<=s.survival_reserve<=100,{'seconds':elapsed,'nutrition':s.nutrition,'hydration':s.hydration,'fatigue':s.fatigue,'reserve':s.survival_reserve})
 check('200_consumes_and_100_shared_transfers',len(cycles)==100 and all(x['pass'] for x in cycles) and len(ids)==200,{'cycles':len(cycles),'unique_guids':len(ids)})
 check('20_rest_sleep_wake_cycles',len(rest_cycles)==20 and all(x['pass'] for x in rest_cycles))
 check('no_item_or_reservation_residue',not inv.get_items() and not storage.get_items() and all(a.get_editor_property('Occupant') is None for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVRestPoint)))
 check('world_pickup_actors_not_leaked_by_record_transactions',len(unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVWorldItem))==11)
 n.debug_set_values(90,90,10);n.debug_set_time_scale(1)
def finish():unreal.unregister_slate_post_tick_callback(h);json.dump({'pid':os.getpid(),'results':results,'consume_cycles':cycles,'rest_cycles':rest_cycles},open(B+'stress.json','w'),indent=2)
at(0,arrange_external);at(.5,lambda:key('E',True));at(1.3,lambda:key('E',False));at(1.8,lambda:check('external_container_open',inv.get_editor_property('OpenContainer')==storage))
for j in range(100):
 q=2+j*.85;at(q,begin_cycle);at(q+.05,lambda:inv.request_transfer(current['Food'],1,False));at(q+.25,lambda:n.request_consume(current['Food']));at(q+.4,food_verify);at(q+.55,lambda:n.request_consume(current['Water']));at(q+.8,lambda j=j:cycle_verify(j))
at(87,inv.request_close_container)
for j in range(20):
 q=88+j*2;at(q,begin_rest);at(q+.1,lambda:key('E',True));at(q+.85,lambda:key('E',False));at(q+1,enter_sleep);at(q+1.3,sleep_verify);at(q+1.7,lambda j=j:wake_verify(j))
at(129,begin_day);at(153,day_verify);at(154,finish)
def tick(dt):
 global t,idx
 t+=dt
 try:
  while idx<len(events) and t>=events[idx][0]:a=events[idx][1];idx+=1;a()
 except Exception as e:check('runner_exception',False,repr(e));finish()
h=unreal.register_slate_post_tick_callback(tick)
