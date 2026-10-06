import unreal,json,time,os
B='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate5Validation/'
worlds=sorted([w for w in unreal.ObjectIterator(unreal.World) if 'UEDPIE_' in w.get_path_name() and w.get_name()=='Gate5SurvivalTest'],key=lambda w:w.get_path_name());sw,w=worlds
host=unreal.GameplayStatics.get_player_controller(sw,0);hp=host.get_controlled_pawn();serverp=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(sw,unreal.RVSurvivorCharacter) if a!=hp)
pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn();i=p.get_component_by_class(unreal.RVInventoryComponent);si=serverp.get_component_by_class(unreal.RVInventoryComponent);sn=serverp.get_editor_property('PlayerState').get_editor_property('Needs');n=pc.get_editor_property('PlayerState').get_editor_property('Needs')
unreal.SystemLibrary.execute_console_command(host,'rv.Needs.AllowDebug 1',host);sn.debug_set_values(40,40,40);sn.debug_set_time_scale(0)
for name in ['Food','Water']:
 item=unreal.RVItemInstance();item.set_editor_property('Id',unreal.GuidLibrary.new_guid());item.set_editor_property('Definition',unreal.load_asset('/Game/Items/DA_'+name));item.set_editor_property('Quantity',2);item.set_editor_property('Condition',.73);si.add_authority(item)
serverp.set_actor_location(unreal.Vector(700,-400,100),False,True)
started=time.time();samples=[];last=None

def state(component):s=component.get_editor_property('State');return {'nutrition':s.nutrition,'hydration':s.hydration,'fatigue':s.fatigue,'rest':str(s.rest_mode)}
def tick(dt):
 global last
 elapsed=time.time()-started;samples.append({'t':elapsed,'client_items':[(str(x.definition.get_editor_property('CatalogId')),x.quantity) for x in i.get_items()],'server_items':[(str(x.definition.get_editor_property('CatalogId')),x.quantity) for x in si.get_items()],'client_needs':state(n),'server_needs':state(sn)})
 try:command=json.load(open(B+'ui_command.json')).get('command')
 except (OSError,ValueError):command=None
 if command!=last:
  last=command
  if command=='critical':sn.debug_set_values(5,5,90)
  if command=='rest':
   bed=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(sw,unreal.RVRestPoint) if str(a.get_editor_property('DisplayName'))=='Rear bed');serverp.set_actor_location(bed.get_attach_parent_actor().get_actor_transform().transform_location(unreal.Vector(-180,0,195)),False,True)
   sn.debug_set_values(40,40,80)
  if command=='hold':
   bed=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVRestPoint) if str(a.get_editor_property('DisplayName'))=='Rear bed');pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p.get_actor_location()+unreal.Vector(0,0,64),bed.get_actor_location()));unreal.SystemLibrary.execute_console_command(pc,'Input.+key E',pc)
  if command=='release':unreal.SystemLibrary.execute_console_command(pc,'Input.-key E',pc)
 if command=='finish' or elapsed>240:
  unreal.unregister_slate_post_tick_callback(handle);json.dump({'samples':samples,'timeout':elapsed>240},open(B+'ui.json','w'),indent=2)
handle=unreal.register_slate_post_tick_callback(tick)
