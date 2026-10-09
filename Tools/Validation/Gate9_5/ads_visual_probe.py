"""Settled rendered sight/hand probe using normal Enhanced Input dispatch."""
from pathlib import Path
exec(Path('D:/GitHub/RVSurvival/RVSurvival/Tools/Validation/Gate9_5/stage_visual.py').read_text())
events=[(.5,'Four',True),(.6,'Four',False),(1.5,'R',True),(1.6,'R',False),(5,'RightMouseButton',True),(8,'RightMouseButton',False)]
done=set()
def probe(dt):
 elapsed=time.time()-started
 for i,(t,key,pressed) in enumerate(events):
  if elapsed>=t and i not in done:
   done.add(i);unreal.RVInteriorMotorhome.dispatch_development_key(pc,key,pressed)
 for t,name in [(4,'ik_ready'),(7,'ik_settled_ads'),(9,'ik_released')]:
  if elapsed>=t and name not in done:
   done.add(name);snap(name)
   bones=['hand_r','hand_l','index_01_r','index_03_r','middle_01_r','middle_03_r','thumb_01_r','thumb_03_r','index_01_l','index_03_l']
   report={bone:str(p.mesh.get_socket_transform(bone)) for bone in bones}
   report['actor']=str(p.get_actor_transform());report['aim_alpha']=p.mesh.get_anim_instance().get_editor_property('WeaponGripIKAlpha')
   (out/(name+'_bones.json')).write_text(json.dumps(report,indent=2))
 if elapsed>11:
  unreal.unregister_slate_post_tick_callback(probe_handle)
  (B/'visual-stop.json').write_text(json.dumps({'time':time.time()}))
probe_handle=unreal.register_slate_post_tick_callback(probe)
