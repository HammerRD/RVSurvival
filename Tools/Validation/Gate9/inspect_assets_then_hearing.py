import unreal,json,traceback
from pathlib import Path
def inspect_assets():
 ao=unreal.load_asset('/Game/Characters/Mannequins/Anims/Pistol/Aim/AO_Pistol')
 report={'axes':[{k:str(a.get_editor_property(k)) for k in ['DisplayName','Min','Max']} for a in ao.get_editor_property('BlendParameters')],'samples':[]}
 for a in ao.get_editor_property('SampleData'):
  clip=a.get_editor_property('Animation');report['samples'].append({'position':str(a.get_editor_property('SampleValue')),'clip':clip.get_path_name(),'additive':str(clip.get_editor_property('AdditiveAnimType')),'base_type':str(clip.get_editor_property('RefPoseType')),'base':str(clip.get_editor_property('RefPoseSeq'))})
 Path('D:/GitHub/RVSurvival/RVSurvival/Docs/Gate9Results/aim-asset-inspection.json').write_text(json.dumps(report,indent=2))
try:inspect_assets()
except Exception:unreal.log_error(traceback.format_exc())
exec(compile(open('D:/GitHub/RVSurvival/RVSurvival/Tools/Validation/Gate9/launch_hearing.py').read(),'launch_hearing.py','exec'))
