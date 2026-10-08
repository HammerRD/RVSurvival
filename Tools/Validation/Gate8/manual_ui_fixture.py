"""Initial state only. Actual F9/button input is supplied through the native window."""
import unreal,json,time
from pathlib import Path
B=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate8Validation')
w=next(a for a in unreal.ObjectIterator(unreal.World) if a.get_name()=='Gate8MedicalTest' and 'UEDPIE_' in a.get_path_name())
pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn();ps=pc.player_state
health=ps.get_editor_property('Health');inventory=p.get_component_by_class(unreal.RVInventoryComponent)
health.debug_apply_injury(unreal.RVInjuryKind.WOUND,unreal.RVBodyRegion.RIGHT_LEG,2)
health.debug_apply_injury(unreal.RVInjuryKind.FRACTURE,unreal.RVBodyRegion.LEFT_LEG,2)
for name in ['Bandage','Splint','PainMedication']:
 record=unreal.RVItemInstance();record.set_editor_property('Id',unreal.GuidLibrary.new_guid())
 record.set_editor_property('Definition',unreal.load_asset('/Game/Medical/DA_'+name));record.set_editor_property('Quantity',3);record.set_editor_property('Condition',.83)
 inventory.add_authority(record)
samples=[];last=0
def tick(dt):
 global last
 if not unreal.SystemLibrary.is_valid(health):
  unreal.unregister_slate_post_tick_callback(h);return
 if time.time()-last<.5:return
 last=time.time()
 samples.append({'time':last,'feedback':health.get_editor_property('Feedback'),'pain':health.get_pain(),'movement_scale':health.get_movement_scale(),'speed':p.get_velocity().length(),'position':str(p.get_actor_location()),'injuries':[{'type':str(i.kind),'bleed':i.bleeding_per_minute,'stabilized':i.get_editor_property('bStabilized'),'revision':i.revision} for i in health.get_editor_property('Injuries')],'items':[{'id':unreal.GuidLibrary.conv_guid_to_string(i.id),'quantity':i.quantity,'condition':i.condition,'name':str(i.definition.get_editor_property('DisplayName'))} for i in inventory.get_items()]})
 (B/'manual-ui-samples.json').write_text(json.dumps(samples,indent=2),encoding='utf-8')
h=unreal.register_slate_post_tick_callback(tick)
def release():unreal.unregister_slate_post_tick_callback(h)
(B/'manual-ui-ready.json').write_text(json.dumps({'initial_fixture':True,'input':'normal OS F9 and UMG mouse clicks; not component shortcut'},indent=2),encoding='utf-8')

