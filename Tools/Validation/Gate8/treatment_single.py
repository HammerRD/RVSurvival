"""Focused transaction diagnostics, not normal-control acceptance."""
import unreal,json,time
from pathlib import Path
B=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate8Validation')
w=next(a for a in unreal.ObjectIterator(unreal.World) if a.get_name()=='Gate8MedicalTest' and 'UEDPIE_' in a.get_path_name())
pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn();ps=pc.player_state
hth=ps.get_editor_property('Health');inv=p.get_component_by_class(unreal.RVInventoryComponent)
results=[];start=time.time();events=[];ids={};fracture=None;burn=None
def check(name,value):results.append({'case':name,'pass':bool(value)})
def items(name):return [i for i in inv.get_items() if str(i.definition.get_editor_property('DisplayName'))==name]
def qty(name):return sum(i.quantity for i in items(name))
def injury(uid):return next(i for i in hth.get_editor_property('Injuries') if unreal.GuidLibrary.conv_guid_to_string(i.id)==unreal.GuidLibrary.conv_guid_to_string(uid))
def seed():
 global fracture,burn
 hth.debug_apply_injury(unreal.RVInjuryKind.FRACTURE,unreal.RVBodyRegion.LEFT_LEG,2)
 hth.debug_apply_injury(unreal.RVInjuryKind.BURN,unreal.RVBodyRegion.RIGHT_ARM,2)
 fracture,burn=[i.id for i in hth.get_editor_property('Injuries')]
 for name in ['Splint','PainMedication','BurnDressing','Antiseptic']:
  r=unreal.RVItemInstance();r.set_editor_property('Id',unreal.GuidLibrary.new_guid());r.set_editor_property('Definition',unreal.load_asset('/Game/Medical/DA_'+name));r.set_editor_property('Quantity',2);r.set_editor_property('Condition',.83);inv.add_authority(r)
  ids[name]=items(name)[0].id
 hth.request_treatment(ps,fracture,ids['Splint'],0)
def cancel():hth.request_cancel_treatment()
def retry():
 check('cancel_retains_splint',qty('Splint')==2)
 check('cancel_leaves_fracture_untreated',not injury(fracture).get_editor_property('bStabilized'))
 hth.request_treatment(ps,fracture,ids['Splint'],0)
def splinted():
 check('splint_completed',injury(fracture).get_editor_property('bStabilized'))
 check('splint_consumed_once',qty('Splint')==1)
 check('fracture_retained',injury(fracture).healing<1)
 check('splinted_speed_scale',abs(hth.get_movement_scale()-.65)<.01)
 hth.request_treatment(ps,fracture,ids['PainMedication'],injury(fracture).revision)
def medication():
 check('GAS_analgesia',ps.get_editor_property('MedicalAttributes').get_editor_property('Analgesia').get_editor_property('CurrentValue')>0)
 check('medication_consumed_once',qty('PainMedication')==1)
 check('medication_does_not_erase_injury',len(hth.get_editor_property('Injuries'))==2)
 hth.request_treatment(ps,burn,ids['BurnDressing'],0)
def dressed():
 check('burn_dressing_completed',injury(burn).get_editor_property('bTreated'))
 check('burn_dressing_consumed_once',qty('BurnDressing')==1)
 hth.request_treatment(ps,burn,ids['Antiseptic'],injury(burn).revision)
def cleaned():
 check('antiseptic_reduces_risk',injury(burn).infection_risk<.01)
 check('antiseptic_consumed_once',qty('Antiseptic')==1)
 check('conditions_preserved',all(abs(i.condition-.83)<.0001 for i in inv.get_items()))
 check('GUIDs_preserved',all(unreal.GuidLibrary.conv_guid_to_string(items(n)[0].id)==unreal.GuidLibrary.conv_guid_to_string(uid) for n,uid in ids.items()))
 hth.request_treatment(ps,unreal.Guid(),ids['Splint'],0)
def finish():
 check('invalid_GUID_no_consumption',qty('Splint')==1)
 unreal.unregister_slate_post_tick_callback(handle)
 (B/'treatment-single.json').write_text(json.dumps({'kind':'component transaction diagnostics; no normal-player acceptance','results':results},indent=2))
events=[(1,seed),(3,cancel),(4,retry),(16,splinted),(20,medication),(30,dressed),(37,cleaned),(39,finish)]
def tick(dt):
 try:
  if events and time.time()-start>=events[0][0]:_,fn=events.pop(0);fn()
 except Exception as e:
  results.append({'case':'harness_exception','pass':False,'detail':repr(e)});finish();events.clear()
handle=unreal.register_slate_post_tick_callback(tick)
