"""Actual UMG visibility and screenshot; real held interaction before inspection."""
import unreal,time,json
from pathlib import Path
B=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate7Validation')
w=next(a for a in unreal.ObjectIterator(unreal.World) if a.get_name()=='Gate7MechanicalTest' and 'UEDPIE_' in a.get_path_name())
pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn()
v=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVMechanicalMotorhome)[0];point=v.get_editor_property('EngineService')
start=time.time();phase=0;rows=[]
def check(n,ok,d=''):rows.append({'case':n,'pass':bool(ok),'detail':str(d)})
def key(k,on):unreal.RVInteriorMotorhome.dispatch_development_key(pc,k,on)
def tick(dt):
 global phase
 t=time.time()-start
 if phase==0:
  p.set_actor_location(v.get_actor_transform().transform_location(unreal.Vector(550,-75,100)),False,True)
  v.get_editor_property('CoolingSystem').debug_set_time_scale(0);v.get_editor_property('CoolingSystem').debug_set_state(.2,9,20,1);phase=1
 elif phase==1 and t>1:
  pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p.get_actor_location()+unreal.Vector(0,0,p.get_editor_property('BaseEyeHeight')),point.get_actor_location()));phase=2
 elif phase==2 and t>2:key('E',True);phase=3
 elif phase==3 and t>2.9:key('E',False);phase=4
 elif phase==4 and t>4:
  check('native_E_service_open',pc.get_editor_property('MechanicalPoint')==point)
  widgets=unreal.WidgetLibrary.get_all_widgets_of_class(w,unreal.RVMechanicalWidget,False)
  check('mechanical_UMG_visible',any(x.is_visible() for x in widgets),len(widgets))
  survival=unreal.WidgetLibrary.get_all_widgets_of_class(w,unreal.RVSurvivalWidget,False)
  check('survival_UMG_preserved',any(x.is_visible() for x in survival),len(survival))
  unreal.SystemLibrary.execute_console_command(pc,'shot showui filename='+str(B/'resume-ui.png')+' -nosuffix',pc);phase=5
 elif phase==5 and t>6:
  unreal.unregister_slate_post_tick_callback(h)
  (B/'ui-probe.json').write_text(json.dumps({'results':rows},indent=2),encoding='utf-8')
h=unreal.register_slate_post_tick_callback(tick)
