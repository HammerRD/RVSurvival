"""Rendered prototype tool-ready/swing check using the saved remapped key."""
from pathlib import Path
exec(Path('D:/GitHub/RVSurvival/RVSurvival/Tools/Validation/Gate9_5/stage_visual.py').read_text())
events=[(.5,'Five',True),(.6,'Five',False),(2,'N',True),(2.1,'N',False)]
done=set()
def probe(dt):
 elapsed=time.time()-started
 for i,(t,key,pressed) in enumerate(events):
  if elapsed>=t and i not in done:done.add(i);unreal.RVInteriorMotorhome.dispatch_development_key(pc,key,pressed)
 for t,name in [(1.5,'crowbar_ready'),(2.25,'crowbar_swing'),(3,'crowbar_return')]:
  if elapsed>=t and name not in done:done.add(name);snap(name)
 if elapsed>5:
  (out/'melee-render-state.json').write_text(json.dumps({'melee_sequence':combat.melee_sequence,'raised_armed_pose':p.mesh.get_anim_instance().get_editor_property('bWeaponReady'),'remapped_key':'N','normal_enhanced_input':True},indent=2))
  unreal.unregister_slate_post_tick_callback(probe_handle);(B/'visual-stop.json').write_text(json.dumps({'time':time.time()}))
probe_handle=unreal.register_slate_post_tick_callback(probe)
