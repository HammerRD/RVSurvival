"""Boundary/expiry/recovery diagnostics; no UI or network acceptance claim."""
import unreal,json,time
from pathlib import Path
B=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate8Validation')
w=next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='Gate8MedicalTest' and 'UEDPIE_' in w.get_path_name())
pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn();ps=pc.player_state;health=ps.get_editor_property('Health');inv=p.get_component_by_class(unreal.RVInventoryComponent)
results=[];events=[];start=time.time();supply=None;before=100
def check(n,b,d=''):results.append({'case':n,'pass':bool(b),'detail':str(d)})
def injuries():return health.get_editor_property('Injuries')
def attr(n):return ps.get_editor_property('MedicalAttributes').get_editor_property(n).get_editor_property('CurrentValue')
def seed(name):
 r=unreal.RVItemInstance();r.set_editor_property('Id',unreal.GuidLibrary.new_guid());r.set_editor_property('Definition',unreal.load_asset('/Game/Development/Medical/DA_'+name));r.set_editor_property('Quantity',1);inv.add_authority(r);return inv.get_items()[-1].id

item_id=None;fracture=None;velocity_before=0
def fixture():
 global item_id
 health.debug_clear_injuries();p.set_actor_location(unreal.Vector(100,-500,95),False,True)
 item=unreal.RVItemInstance();item.set_editor_property('Id',unreal.GuidLibrary.new_guid());item.set_editor_property('Definition',unreal.load_asset('/Game/Medical/DA_Bandage'));item.set_editor_property('Condition',.47);inv.add_authority(item);item_id=inv.get_items()[0].id;inv.request_drop(item_id,1)
def dropped():
 check('medical_drop_removed_inventory',len(inv.get_items())==0)
 pickup=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVWorldItem) if unreal.GuidLibrary.conv_guid_to_string(a.get_editor_property('Item').id)==unreal.GuidLibrary.conv_guid_to_string(item_id))
 check('medical_world_drop_condition',abs(pickup.get_editor_property('Item').condition-.47)<.0001)
 pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p.get_actor_location()+unreal.Vector(0,0,64),pickup.get_actor_location()))
 unreal.RVInteriorMotorhome.dispatch_development_key(pc,'E',True)
def repicked():
 unreal.RVInteriorMotorhome.dispatch_development_key(pc,'E',False)
 check('normal_E_medical_repick_GUID_condition',len(inv.get_items())==1 and unreal.GuidLibrary.conv_guid_to_string(inv.get_items()[0].id)==unreal.GuidLibrary.conv_guid_to_string(item_id) and abs(inv.get_items()[0].condition-.47)<.0001)
 pc.set_control_rotation(unreal.Rotator(yaw=0));health.debug_apply_injury(unreal.RVInjuryKind.FRACTURE,unreal.RVBodyRegion.LEFT_LEG,2)
 unreal.RVInteriorMotorhome.dispatch_development_key(pc,'W',True)
def limited():
 global velocity_before
 velocity_before=p.get_velocity().length();check('leg_fracture_native_walk_slowed',180<velocity_before<240,velocity_before);unreal.RVInteriorMotorhome.dispatch_development_key(pc,'W',False)
 item=unreal.RVItemInstance();item.set_editor_property('Id',unreal.GuidLibrary.new_guid());item.set_editor_property('Definition',unreal.load_asset('/Game/Medical/DA_Splint'));inv.add_authority(item)
 i=injuries()[0];health.request_treatment(ps,i.id,inv.get_items()[-1].id,i.revision)
def after_splint():
 check('splint_retains_fracture',injuries()[0].kind==unreal.RVInjuryKind.FRACTURE and injuries()[0].get_editor_property('bStabilized'))
 unreal.RVInteriorMotorhome.dispatch_development_key(pc,'W',True)
def restored():
 speed=p.get_velocity().length();check('splint_native_walk_improved_not_full',speed>velocity_before+100 and 350<speed<430,speed);unreal.RVInteriorMotorhome.dispatch_development_key(pc,'W',False)
def finish():
 unreal.unregister_slate_post_tick_callback(handle);(B/'medical-actions.json').write_text(json.dumps({'kind':'normal E repick/W walking; owned drop/treatment diagnostics','results':results},indent=2))
events=[(1,fixture),(3,dropped),(4.5,repicked),(5.5,limited),(17,after_splint),(18,restored),(19,finish)]
def tick(dt):
 try:
  if events and time.time()-start>=events[0][0]:_,fn=events.pop(0);fn()
 except Exception as e:check('harness_exception',False,repr(e));events.clear();finish()
handle=unreal.register_slate_post_tick_callback(tick)
