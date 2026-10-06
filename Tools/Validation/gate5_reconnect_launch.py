import unreal,json,time,os
from runner_runtime import load_runner,release_runners
B='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate5Validation/'
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level('/Game/Maps/Gate5SurvivalTest')
s=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.LevelEditorPlaySettings'));s.set_editor_property('PlayNumberOfClients',2);s.set_editor_property('RunUnderOneProcess',False);s.set_editor_property('AdditionalLaunchParameters','-ExecCmds="py '+B+'reconnect_startup.py"')
n=s.get_editor_property('NetworkEmulationSettings');n.set_editor_property('bIsNetworkEmulationEnabled',True);o=n.get_editor_property('OutPackets');o.set_editor_property('MinLatency',100);o.set_editor_property('MaxLatency',100);o.set_editor_property('PacketLossPercentage',2);n.set_editor_property('OutPackets',o);s.set_editor_property('NetworkEmulationSettings',n)
unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings')).set_editor_property('bThrottleCPUWhenNotForeground',False)
started=time.time();seeded=False;initial_pawn='';disconnected=False;rejoined=False;ending=None;rows=[];ids={}
def check(name,ok,detail=''):rows.append({'case':name,'pass':bool(ok),'detail':str(detail)});unreal.log('GATE5_RECONNECT '+json.dumps(rows[-1]))
def add(i,name,q):
 x=unreal.RVItemInstance();x.set_editor_property('Id',unreal.GuidLibrary.new_guid());x.set_editor_property('Definition',unreal.load_asset('/Game/Items/DA_'+name));x.set_editor_property('Quantity',q);x.set_editor_property('Condition',.54);d=unreal.RVItemStateEntry();d.set_editor_property('Key','Batch');d.set_editor_property('Value','ReconnectTest');x.set_editor_property('CustomState',[d]);i.add_authority(x);ids[name]=unreal.GuidLibrary.conv_guid_to_string(x.id)
def inspect_server():
 global seeded,initial_pawn,disconnected,rejoined
 w=next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='Gate5SurvivalTest' and unreal.GameplayStatics.get_game_mode(w));pc=unreal.GameplayStatics.get_player_controller(w,0);host=pc.get_controlled_pawn();hn=pc.get_editor_property('PlayerState').get_editor_property('Needs');cs=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSurvivorCharacter);remote=next((a for a in cs if a!=host),None)
 bed=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVRestPoint) if str(a.get_editor_property('DisplayName'))=='Rear bed');storage=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVStoragePoint) if str(a.get_editor_property('Container').get_editor_property('DisplayName'))=='External storage').get_editor_property('Container')
 if not seeded and remote:
  unreal.SystemLibrary.execute_console_command(pc,'rv.Needs.AllowDebug 1',pc);hn.debug_set_values(35,45,55);hn.debug_set_time_scale(0);rn=remote.get_editor_property('PlayerState').get_editor_property('Needs');rn.debug_set_values(40,50,80);rn.debug_set_time_scale(0)
  add(host.get_component_by_class(unreal.RVInventoryComponent),'Water',1);add(storage,'Food',2);add(storage,'Bandage',1)
  remote.set_actor_location(bed.get_attach_parent_actor().get_actor_transform().transform_location(unreal.Vector(-180,0,195)),False,True);initial_pawn=remote.get_name();seeded=True
 if seeded and not remote and not disconnected:
  check('disconnect_releases_bed',bed.get_editor_property('Occupant') is None);check('host_needs_unchanged_after_disconnect',abs(hn.get_editor_property('State').nutrition-35)<.01);disconnected=True
 if disconnected and remote and remote.get_name()!=initial_pawn and not rejoined:
  rn=remote.get_editor_property('PlayerState').get_editor_property('Needs');check('native_rejoin_state_valid',all(0<=v<=100 for v in [rn.get_editor_property('State').nutrition,rn.get_editor_property('State').hydration,rn.get_editor_property('State').fatigue]),{'old_pawn':initial_pawn,'new_pawn':remote.get_name()})
  rn.debug_set_values(30,40,50);rn.debug_set_time_scale(0);remote.set_actor_location(storage.get_owner().get_actor_location()+unreal.Vector(-140,50,62),False,True);rejoined=True
 if rejoined and os.path.exists(B+'reconnect_client.json') and os.path.getmtime(B+'reconnect_client.json')>started:
  hnstate=hn.get_editor_property('State');check('host_needs_unchanged_after_rejoin_and_foreign_consume',hnstate.nutrition==35 and hnstate.hydration==45 and hnstate.fatigue==55)
  check('host_item_identity_preserved',unreal.GuidLibrary.conv_guid_to_string(host.get_component_by_class(unreal.RVInventoryComponent).get_items()[0].id)==ids['Water'])
  check('shared_container_conservation',sum(x.quantity for x in storage.get_items())==2)
  check('bed_not_locked_after_rejoin',bed.get_editor_property('Occupant') is None)
  json.dump({'pid':os.getpid(),'results':rows},open(B+'reconnect_server.json','w'),indent=2);return True
 return False
def tick(dt):
 global ending
 try:
  if not ending and inspect_server():unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play();ending=time.time()+4
  if ending and time.time()>ending:
   unreal.unregister_slate_post_tick_callback(h);quit=unreal.SystemLibrary.quit_editor;release_runners();quit();return
  if not ending and time.time()-started>100:check('server_timeout',False);json.dump({'results':rows},open(B+'reconnect_server.json','w'),indent=2);unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play();ending=time.time()+4
 except StopIteration:return
 except Exception as e:check('runner_exception',False,repr(e));unreal.unregister_slate_post_tick_callback(h)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play();h=unreal.register_slate_post_tick_callback(tick)
