import unreal,json
B='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate5Refinement/'
ws=sorted([w for w in unreal.ObjectIterator(unreal.World) if '/Game/Maps/UEDPIE_' in w.get_path_name() and w.get_name()=='Gate4InventoryTest'],key=lambda w:w.get_path_name());sw,cw=ws
host=unreal.GameplayStatics.get_player_controller(sw,0);client=unreal.GameplayStatics.get_player_controller(cw,0)
hp=host.get_controlled_pawn();cp=client.get_controlled_pawn()
CC=unreal.load_class(None,'/Script/RVSurvival.RVSurvivorCharacter');IC=unreal.load_class(None,'/Script/RVSurvival.RVInventoryComponent');PC=unreal.load_class(None,'/Script/RVSurvival.RVWorldItem');SC=unreal.load_class(None,'/Script/RVSurvival.RVStoragePoint')
sp=next(p for p in unreal.GameplayStatics.get_all_actors_of_class(sw,CC) if p!=hp)
hi=hp.get_component_by_class(IC);ci=cp.get_component_by_class(IC);si=sp.get_component_by_class(IC)
rows=[];events=[];index=0;t=0;water=None;drop=None;targets={}
external=min(unreal.GameplayStatics.get_all_actors_of_class(sw,SC),key=lambda a:(a.get_actor_location()-unreal.Vector(600,-350,100)).length())
cexternal=min(unreal.GameplayStatics.get_all_actors_of_class(cw,SC),key=lambda a:(a.get_actor_location()-unreal.Vector(600,-350,100)).length())
def check(n,ok,d=''):
 r={'case':n,'pass':bool(ok),'detail':str(d)};rows.append(r);unreal.log('GATE4 '+json.dumps(r))
def at(t,f):events.append((t,f))
def key(pc,k,on):
 if on and k=='E' and pc in targets:aim(pc,pc.get_controlled_pawn(),targets[pc])
 unreal.SystemLibrary.execute_console_command(pc,'Input.'+('+' if on else '-')+'key '+k,pc)
def find(w,name):return next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,PC) if str(a.get_editor_property('Item').get_editor_property('Definition').get_editor_property('CatalogId'))==name)
def aim(pc,p,target):pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p.get_actor_location()+unreal.Vector(0,0,64),target.get_actor_location()))
def arrange(pc,serverp,localp,target):
 targets[pc]=target;pos=target.get_actor_location()+unreal.Vector(-140,-50 if pc==host else 50,62);serverp.set_actor_location(pos,False,True);aim(pc,localp,target)
def items(i):return i.get_items()
def count(i):return sum(x.quantity for x in items(i))
def pickup(name,pc=host):
 target=find(sw,name);arrange(pc,hp if pc==host else sp,hp if pc==host else cp,target)
def save_water():
 global water
 water=items(hi)[0];check('single_host_pickup',water.quantity==3 and abs(water.condition-.73)<.001,count(hi))
def do_drop():hi.request_drop(water.id,water.quantity)
def drop_aim():
 global drop
 drop=find(sw,'Water');check('drop_preserves_identity_condition',unreal.GuidLibrary.equal_equal_guid_guid(drop.get_editor_property('Item').id,water.id) and abs(drop.get_editor_property('Item').condition-water.condition)<.001)
 targets[host]=drop;aim(host,hp,drop)
def transfer(i,to):i.request_transfer(items(i if to else external.get_editor_property('Container'))[0].id,1,to)
for pc in [host,client]:
 unreal.SystemLibrary.execute_console_command(pc,'t.MaxFPS 60',pc)
 unreal.SystemLibrary.execute_console_command(pc,'rv.Inventory.Debug 1',pc)
at(0,lambda:pickup('Water'));at(.5,lambda:key(host,'E',True));at(1.4,lambda:key(host,'E',False));at(2,save_water)
at(2.2,do_drop);at(3,drop_aim);at(3.5,lambda:key(host,'E',True));at(4.4,lambda:key(host,'E',False));at(5,lambda:check('repick',count(hi)==3 and unreal.GuidLibrary.equal_equal_guid_guid(items(hi)[0].id,water.id)))
at(5.2,lambda:pickup('EnginePart'));at(5.7,lambda:key(host,'E',True));at(6.6,lambda:key(host,'E',False));at(7,lambda:check('non_stackable',len(items(hi))==2))
at(7.2,lambda:pickup('FuelCan'));at(7.7,lambda:key(host,'E',True));at(8.6,lambda:key(host,'E',False));at(9,lambda:check('weight_block',count(hi)==4 and 'Weight' in hi.can_accept(find(sw,'FuelCan').get_editor_property('Item'))))
at(9.2,lambda:pickup('Bulky'));at(9.7,lambda:key(host,'E',True));at(10.6,lambda:key(host,'E',False));at(11,lambda:check('volume_block',count(hi)==4 and 'Volume' in hi.can_accept(find(sw,'Bulky').get_editor_property('Item'))))
at(11.2,lambda:arrange(host,hp,hp,external));at(11.7,lambda:key(host,'E',True));at(12.6,lambda:key(host,'E',False));at(13,lambda:check('open_container',hi.get_editor_property('OpenContainer')==external.get_editor_property('Container')))
at(13.2,lambda:transfer(hi,True));at(14,lambda:check('player_to_container',count(external.get_editor_property('Container'))==1 and count(hi)==3))
at(14.2,lambda:transfer(hi,False));at(15,lambda:check('container_to_player',count(external.get_editor_property('Container'))==0 and count(hi)==4))
at(15.2,lambda:pickup('Bandage',client));at(15.7,lambda:key(client,'E',True));at(16.6,lambda:key(client,'E',False));at(17.5,lambda:check('client_pickup_replicates',count(ci)==3 and count(si)==3))
at(17.7,lambda:arrange(client,sp,cp,external));at(18.2,lambda:key(client,'E',True));at(19.1,lambda:key(client,'E',False));at(20,lambda:ci.request_transfer(items(ci)[0].id,1,True));at(21,lambda:check('shared_container_replication',count(external.get_editor_property('Container'))==1 and count(cexternal.get_editor_property('Container'))==1,{'server_count':count(external.get_editor_property('Container')),'client_count':count(cexternal.get_editor_property('Container')),'client_open':str(ci.get_editor_property('OpenContainer')),'server_open':str(si.get_editor_property('OpenContainer')),'feedback':str(si.get_editor_property('Feedback'))}))
at(21.2,lambda:pickup('Food'));at(21.3,lambda:pickup('Food',client));at(22,lambda:(key(host,'E',True),key(client,'E',True)));at(23,lambda:(key(host,'E',False),key(client,'E',False)));at(24,lambda:check('contended_pickup_one_winner',sum(x.quantity for i in [hi,si] for x in items(i) if str(x.definition.get_editor_property('CatalogId'))=='Food')==3))
at(25,lambda:check('condition_after_transfer',all(abs(x.condition-.73)<.001 for i in [hi,ci,external.get_editor_property('Container')] for x in items(i))))
snapshots={}
def category_count(i,name):return sum(x.quantity for x in items(i) if str(x.definition.get_editor_property('CatalogId'))==name)
def signature(i):return sorted((unreal.GuidLibrary.conv_guid_to_string(x.id),x.quantity,round(x.condition,4)) for x in items(i))
def mark_counts():snapshots['counts']=(count(hi),count(si),count(external.get_editor_property('Container')))
def limit_container():
 mark_counts();external.get_editor_property('Container').set_editor_property('MaxVolumeLitres',0)
def claim_shared():
 c=external.get_editor_property('Container');hi.request_transfer(items(c)[0].id,1,False);ci.request_transfer(items(cexternal.get_editor_property('Container'))[0].id,1,False)
def reject_foreign():
 mark_counts();ci.request_transfer(items(hi)[0].id,1,True)
def client_drop():ci.request_drop(items(ci)[0].id,1)
def arrange_dropped():
 a=find(sw,'Bandage');arrange(host,hp,hp,a);arrange(client,sp,cp,a)
def dropped_replica():
 a=find(sw,'Bandage');b=find(cw,'Bandage');check('client_drop_replicated_state',unreal.GuidLibrary.equal_equal_guid_guid(a.get_editor_property('Item').id,b.get_editor_property('Item').id) and abs(a.get_editor_property('Item').condition-.73)<.001)
def unique_ids():
 ids=[unreal.GuidLibrary.conv_guid_to_string(x.id) for i in [hi,si,external.get_editor_property('Container')] for x in items(i)]
 check('unique_runtime_ids',len(ids)==len(set(ids)),ids)
 check('custom_state_preserved',all(x.custom_state and str(x.custom_state[0].key)=='Batch' and x.custom_state[0].value=='Gate4Prototype' for i in [hi,si,external.get_editor_property('Container')] for x in items(i)))
def out_of_range():
 snapshots['before_range']=signature(si);sp.set_actor_location(unreal.Vector(2500,-350,100),False,True)
def restore_client():arrange(client,sp,cp,external)
def snapshot_shared():snapshots['shared']=signature(external.get_editor_property('Container'))
def disconnect():
 global client,cp,cw,ci,cexternal,sp,si,ws
 controller=client;targets.pop(controller,None);client=cp=cw=ci=cexternal=sp=si=None;ws=[];globals()['pc']=None
 unreal.SystemLibrary.execute_console_command(controller,'disconnect',controller)
at(26,lambda:arrange(host,hp,hp,external));at(26.1,restore_client)
at(26.6,lambda:(key(host,'E',True),key(client,'E',True)));at(27.5,lambda:(key(host,'E',False),key(client,'E',False)))
at(28,lambda:check('two_users_same_container',hi.get_editor_property('OpenContainer')==external.get_editor_property('Container') and si.get_editor_property('OpenContainer')==external.get_editor_property('Container') and ci.get_editor_property('OpenContainer')==cexternal.get_editor_property('Container')))
at(28.2,limit_container);at(28.5,lambda:hi.request_transfer(items(hi)[0].id,1,True));at(29.2,lambda:check('container_full_atomic_rejection',(count(hi),count(si),count(external.get_editor_property('Container')))==snapshots['counts'] and 'Volume' in str(hi.get_editor_property('Feedback'))))
at(29.3,lambda:external.get_editor_property('Container').set_editor_property('MaxVolumeLitres',120));at(29.7,claim_shared)
at(30.7,lambda:check('contended_container_one_winner_no_duplication',count(external.get_editor_property('Container'))==0 and count(cexternal.get_editor_property('Container'))==0 and category_count(hi,'Bandage')+category_count(si,'Bandage')==3))
at(31,reject_foreign);at(32,lambda:check('foreign_item_id_rejected',(count(hi),count(si),count(external.get_editor_property('Container')))==snapshots['counts']))
at(32.5,client_drop);at(33.5,dropped_replica);at(34,arrange_dropped);at(34.5,lambda:(key(host,'E',True),key(client,'E',True)));at(35.5,lambda:(key(host,'E',False),key(client,'E',False)))
at(36.5,lambda:check('drop_immediate_contended_repick_no_duplication',category_count(hi,'Bandage')+category_count(si,'Bandage')==3 and not [a for a in unreal.GameplayStatics.get_all_actors_of_class(cw,PC) if str(a.get_editor_property('Item').definition.get_editor_property('CatalogId'))=='Bandage']))
at(36.7,unique_ids);at(37,lambda:check('physical_carry_excluded_from_backpack','physical carrying' in hi.can_accept(find(sw,'Battery').get_editor_property('Item'))))
at(37.5,out_of_range);at(38.2,lambda:ci.request_transfer(items(ci)[0].id,1,True));at(39.2,lambda:check('stale_container_access_rejected',si.get_editor_property('OpenContainer') is None and signature(si)==snapshots['before_range']))
at(39.5,restore_client);at(40.2,lambda:key(client,'E',True));at(41.2,lambda:key(client,'E',False));at(41.7,lambda:ci.request_transfer(items(ci)[0].id,1,True));at(43,snapshot_shared);at(43.2,disconnect)
at(47,lambda:check('disconnect_preserves_shared_container',signature(external.get_editor_property('Container'))==snapshots['shared'] and count(external.get_editor_property('Container'))>0))
def finish():
 unreal.unregister_slate_post_tick_callback(h);json.dump({'results':rows},open(B+'full.json','w'),indent=2)
at(49,finish)
def tick(dt):
 global t,index
 t+=dt
 try:
  while index<len(events) and t>=events[index][0]:
   action=events[index][1];index+=1;action()
 except Exception as e:
  check('runner_exception',False,repr(e));finish()
h=unreal.register_slate_post_tick_callback(tick)
