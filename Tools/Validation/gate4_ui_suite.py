import unreal,json,time
B='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate4Validation/'
worlds=sorted([w for w in unreal.ObjectIterator(unreal.World) if '/Game/Maps/UEDPIE_' in w.get_path_name() and w.get_name()=='Gate4InventoryTest'],key=lambda w:w.get_path_name());sw,w=worlds
server_host=unreal.GameplayStatics.get_player_controller(sw,0).get_controlled_pawn();server_p=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(sw,unreal.load_class(None,'/Script/RVSurvival.RVSurvivorCharacter')) if a!=server_host);server_inv=server_p.get_component_by_class(unreal.load_class(None,'/Script/RVSurvival.RVInventoryComponent'))
pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn();inventory=p.get_component_by_class(unreal.load_class(None,'/Script/RVSurvival.RVInventoryComponent'))
storage=min(unreal.GameplayStatics.get_all_actors_of_class(w,unreal.load_class(None,'/Script/RVSurvival.RVStoragePoint')),key=lambda a:(a.get_actor_location()-unreal.Vector(600,-350,100)).length());container=storage.get_editor_property('Container')
server_storage=min(unreal.GameplayStatics.get_all_actors_of_class(sw,unreal.load_class(None,'/Script/RVSurvival.RVStoragePoint')),key=lambda a:(a.get_actor_location()-unreal.Vector(600,-350,100)).length());server_container=server_storage.get_editor_property('Container')
def seed():
 for name,qty in [('Water',3),('Tool',1)]:
  item=unreal.RVItemInstance();item.set_editor_property('Id',unreal.GuidLibrary.new_guid());item.set_editor_property('Definition',unreal.load_asset('/Game/Items/DA_'+name));item.set_editor_property('Quantity',qty);item.set_editor_property('Condition',.73);server_inv.add_authority(item)
 server_p.set_actor_location(storage.get_actor_location()+unreal.Vector(-140,0,62),False,True)
 pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p.get_actor_location()+unreal.Vector(0,0,64),storage.get_actor_location()))
seed();started=time.time();hold=False;opened=False;last_cmd=None;samples=[]
for command in ['t.MaxFPS 60','t.IdleWhenNotForeground 0']:unreal.SystemLibrary.execute_console_command(pc,command,pc)
def tick(dt):
 global hold,opened,last_cmd
 elapsed=time.time()-started
 if elapsed>1 and not hold:
  pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p.get_actor_location()+unreal.Vector(0,0,64),storage.get_actor_location()));unreal.SystemLibrary.execute_console_command(pc,'Input.+key E',pc);hold=True
 if elapsed>2 and not opened:unreal.SystemLibrary.execute_console_command(pc,'Input.-key E',pc);opened=True
 samples.append({'t':elapsed,'player':[(str(x.definition.get_editor_property('CatalogId')),x.quantity,x.condition) for x in inventory.get_items()],'container':[(str(x.definition.get_editor_property('CatalogId')),x.quantity,x.condition) for x in container.get_items()],'server_player':[(str(x.definition.get_editor_property('CatalogId')),x.quantity,x.condition) for x in server_inv.get_items()],'server_container':[(str(x.definition.get_editor_property('CatalogId')),x.quantity,x.condition) for x in server_container.get_items()],'open':bool(inventory.get_editor_property('OpenContainer')),'feedback':str(inventory.get_editor_property('Feedback'))})
 try:cmd=json.load(open(B+'ui_command.json')).get('command')
 except (OSError,ValueError):cmd=None
 if cmd=='full':server_container.set_editor_property('MaxVolumeLitres',.1)
 if cmd=='reset':server_container.set_editor_property('MaxVolumeLitres',120)
 if cmd=='finish':
  unreal.unregister_slate_post_tick_callback(handle);json.dump({'samples':samples},open(B+'ui.json','w'),indent=2)
handle=unreal.register_slate_post_tick_callback(tick)


