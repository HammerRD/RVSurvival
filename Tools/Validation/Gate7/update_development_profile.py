"""Save the separate 20x thermal profile without loading/reconfiguring a world."""
import unreal,json
from pathlib import Path
B=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate7Validation')
rows=[]
def check(n,ok):rows.append({'case':n,'pass':bool(ok)})
def update():
 normal=unreal.load_asset('/Game/Mechanical/DA_NormalMechanical');dev=unreal.load_asset('/Game/Development/Mechanical/DA_AcceleratedMechanical')
 tuning=normal.get_editor_property('Tuning').copy();original=tuning.idle_heat_c_per_second
 for field in ['IdleHeatCPerSecond','LoadHeatCPerSecond','PassiveCoolingPerSecond','RadiatorCoolingPerSecond','MinorLeakLitresPerSecond','MajorLeakLitresPerSecond','EngineDamagePerSecond']:
  tuning.set_editor_property(field,tuning.get_editor_property(field)*20)
 dev.set_editor_property('Tuning',tuning)
 check('normal_tuning_unchanged',normal.get_editor_property('Tuning').idle_heat_c_per_second==original)
 check('development_20x_thermal_same_thresholds',dev.get_editor_property('Tuning').load_heat_c_per_second==20 and dev.get_editor_property('Tuning').overheat_c==normal.get_editor_property('Tuning').overheat_c)
 check('saved_development_only_asset',unreal.EditorAssetLibrary.save_loaded_asset(dev,False))
try:
 check('save_before',unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True));update();check('save_after',unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True))
except Exception as e:rows.append({'case':'exception','pass':False,'detail':repr(e)})
(B/'development-profile.json').write_text(json.dumps({'results':rows},indent=2),encoding='utf-8');unreal.SystemLibrary.quit_editor()
