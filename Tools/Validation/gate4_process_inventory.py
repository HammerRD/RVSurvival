import unreal,json,time,os
B='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate4Validation/'
session=json.load(open(B+'process_session.json'));config=session['config'];start=session['start'];out=config['name']
CC=unreal.load_class(None,'/Script/RVSurvival.RVSurvivorCharacter');IC=unreal.load_class(None,'/Script/RVSurvival.RVInventoryComponent');PC=unreal.load_class(None,'/Script/RVSurvival.RVWorldItem');SC=unreal.load_class(None,'/Script/RVSurvival.RVStoragePoint')
world=next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='Gate4InventoryTest' and unreal.GameplayStatics.get_player_controller(w,0) and unreal.GameplayStatics.get_player_controller(w,0).get_controlled_pawn())
is_server=unreal.GameplayStatics.get_game_mode(world) is not None;own=unreal.GameplayStatics.get_player_controller(world,0);ownpawn=own.get_controlled_pawn();other=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world,CC) if a!=ownpawn)
hp=ownpawn if is_server else other;cp=other if is_server else ownpawn;hi=hp.get_component_by_class(IC);ci=cp.get_component_by_class(IC)
ext=min(unreal.GameplayStatics.get_all_actors_of_class(world,SC),key=lambda a:(a.get_actor_location()-unreal.Vector(600,-350,100)).length());container=ext.get_editor_property('Container')
rows=[];samples=[];events=[];idx=0;active=True;initial_ids={};snapshots={};sample_at=0

def guid(g):return unreal.GuidLibrary.conv_guid_to_string(g)
def items(i):return i.get_items()
def qty(i):return sum(x.quantity for x in items(i))
def named(i,name):return next(x for x in items(i) if str(x.definition.get_editor_property('CatalogId'))==name)
def sig(i):return sorted((guid(x.id),str(x.definition.get_editor_property('CatalogId')),x.quantity,round(x.condition,4)) for x in items(i))
def pickups(name):return [a for a in unreal.GameplayStatics.get_all_actors_of_class(world,PC) if a.get_editor_property('Item').definition and str(a.get_editor_property('Item').definition.get_editor_property('CatalogId'))==name]
def find(name):return pickups(name)[0]
def check(name,ok,detail=''):
 row={'case':name,'pass':bool(ok),'detail':str(detail)};rows.append(row);unreal.log('GATE4_PROCESS '+json.dumps(row))
def at(t,f):events.append((t,f))
def key(k,on):unreal.SystemLibrary.execute_console_command(own,'Input.'+('+' if on else '-')+'key '+k,own)
def aim(actor):own.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(ownpawn.get_actor_location()+unreal.Vector(0,0,64),actor.get_actor_location()))
def arrange(p,actor,y):
 if not is_server:return
 pos=actor.get_actor_location()+unreal.Vector(-140,y,62);pos.z=max(100,pos.z);p.set_actor_location(pos,False,True)
def arrange_both(actor):arrange(hp,actor,-50);arrange(cp,actor,50)
def own_hold(actor):aim(actor);key('E',True)
def initial(name,inventory):initial_ids[name]=guid(named(inventory,name).id)
def withdraw():ownpawn.get_component_by_class(IC).request_transfer(named(container,'Water').id,1,False)
def set_limit(value):
 if is_server:container.set_editor_property('MaxVolumeLitres',value)
def snapshot():snapshots['counts']=(qty(hi),qty(ci),qty(container))
def failed_capacity():check('full_container_preserves_source',(qty(hi),qty(ci),qty(container))==snapshots['counts'])
def drop_client():
 if not is_server:ci.request_drop(named(ci,'Bandage').id,named(ci,'Bandage').quantity)
def drop_check():
 a=find('Bandage').get_editor_property('Item');check('client_drop_identity_condition',guid(a.id)==initial_ids['Bandage'] and a.quantity==2 and abs(a.condition-.73)<.001 and a.custom_state[0].value=='Gate4Prototype')
def foreign():
 if not is_server:ci.request_transfer(named(hi,'Water').id,1,True)
def native_client_cannot_mint():
 if is_server:return
 before=qty(ci);item=unreal.RVItemInstance();item.set_editor_property('Id',unreal.GuidLibrary.new_guid());item.set_editor_property('Definition',unreal.load_asset('/Game/Items/DA_Water'))
 ci.add_authority(item);check('client_cannot_add_authority_items',qty(ci)==before)
def sample():samples.append({'epoch':time.time(),'t':time.time()-start,'host':sig(hi),'client':sig(ci),'container':sig(container)})
def finish_client():
 global active,own,ownpawn,other,hp,cp,hi,ci,world,ext,container
 if is_server:return
 sample();check('client_completed_sequence',True)
 json.dump({'server':False,'pid':os.getpid(),'config':config,'results':rows,'samples':samples},open(B+out+'_client.json','w'),indent=2)
 active=False;unreal.unregister_slate_post_tick_callback(handle)
 controller=own;own=ownpawn=other=hp=cp=hi=ci=world=ext=container=None
 unreal.SystemLibrary.execute_console_command(controller,'disconnect',controller)
def finish_server():
 global active
 if not is_server:return
 check('disconnect_shared_contents_preserved',sig(container)==snapshots.get('disconnect') and qty(container)==1)
 active=False;unreal.unregister_slate_post_tick_callback(handle)
 json.dump({'server':True,'pid':os.getpid(),'config':config,'results':rows,'samples':samples},open(B+out+'_server.json','w'),indent=2)
for command in ['t.MaxFPS 60','t.IdleWhenNotForeground 0','rv.Inventory.Debug 1']:unreal.SystemLibrary.execute_console_command(own,command,own)
at(0,lambda:arrange(hp,find('Water'),-50));at(.7,lambda:own_hold(find('Water')) if is_server else None);at(1.7,lambda:key('E',False) if is_server else None);at(2.3,lambda:(check('host_pickup',qty(hi)==3),initial('Water',hi)))
at(2.5,lambda:arrange(cp,find('Bandage'),50));at(3.2,lambda:own_hold(find('Bandage')) if not is_server else None);at(4.2,lambda:key('E',False) if not is_server else None);at(5,lambda:(check('client_pickup',qty(ci)==3),initial('Bandage',ci)))
at(5.2,lambda:arrange_both(ext));at(6,lambda:own_hold(ext));at(7,lambda:key('E',False));at(7.8,lambda:check('own_container_open',ownpawn.get_component_by_class(IC).get_editor_property('OpenContainer')==container))
at(8,lambda:hi.request_transfer(named(hi,'Water').id,1,True) if is_server else None);at(8.2,lambda:ci.request_transfer(named(ci,'Bandage').id,1,True) if not is_server else None)
at(9.8,lambda:check('concurrent_deposit_both_preserved',qty(container)==2 and qty(hi)==qty(ci)==2 and qty(hi)+qty(ci)+qty(container)==6,sig(container)))
at(10,withdraw);at(11.8,lambda:check('same_stack_withdraw_one_winner',qty(container)==1 and sum(x.quantity for i in [hi,ci] for x in items(i) if str(x.definition.get_editor_property('CatalogId'))=='Water')==3 and qty(hi)+qty(ci)+qty(container)==6))
at(12,snapshot);at(12.2,lambda:set_limit(.1));at(12.6,lambda:hi.request_transfer(named(hi,'Water').id,1,True) if is_server else None);at(14,failed_capacity);at(14.2,lambda:set_limit(120))
at(14.5,drop_client);at(16,drop_check);at(16.2,lambda:arrange_both(find('Bandage')));at(17,lambda:own_hold(find('Bandage')));at(18,lambda:key('E',False));at(19.5,lambda:check('dropped_contended_repick_no_duplication',not pickups('Bandage') and qty(hi)+qty(ci)+qty(container)==6))
at(19.8,snapshot);at(20,foreign);at(21.5,lambda:check('forged_item_id_no_mutation',(qty(hi),qty(ci),qty(container))==snapshots['counts']))
at(21.7,lambda:arrange_both(find('Food')));at(22.5,lambda:own_hold(find('Food')));at(23.5,lambda:key('E',False));at(25,lambda:check('contended_pickup_no_duplication',not pickups('Food') and qty(hi)+qty(ci)+qty(container)==9))
at(25.2,lambda:check('all_condition_custom_state_preserved',all(abs(x.condition-.73)<.001 and x.custom_state[0].value=='Gate4Prototype' for i in [hi,ci,container] for x in items(i))))
at(25.5,native_client_cannot_mint);at(26,lambda:snapshots.update(disconnect=sig(container)));at(27,finish_client);at(31,finish_server)
def tick(dt):
 global idx,sample_at
 if not active:return
 t=time.time()-start
 if t<0:return
 try:
  while idx<len(events) and t>=events[idx][0]:
   f=events[idx][1];idx+=1;f()
   if not active:return
  if t>=sample_at:sample();sample_at=t+.1
 except Exception as e:
  check('runner_exception',False,repr(e));finish_server() if is_server else finish_client()
handle=unreal.register_slate_post_tick_callback(tick)

