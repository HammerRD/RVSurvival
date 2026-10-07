import unreal,json,os
B='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate7Regressions/'
w=next(w for w in unreal.ObjectIterator(unreal.World) if 'UEDPIE_' in w.get_path_name() and w.get_name()=='Gate5SurvivalTest')
pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn();n=pc.get_editor_property('PlayerState').get_editor_property('Needs');i=p.get_component_by_class(unreal.RVInventoryComponent)
rows=[];events=[];t=0;index=0;water=None;food=None;before=None;rest=None
def check(name,ok,detail=''):
 rows.append({'case':name,'pass':bool(ok),'detail':str(detail)});unreal.log('GATE5 '+json.dumps(rows[-1]))
def at(t,f):events.append((t,f))
def key(k,on):unreal.SystemLibrary.execute_console_command(w,'Input.'+('+' if on else '-')+'key '+k,pc)
def state():return n.get_editor_property('State')
def find_item(key):return next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVWorldItem) if str(a.get_editor_property('Item').definition.get_editor_property('CatalogId'))==key)
def records(key):return [r for r in i.get_items() if str(r.definition.get_editor_property('CatalogId'))==key]
def quantity(key):return sum(r.quantity for r in records(key))
def arrange(target,pos=None):
 p.set_actor_location(pos or target.get_actor_location()+unreal.Vector(-140,0,62),False,True);pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p.get_actor_location()+unreal.Vector(0,0,64),target.get_actor_location()))
def setup():
 check('debug_off_by_default',not n.debug_set_values(50,50,50));unreal.SystemLibrary.execute_console_command(w,'rv.Needs.AllowDebug 1',pc);check('debug_authority_enabled',n.debug_set_values(40,40,40));n.debug_set_time_scale(0)
 check('tuning_asset_assigned',n.get_editor_property('TuningAsset') is not None)
 n.debug_advance_time(3600);s=state();check('one_hour_idle_drain',abs(s.nutrition-34)<.01 and abs(s.hydration-28)<.01 and abs(s.fatigue-44)<.01,(s.nutrition,s.hydration,s.fatigue))
 check('invalid_debug_value_rejected',not n.debug_set_values(float('nan'),40,40));n.debug_set_values(40,40,40)
 arrange(find_item('Water'))
def water_ready():
 global water
 check('water_picked_up_through_interaction',quantity('Water')==3,quantity('Water'));water=records('Water')[0]
 n.request_consume(water.id)
def water_first():
 s=state();check('drink_owned_stack',quantity('Water')==2 and abs(s.hydration-75)<.01,(quantity('Water'),s.hydration));r=records('Water')[0];check('remaining_stack_state_preserved',unreal.GuidLibrary.equal_equal_guid_guid(r.id,water.id) and abs(r.condition-.73)<.001 and r.custom_state[0].value=='Gate4Prototype')
 n.debug_set_values(40,10,40);n.request_consume(water.id)
def water_last():
 n.debug_set_values(40,10,40);n.request_consume(water.id);n.request_consume(water.id)
def check_water_last():
 check('last_water_removed_once',quantity('Water')==0 and abs(state().hydration-45)<.01,(quantity('Water'),state().hydration));n.request_consume(water.id)
def food_ready():
 global food
 food=records('Food')[0];check('food_picked_up',food.quantity==3);n.request_consume(food.id)
def eat_repeat():n.debug_set_values(10,40,40);n.request_consume(food.id)
def food_last():n.debug_set_values(10,40,40);n.request_consume(food.id);n.request_consume(food.id)
def rest_start():
 global rest
 rest=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVRestPoint) if str(a.get_editor_property('DisplayName'))=='Rear bed')
 rv=rest.get_attach_parent_actor();arrange(rest,rv.get_actor_transform().transform_location(unreal.Vector(-180,0,195)));n.debug_set_values(40,40,80)
def rest_check():
 check('rest_entered_via_hold',state().rest_mode==unreal.RVRestMode.RESTING,state().rest_mode)
 n.debug_advance_time(3600);s=state();check('rest_recovers_fatigue_not_food_water',abs(s.fatigue-70)<.01 and s.nutrition<40 and s.hydration<40,(s.nutrition,s.hydration,s.fatigue));n.request_rest_mode(unreal.RVRestMode.SLEEPING)
def sleep_check():
 check('sleep_state',state().rest_mode==unreal.RVRestMode.SLEEPING);old=(state().nutrition,state().hydration);n.debug_advance_time(3600);s=state();check('sleep_recovery_and_continued_metabolism',abs(s.fatigue-45)<.01 and s.nutrition<old[0] and s.hydration<old[1],(s.nutrition,s.hydration,s.fatigue))
 key('W',True);key('SpaceBar',True)
def wake():
 key('W',False);key('SpaceBar',False);check('rest_movement_restricted',p.get_component_by_class(unreal.CharacterMovementComponent).get_max_speed()==0);n.request_rest_mode(unreal.RVRestMode.AWAKE)
def after_wake():
 check('wake_frees_reservation',state().rest_mode==unreal.RVRestMode.AWAKE and rest.get_editor_property('Occupant') is None)
 check('world_movement_policy_restored',p.get_component_by_class(unreal.CharacterMovementComponent).get_max_speed()>0)
 n.debug_set_values(-50,150,150);s=state();check('debug_values_clamped',s.nutrition==0 and s.hydration==100 and s.fatigue==100)
 check('critical_warnings_and_tags',all(x in n.get_warnings() for x in ['Very hungry','Exhausted']) and len(unreal.GameplayTagLibrary.break_gameplay_tag_container(n.get_status_tags()))>=2,n.get_warnings())
 check('critical_movement_consequence',n.get_movement_scale()<1);n.debug_set_values(90,90,10);n.debug_advance_time(86400);s=state();check('24_hour_equivalent_clamped',s.nutrition==0 and s.hydration==0 and s.fatigue==100 and 1<=s.survival_reserve<=100,(s.nutrition,s.hydration,s.fatigue,s.survival_reserve))
 n.debug_set_values(90,90,10);n.debug_set_time_scale(1)
def finish():
 unreal.unregister_slate_post_tick_callback(h);json.dump({'pid':os.getpid(),'results':rows},open(B+'needs-single.json','w'),indent=2)
at(0,setup);at(.5,lambda:key('E',True));at(1.3,lambda:key('E',False));at(1.8,water_ready);at(2.3,water_first);at(2.8,lambda:check('second_drink',quantity('Water')==1 and abs(state().hydration-45)<.01));at(3,water_last);at(3.5,check_water_last);at(4,lambda:check('stale_guid_rejected',quantity('Water')==0 and 'owned' in n.get_editor_property('Feedback')))
at(4.2,lambda:arrange(find_item('Food')));at(4.7,lambda:key('E',True));at(5.5,lambda:key('E',False));at(6,food_ready);at(6.5,lambda:check('eat_recovers_nutrition',quantity('Food')==2 and abs(state().nutrition-65)<.01));at(7,eat_repeat);at(7.5,lambda:check('eat_stack_second',quantity('Food')==1));at(8,food_last);at(8.5,lambda:check('food_final_contention_once',quantity('Food')==0 and abs(state().nutrition-35)<.01));at(9,lambda:n.request_consume(unreal.GuidLibrary.new_guid()));at(9.5,lambda:check('invalid_guid_rejected','owned' in n.get_editor_property('Feedback')))
at(10,rest_start);at(10.5,lambda:key('E',True));at(11.3,lambda:key('E',False));at(12,rest_check);at(12.5,sleep_check);at(13.5,wake);at(14,after_wake);at(15,finish)
def tick(dt):
 global t,index
 t+=dt
 try:
  while index<len(events) and t>=events[index][0]:a=events[index][1];index+=1;a()
 except Exception as e:check('runner_exception',False,repr(e));finish()
h=unreal.register_slate_post_tick_callback(tick)
