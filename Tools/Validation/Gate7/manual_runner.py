"""Live native-window inspection. Scoped UObject reacquisition, primitive state only."""
import unreal,time,json
from pathlib import Path
B=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate7Validation')
phase=0;deadline=0;nextsample=0;held=None
def step():
 global phase,deadline,held
 w=next(a for a in unreal.ObjectIterator(unreal.World) if a.get_name()=='Gate7MechanicalTest' and 'UEDPIE_' in a.get_path_name())
 pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn();v=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVMechanicalMotorhome)[0];c=v.get_editor_property('CoolingSystem');point=v.get_editor_property('EngineService');inv=p.get_component_by_class(unreal.RVInventoryComponent)
 now=time.time()
 if held and now>held[1]:
  unreal.RVInteriorMotorhome.dispatch_development_key(pc,held[0],False);held=None
 if phase==4 and not held and (B/'manual-command.json').exists():
  command=json.loads((B/'manual-command.json').read_text());(B/'manual-command.json').unlink()
  unreal.RVInteriorMotorhome.dispatch_development_key(pc,command['key'],True);held=(command['key'],now+command.get('seconds',.2))
 if phase==0:
  unreal.SystemLibrary.execute_console_command(w,"t.MaxFPS 60");unreal.SystemLibrary.execute_console_command(w,"t.IdleWhenNotForeground 0");c.debug_set_time_scale(0);c.debug_set_state(.7,7,20,1)
  for cat,quantity in [('MechanicTools',1),('RadiatorPatch',3),('CoolantPartial',1)]:
   record=unreal.RVItemInstance();record.set_editor_property('Id',unreal.GuidLibrary.new_guid());record.set_editor_property('Definition',unreal.load_asset('/Game/Mechanical/DA_'+cat));record.set_editor_property('Quantity',quantity);record.set_editor_property('Condition',.83);inv.add_authority(record)
  p.set_actor_location(v.get_actor_transform().transform_location(unreal.Vector(550,0,100)),False,True);phase=1;deadline=now+1
 elif phase==1 and now>deadline:
  pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p.get_actor_location()+unreal.Vector(0,0,64),point.get_actor_location()));phase=2;deadline=now+.5
 elif phase==2 and now>deadline:
  unreal.RVInteriorMotorhome.dispatch_development_key(pc,'E',True);phase=3;deadline=now+.85
 elif phase==3 and now>deadline:unreal.RVInteriorMotorhome.dispatch_development_key(pc,'E',False);phase=4
 items=[{'catalog':str(i.definition.get_editor_property('CatalogId')),'guid':unreal.GuidLibrary.conv_guid_to_string(i.id),'quantity':i.quantity,'condition':i.condition,'litres':i.fuel_litres,'revision':i.fuel_revision} for i in inv.get_items()]
 widgets=unreal.WidgetLibrary.get_all_widgets_of_class(w,unreal.RVMechanicalWidget,False)
 visible=[{'visibility':str(a.get_visibility()),'viewport':a.is_in_viewport(),'size':str(a.get_desired_size())} for a in widgets]
 return {'phase':phase,'service_open':pc.get_editor_property('MechanicalPoint')==point,'feedback':pc.get_editor_property('MechanicalFeedback'),'coolant':c.get_editor_property('Cooling').coolant_litres,'temporary_patch':c.get_editor_property('Cooling').get_editor_property('bTemporaryPatch'),'hood_open':v.get_editor_property('EngineHood').get_editor_property('bOpen'),'repair':str(point.get_editor_property('ActiveRepair')),'items':items,'widgets':visible,'position':str(p.get_actor_location())}
def tick(dt):
 global nextsample
 if time.time()<nextsample:return
 nextsample=time.time()+.25
 try:
  snapshot=step();(B/'manual-current.json').write_text(json.dumps(snapshot,indent=2),encoding='utf-8')
  with open(B/'manual-actions.jsonl','a') as output:output.write(json.dumps(snapshot)+'\n')
  if (B/'manual-end').exists():
   unreal.unregister_slate_post_tick_callback(h);(B/'manual-finished').write_text('done')
 except Exception as e:
  unreal.log_error('GATE7_MANUAL '+repr(e));unreal.unregister_slate_post_tick_callback(h);(B/'manual-finished').write_text('failed')
h=unreal.register_slate_post_tick_callback(tick)
