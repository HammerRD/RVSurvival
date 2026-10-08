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
def bleeding():
 for severity,expected in [(1,.5),(2,3),(3,10)]:
  health.debug_apply_injury(unreal.RVInjuryKind.WOUND,unreal.RVBodyRegion.TORSO,severity);check('bleed_severity_'+str(severity),abs(injuries()[-1].bleeding_per_minute-expected)<.01)
 health.debug_set_time_scale(20)
def depleted():
 check('combined_bleed_reduces_blood',attr('Blood')<95,attr('Blood'));health.debug_set_time_scale(1)
 global supply;supply=seed('DiagnosticBandage');i=injuries()[-1];health.request_treatment(ps,i.id,supply,i.revision)
def severity_rejected():
 check('severe_rejected_by_basic_bandage',len(inv.get_items())==1 and inv.get_items()[0].quantity==1)
 check('severe_bleed_unchanged',injuries()[-1].bleeding_per_minute==10)
 health.debug_clear_injuries();health.debug_apply_injury(unreal.RVInjuryKind.FRACTURE,unreal.RVBodyRegion.LEFT_ARM,2)
 global supply;supply=seed('DiagnosticPainMedication');health.request_treatment(ps,injuries()[0].id,supply,0)
def relief():check('native_GAS_timed_relief_active',attr('Analgesia')>0);check('final_medication_item_removed',len(inv.get_items())==1)
def expired():
 check('native_GAS_relief_expired',abs(attr('Analgesia'))<.01);check('pain_returns_with_injury',health.get_pain()>19)
 health.debug_clear_injuries();health.debug_apply_injury(unreal.RVInjuryKind.CONCUSSION,unreal.RVBodyRegion.HEAD,1);health.debug_set_time_scale(10000)
def recovery():
 check('concussion_recovers_over_time',injuries()[0].healing>.1,injuries()[0].healing)
 check('head_status_tag_present',unreal.GameplayTagLibrary.get_num_gameplay_tags_in_container(health.get_status_tags())>0)
 health.debug_set_time_scale(1);health.debug_set_vitals(20,20)
 inv.server_drop(inv.get_items()[0].id,1)
def downed():
 check('downed_rejects_drop',len(inv.get_items())==1)
 check('downed_speed_zero',health.get_movement_scale()==0)
 check('downed_cannot_act',not health.can_act())
 health.debug_set_vitals(-500,500);check('vital_bounds',attr('Blood')==0 and attr('Vitality')==100)
 check('terminal_foundation',str(health.get_editor_property('LifeState')).find('TERMINAL')>=0)
 health.debug_clear_injuries()
def finish():
 check('reset_releases_treatment',not unreal.GuidLibrary.is_valid_guid(health.get_editor_property('ActiveTreatment')))
 unreal.unregister_slate_post_tick_callback(handle)
 (B/'medical-edges.json').write_text(json.dumps({'kind':'medical boundary diagnostics','results':results},indent=2))
events=[(1,bleeding),(4,depleted),(6,severity_rejected),(7,relief),(10,expired),(13,recovery),(15,downed),(16,finish)]
def tick(dt):
 try:
  if events and time.time()-start>=events[0][0]:_,fn=events.pop(0);fn()
 except Exception as e:check('harness_exception',False,repr(e));events.clear();finish()
handle=unreal.register_slate_post_tick_callback(tick)
