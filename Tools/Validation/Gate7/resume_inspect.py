"""Read saved Gate7 state without retaining world references across shutdown."""
import unreal,json
from pathlib import Path
ROOT=Path('D:/GitHub/RVSurvival/RVSurvival')
def inspect():
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    rv=next(a for a in actors if isinstance(a,unreal.RVMechanicalMotorhome))
    def v(x):return [x.x,x.y,x.z]
    return {'physical_entry':rv.get_editor_property('bPhysicalDoorEntry'),
        'collision':[{'name':str(x.name),'center':v(x.center),'extent':v(x.extent)} for x in rv.get_editor_property('InteriorCollision')],
        'parts':[{'name':str(x.name),'mesh':x.mesh.get_path_name(),'transform':str(x.transform),'bounds':str(x.mesh.get_bounds())} for x in rv.get_editor_property('VisualParts')],
        'rests':[str(a.get_editor_property('DisplayName')) for a in actors if isinstance(a,unreal.RVRestPoint)],
        'ladders':[{'roof':a.get_editor_property('bRoofAccess'),'height':a.get_editor_property('ClimbHeight')} for a in actors if isinstance(a,unreal.RVLadder)],
        'actor_count':len(actors)}
try:
    folder=ROOT/'Saved/Gate7Resume';folder.mkdir(parents=True,exist_ok=True)
    (folder/'before.json').write_text(json.dumps(inspect(),indent=2),encoding='utf-8')
finally:unreal.SystemLibrary.quit_editor()
