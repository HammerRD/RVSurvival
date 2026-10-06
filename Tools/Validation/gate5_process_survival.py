import unreal,json,time,os
B='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate5Validation/'
session=json.load(open(B+'process_session.json'));config=session['config'];start=session['start'];out=config['name']
w=next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='Gate5SurvivalTest' and unreal.GameplayStatics.get_player_controller(w,0) and unreal.GameplayStatics.get_player_controller(w,0).get_controlled_pawn())
authority=unreal.GameplayStatics.get_game_mode(w) is not None;own=unreal.GameplayStatics.get_player_controller(w,0);p=own.get_controlled_pawn();other=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSurvivorCharacter) if a!=p)
hp=p if authority else other;cp=other if authority else p
hi=hp.get_component_by_class(unreal.RVInventoryComponent);ci=cp.get_component_by_class(unreal.RVInventoryComponent);inv=hi if authority else ci
hn=hp.get_editor_property('PlayerState').get_editor_property('Needs');cn=cp.get_editor_property('PlayerState').get_editor_property('Needs');needs=hn if authority else cn
ext=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVStoragePoint) if str(a.get_editor_property('Container').get_editor_property('DisplayName'))=='External storage');container=ext.get_editor_property('Container')
bed=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVRestPoint) if str(a.get_editor_property('DisplayName'))=='Rear bed');rv=bed.get_attach_parent_actor()
results=[];samples=[];events=[];idx=0;active=True;sample_at=0;ids={};before={}
def guid(g):return unreal.GuidLibrary.conv_guid_to_string(g)
def sig(i):return sorted((guid(x.id),str(x.definition.get_editor_property('CatalogId')),x.quantity,round(x.condition,4)) for x in i.get_items())
def record(i,key):return next(x for x in i.get_items() if str(x.definition.get_editor_property('CatalogId'))==key)
def qty(i,key=None):return sum(x.quantity for x in i.get_items() if key is None or str(x.definition.get_editor_property('CatalogId'))==key)
def state(n):s=n.get_editor_property('State');return {'nutrition':s.nutrition,'hydration':s.hydration,'fatigue':s.fatigue,'rest':str(s.rest_mode),'seconds':s.simulated_seconds}
def check(name,ok,detail=''):results.append({'case':name,'pass':bool(ok),'detail':str(detail)});unreal.log('GATE5_PROCESS '+json.dumps(results[-1]))
def at(t,f):events.append((t,f))
def command(s):unreal.SystemLibrary.execute_console_command(own,s,own)
def key(k,on):command('Input.'+('+' if on else '-')+'key '+k)
def aim(a):own.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p.get_actor_location()+unreal.Vector(0,0,64),a.get_actor_location()))
def add(i,key,quantity):
 x=unreal.RVItemInstance();x.set_editor_property('Id',unreal.GuidLibrary.new_guid());x.set_editor_property('Definition',unreal.load_asset('/Game/Items/DA_'+key));x.set_editor_property('Quantity',quantity);x.set_editor_property('Condition',.71);i.add_authority(x)
def setup():
 if not authority:return
 command('rv.Needs.AllowDebug 1');hn.debug_set_values(20,30,40);cn.debug_set_values(40,40,60);hn.debug_set_time_scale(0);cn.debug_set_time_scale(0)
 for i in [hi,ci]:
  add(i,'Food',2);add(i,'Water',2);add(i,'Tool',1)
 add(container,'Food',1)
def remember():
 for label,i in [('host',hi),('client',ci)]:ids[label]={key:record(i,key).id for key in ['Food','Water','Tool']}
 ids['shared']=record(container,'Food').id
 check('two_independent_initial_needs',abs(hn.get_editor_property('State').nutrition-20)<.01 and abs(cn.get_editor_property('State').nutrition-40)<.01)
 if not authority:check('client_debug_cannot_authorize_state',not cn.debug_set_values(99,99,99))
def consume(key,twice=False):
 g=ids['host' if authority else 'client'][key];needs.request_consume(g)
 if twice:needs.request_consume(g)
def check_eat(first):
 expected=(45 if authority else 65) if first else (70 if authority else 90)
 check('owned_food_'+('first' if first else 'last_once'),qty(inv,'Food')==(1 if first else 0) and abs(needs.get_editor_property('State').nutrition-expected)<.01,state(needs))
def check_drink(first):
 expected=(65 if authority else 75) if first else 100
 check('owned_water_'+('first' if first else 'last_once'),qty(inv,'Water')==(1 if first else 0) and abs(needs.get_editor_property('State').hydration-expected)<.01,state(needs))
def invalids():
 needs.request_consume(ids['client' if authority else 'host']['Tool']);needs.request_consume(ids['host' if authority else 'client']['Food']);needs.request_consume(ids['host' if authority else 'client']['Tool']);needs.request_consume(unreal.GuidLibrary.new_guid())
def invalid_check():
 check('foreign_stale_nonconsumable_invalid_rejected',qty(hi)==qty(ci)==1 and abs(hn.get_editor_property('State').nutrition-70)<.01 and abs(cn.get_editor_property('State').nutrition-90)<.01)
def arrange_external():
 if authority:
  for pawn,y in [(hp,-50),(cp,50)]:pawn.set_actor_location(ext.get_actor_location()+unreal.Vector(-140,y,62),False,True)
def withdraw():inv.request_transfer(ids['shared'],1,False)
def consume_winner():
 if qty(inv,'Food'):needs.request_consume(record(inv,'Food').id)
def shared_check():
 check('shared_final_item_transfer_one_winner',qty(container)==0 and qty(hi,'Food')+qty(ci,'Food')==1)
def final_shared():check('shared_final_item_consumed_without_duplicate',qty(hi,'Food')+qty(ci,'Food')+qty(container,'Food')==0 and (abs(hn.get_editor_property('State').nutrition+cn.get_editor_property('State').nutrition-185)<.01 or abs(hn.get_editor_property('State').nutrition+cn.get_editor_property('State').nutrition-170)<.01),(state(hn),state(cn)))
def arrange_bed():
 if authority:
  for pawn,y in [(hp,-35),(cp,35)]:pawn.set_actor_location(rv.get_actor_transform().transform_location(unreal.Vector(-180,y,195)),False,True)
def rest_check():
 modes=[hn.get_editor_property('State').rest_mode,cn.get_editor_property('State').rest_mode]
 check('one_rest_reservation_winner',sum(m!=unreal.RVRestMode.AWAKE for m in modes)==1 and bed.get_editor_property('Occupant') is not None,modes)
 if authority:
  n=hn if modes[0]!=unreal.RVRestMode.AWAKE else cn;n.debug_advance_time(3600)
 if needs.get_editor_property('State').rest_mode!=unreal.RVRestMode.AWAKE:needs.request_rest_mode(unreal.RVRestMode.SLEEPING)
def sleep_check():check('exclusive_sleep_replicated',sum(n.get_editor_property('State').rest_mode==unreal.RVRestMode.SLEEPING for n in [hn,cn])==1)
def awake():needs.request_rest_mode(unreal.RVRestMode.AWAKE)
def client_hold():
 if not authority:aim(bed);key('E',True)
def end_client_hold():
 if not authority:key('E',False)
def client_sleep():
 if not authority:cn.request_rest_mode(unreal.RVRestMode.SLEEPING)
def sample():samples.append({'t':time.time()-start,'host':sig(hi),'client':sig(ci),'container':sig(container),'needs':{'host':state(hn),'client':state(cn)},'rest_occupied':bed.get_editor_property('Occupant') is not None})
def finish_client():
 global active
 if authority:return
 check('client_sleep_before_disconnect',cn.get_editor_property('State').rest_mode==unreal.RVRestMode.SLEEPING)
 sample();json.dump({'pid':os.getpid(),'authority':False,'config':config,'results':results,'samples':samples},open(B+out+'_client.json','w'),indent=2)
 active=False;unreal.unregister_slate_post_tick_callback(handle)
 controller=own;execute=unreal.SystemLibrary.execute_console_command
 from runner_runtime import release_runners
 release_runners();execute(controller,'disconnect',controller)
def finish_server():
 global active
 if not authority:return
 check('disconnect_releases_rest_and_preserves_shared_storage',bed.get_editor_property('Occupant') is None and qty(container)==0 and hn.get_editor_property('State').rest_mode==unreal.RVRestMode.AWAKE)
 sample();active=False;unreal.unregister_slate_post_tick_callback(handle);json.dump({'pid':os.getpid(),'authority':True,'config':config,'results':results,'samples':samples},open(B+out+'_server.json','w'),indent=2)
command('t.MaxFPS 60');command('t.IdleWhenNotForeground 0')
at(0,setup);at(2,remember);at(3,lambda:consume('Food'));at(4,lambda:check_eat(True));at(5,lambda:consume('Food',True));at(6,lambda:check_eat(False));at(7,lambda:consume('Water'));at(8,lambda:check_drink(True));at(9,lambda:consume('Water',True));at(10,lambda:check_drink(False));at(11,invalids);at(12,invalid_check)
at(13,arrange_external);at(14,lambda:(aim(ext),key('E',True)));at(15,lambda:key('E',False));at(16,withdraw);at(17,shared_check);at(18,consume_winner);at(19,final_shared)
at(20,arrange_bed);at(21,lambda:(aim(bed),key('E',True)));at(22,lambda:key('E',False));at(23,rest_check);at(24,sleep_check);at(25,awake);at(26,client_hold);at(27,end_client_hold);at(28,client_sleep);at(30,finish_client);at(34,finish_server)

dinette=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVRestPoint) if str(a.get_editor_property('DisplayName'))=='Dinette rest')
def host_dinette_position():
 if authority:hp.set_actor_location(rv.get_actor_transform().transform_location(unreal.Vector(55,0,177)),False,True)
def host_rest_hold(on):
 if authority:
  if on:aim(dinette)
  key('E',on)
def host_sleep():
 if authority:hn.request_rest_mode(unreal.RVRestMode.SLEEPING)
def both_surfaces():
 check('two_distinct_sleep_surfaces',hn.get_editor_property('State').rest_mode==cn.get_editor_property('State').rest_mode==unreal.RVRestMode.SLEEPING and bed.get_editor_property('Occupant') is not None and dinette.get_editor_property('Occupant') is not None and bed.get_editor_property('Occupant')!=dinette.get_editor_property('Occupant'))
def host_sleep_after_disconnect():
 if authority:check('disconnect_does_not_cancel_other_sleep',hn.get_editor_property('State').rest_mode==unreal.RVRestMode.SLEEPING and dinette.get_editor_property('Occupant')==hp.get_editor_property('PlayerState'))
at(25.3,host_dinette_position);at(26,lambda:host_rest_hold(True));at(27,lambda:host_rest_hold(False));at(28,host_sleep);at(29,both_surfaces);at(31,host_sleep_after_disconnect);at(32,lambda:hn.request_rest_mode(unreal.RVRestMode.AWAKE) if authority else None)
events.sort(key=lambda e:e[0])

def tick(dt):
 global idx,sample_at
 if not active:return
 t=time.time()-start
 if t<0:return
 try:
  while idx<len(events) and t>=events[idx][0]:
   f=events[idx][1];idx+=1;terminating=f is finish_client and not authority
   f()
   if terminating:return
   if not active:return
  if active and t>=sample_at:sample();sample_at=t+.1
 except Exception as e:check('runner_exception',False,repr(e));finish_server() if authority else finish_client()
handle=unreal.register_slate_post_tick_callback(tick)
