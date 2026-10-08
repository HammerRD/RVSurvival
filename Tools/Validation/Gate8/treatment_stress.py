"""Repeated native timer transactions target duplicate completion and cancellation leaks."""
import unreal,json,time
from pathlib import Path
B=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate8Validation')
w=next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='Gate8MedicalTest' and 'UEDPIE_' in w.get_path_name())
pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn();ps=pc.player_state;health=ps.get_editor_property('Health');inv=p.get_component_by_class(unreal.RVInventoryComponent)
for _ in range(2):
 item=unreal.RVItemInstance();item.set_editor_property('Id',unreal.GuidLibrary.new_guid());item.set_editor_property('Definition',unreal.load_asset('/Game/Development/Medical/DA_DiagnosticBandage'));item.set_editor_property('Quantity',10);item.set_editor_property('Condition',.62);inv.add_authority(item)
initial_ids={unreal.GuidLibrary.conv_guid_to_string(i.id) for i in inv.get_items()}
cycle=0;phase='begin';deadline=time.time()+1;failures=[];cancelled=0
def quantity():return sum(i.quantity for i in inv.get_items())
def begin():
 health.debug_clear_injuries();health.debug_apply_injury(unreal.RVInjuryKind.WOUND,unreal.RVBodyRegion.LEFT_ARM,1)
 i=health.get_editor_property('Injuries')[0];s=inv.get_items()[0]
 for _ in range(2):health.request_treatment(ps,i.id,s.id,i.revision)
def finish():
 unreal.unregister_slate_post_tick_callback(handle)
 (B/'treatment-stress.json').write_text(json.dumps({'kind':'20 repeated timer transactions, duplicate requests and every-fifth cancellation/retry','completed_cycles':cycle,'cancelled_retried':cancelled,'final_quantity':quantity(),'failures':failures},indent=2))
def tick(dt):
 global cycle,phase,deadline,cancelled
 if time.time()<deadline:return
 try:
  if phase=='begin':
   if cycle>=20:finish();return
   begin();phase='cancel' if cycle%5==0 else 'verify';deadline=time.time()+(.2 if phase=='cancel' else 1.5)
  elif phase=='cancel':health.request_cancel_treatment();phase='retry';deadline=time.time()+.3
  elif phase=='retry':
   if quantity()!=20-cycle:failures.append({'cycle':cycle,'reason':'cancel consumed supply'})
   cancelled+=1;begin();phase='verify';deadline=time.time()+1.5
  else:
   if quantity()!=19-cycle or health.get_editor_property('Injuries')[0].bleeding_per_minute!=0:failures.append({'cycle':cycle,'reason':'completion/quantity mismatch','quantity':quantity()})
   if any(i.quantity<=0 or abs(i.condition-.62)>.0001 or unreal.GuidLibrary.conv_guid_to_string(i.id) not in initial_ids for i in inv.get_items()):failures.append({'cycle':cycle,'reason':'instance integrity'})
   cycle+=1;phase='begin';deadline=time.time()+.1
 except Exception as e:failures.append({'cycle':cycle,'exception':repr(e)});finish()
handle=unreal.register_slate_post_tick_callback(tick)
