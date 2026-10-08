"""Direct component diagnostic only; normal player UI controls are a later acceptance pass."""
import unreal, json, time
from pathlib import Path
B=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate8Validation')
w=next(a for a in unreal.ObjectIterator(unreal.World) if a.get_name()=='Gate7MechanicalTest' and 'UEDPIE_' in a.get_path_name())
pc=unreal.GameplayStatics.get_player_controller(w,0)
p=pc.get_controlled_pawn(); ps=pc.player_state; health=ps.get_editor_property('Health')
inventory=p.get_component_by_class(unreal.RVInventoryComponent)
results=[];start=time.time();events=[];before=None;injury=None;supply=None
def check(name,value,detail=''):
 results.append({'case':name,'pass':bool(value),'detail':str(detail)})
 unreal.log('GATE8 '+name+' '+str(bool(value)))
def injuries():return health.get_editor_property('Injuries')
def blood():return ps.get_editor_property('MedicalAttributes').get_editor_property('Blood').get_editor_property('CurrentValue')
def seed():
 global injury,supply,before
 check('persistent_ASC_present',bool(ps.get_editor_property('MedicalAbilitySystem')))
 check('initial_active',health.can_act())
 check('initial_blood',abs(blood()-100)<.01)
 check('wound_debug',health.debug_apply_injury(unreal.RVInjuryKind.WOUND,unreal.RVBodyRegion.RIGHT_LEG,2))
 injury=injuries()[0].get_editor_property('Id')
 check('identified_wound',unreal.GuidLibrary.is_valid_guid(injury))
 check('moderate_bleed',abs(injuries()[0].get_editor_property('BleedingPerMinute')-3)<.01)
 health.debug_set_time_scale(60);before=blood()
def drain():
 check('blood_loss',blood()<before-3,(before,blood()))
 health.debug_set_time_scale(1)
 # Runtime-only definition fixture, never modifies accepted DA_Bandage/vendor content.
 definition=unreal.load_asset('/Game/Development/Medical/DA_DiagnosticBandage')
 record=unreal.RVItemInstance();record.set_editor_property('Id',unreal.GuidLibrary.new_guid())
 record.set_editor_property('Definition',definition);record.set_editor_property('Quantity',2)
 admission=inventory.add_authority(record)
 check('existing_inventory_admission',len(inventory.get_items())==1 and inventory.get_items()[0].quantity==2,admission)
 global supply
 supply=inventory.get_items()[0].get_editor_property('Id')
 health.request_treatment(ps,injury,supply,0)
def complete():
 check('bandage_completed',injuries()[0].get_editor_property('BleedingPerMinute')==0,health.get_editor_property('Feedback'))
 check('consumed_once',sum(i.quantity for i in inventory.get_items())==1)
 check('injury_retained',len(injuries())==1 and injuries()[0].get_editor_property('Healing')<1)
 health.request_treatment(ps,injury,supply,0)
def stale():
 check('stale_revision_rejected',sum(i.quantity for i in inventory.get_items())==1)
 check('fracture_apply',health.debug_apply_injury(unreal.RVInjuryKind.FRACTURE,unreal.RVBodyRegion.LEFT_LEG,2))
 check('leg_consequence',abs(health.get_movement_scale()-.35)<.01)
 check('pain_present',health.get_pain()>0)
 check('burn_apply',health.debug_apply_injury(unreal.RVInjuryKind.BURN,unreal.RVBodyRegion.LEFT_ARM,1))
 check('concussion_apply',health.debug_apply_injury(unreal.RVInjuryKind.CONCUSSION,unreal.RVBodyRegion.HEAD,1))
 check('vitals_clamp',health.debug_set_vitals(500,-5))
 check('downed_state',not health.can_act())
 check('debug_clear',health.debug_clear_injuries())
 check('reset_active',health.can_act() and len(injuries())==0)
def finish():
 unreal.unregister_slate_post_tick_callback(h)
 (B/'foundation-single.json').write_text(json.dumps({'kind':'component diagnostic; no manual-control acceptance','results':results},indent=2),encoding='utf-8')
events=[(1,seed),(4,drain),(7,complete),(9,stale),(10,finish)]
def tick(dt):
 try:
  if events and time.time()-start>=events[0][0]:
   _,fn=events.pop(0);fn()
 except Exception as e:
  check('harness_exception',False,repr(e));finish()
h=unreal.register_slate_post_tick_callback(tick)
