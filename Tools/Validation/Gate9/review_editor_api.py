import unreal,json
from pathlib import Path
out=Path('D:/GitHub/RVSurvival/RVSurvival/Docs/Gate9Results')
try:
 data={'merge_options':unreal.MergeStaticMeshActorsOptions.__doc__,'merge':unreal.StaticMeshEditorSubsystem.merge_static_mesh_actors.__doc__,'nav':unreal.NavMeshBoundsVolume.__doc__,'classes':[str(getattr(unreal,n,None)) for n in ['RVCombatComponent','RVInfected','RVInfectedProfile']]}
 (out/'editor-api-review.json').write_text(json.dumps(data,indent=2))
finally:unreal.SystemLibrary.quit_editor()
