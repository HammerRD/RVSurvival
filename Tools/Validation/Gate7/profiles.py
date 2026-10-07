"""Saved development profile has faster time, same healthy equilibrium/thresholds."""
import unreal,json
from pathlib import Path
B=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate7Validation');rows=[]
def check(n,ok,d=''):rows.append({'case':n,'pass':bool(ok),'detail':str(d)})
try:
 w=next(a for a in unreal.ObjectIterator(unreal.World) if a.get_name()=='Gate7MechanicalTest' and 'UEDPIE_' in a.get_path_name())
 v=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVMechanicalMotorhome)[0];c=v.get_editor_property('CoolingSystem');normal=c.get_editor_property('Tuning').copy();dev=unreal.load_asset('/Game/Development/Mechanical/DA_AcceleratedMechanical').get_editor_property('Tuning').copy()
 check('saved_normal_and_20x_development_distinct',normal.idle_heat_c_per_second==.25 and dev.idle_heat_c_per_second==5 and dev.load_heat_c_per_second==20 and dev.overheat_c==normal.overheat_c)
 c.debug_set_time_scale(0);c.set_editor_property('Tuning',dev);c.debug_set_state(.7,12,20,1);c.debug_advance(10,False,0,0);fast_litres=c.get_editor_property('Cooling').coolant_litres
 c.set_editor_property('Tuning',normal);c.debug_set_state(.7,12,20,1);c.debug_advance(200,False,0,0);check('20x_minor_leak_equivalence',abs(fast_litres-c.get_editor_property('Cooling').coolant_litres)<1e-8 and abs(fast_litres-11.8)<1e-8,fast_litres)
 c.set_editor_property('Tuning',dev);c.debug_set_state(1,12,20,1);c.debug_advance(180,True,1,2682.24);fast_c=c.get_editor_property('Cooling').temperature_c
 c.set_editor_property('Tuning',normal);c.debug_set_state(1,12,20,1);c.debug_advance(3600,True,1,2682.24);normal_c=c.get_editor_property('Cooling').temperature_c
 check('20x_thermal_same_healthy_equilibrium',abs(fast_c-normal_c)<1e-6 and fast_c<115,{'development_c':fast_c,'normal_c':normal_c})
 check('normal_default_profile_still_selected',c.get_editor_property('Profile').get_name()=='DA_NormalMechanical' and c.get_editor_property('Tuning').load_heat_c_per_second==1)
 c.debug_set_state(1,12,20,1)
except Exception as e:check('profile_exception',False,repr(e))
(B/'profiles.json').write_text(json.dumps({'results':rows},indent=2),encoding='utf-8')
