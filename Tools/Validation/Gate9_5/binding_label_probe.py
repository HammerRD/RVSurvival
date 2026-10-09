"""Cross-check native profile values and the exact player-help label accessor."""
import unreal,json,time
from pathlib import Path
out=Path('D:/GitHub/RVSurvival/RVSurvival/Docs/Gate9_5Results');started=time.time()
w=next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='Gate9_5CombatRefinementTest' and unreal.GameplayStatics.get_player_controller(w,0) and unreal.GameplayStatics.get_player_controller(w,0).get_controlled_pawn())
pc=unreal.GameplayStatics.get_player_controller(w,0);settings=next(s.get_user_settings() for s in unreal.ObjectIterator(unreal.EnhancedInputLocalPlayerSubsystem) if s.get_user_settings())
report={'before':pc.get_control_binding_label('Fire')}
args=unreal.MapPlayerKeyArgs();key=unreal.Key();key.set_editor_property('KeyName','Q');args.set_editor_property('MappingName','Fire');args.set_editor_property('NewKey',key);args.set_editor_property('Slot',unreal.PlayerMappableKeySlot.FIRST)
settings.map_player_key(args);settings.apply_settings();report['immediate']=pc.get_control_binding_label('Fire')
def tick(dt):
 global w,pc,settings
 if time.time()-started>1:
  report['settled']=pc.get_control_binding_label('Fire');report['pass']=report['immediate']=='Q' and report['settled']=='Q'
  settings.get_active_key_profile().reset_mapping_to_default('Fire');settings.apply_settings()
  report['reset']=pc.get_control_binding_label('Fire')
  (out/'binding-label-probe.json').write_text(json.dumps(report,indent=2));unreal.unregister_slate_post_tick_callback(handle);w=pc=settings=None
handle=unreal.register_slate_post_tick_callback(tick)
