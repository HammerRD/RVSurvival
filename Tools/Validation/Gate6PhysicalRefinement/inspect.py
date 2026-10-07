"""Read-only saved layout inspection; no UObject survives the function scope."""
import unreal, json
from pathlib import Path
BASE=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate6PhysicalRefinement')
BASE.mkdir(parents=True,exist_ok=True)
def inspect():
    levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    assert levels.load_level('/Game/Maps/Gate6FuelElectricalTest')
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    rv=next(a for a in actors if isinstance(a,unreal.RVSystemsMotorhome))
    def vec(v):return [v.x,v.y,v.z]
    parts=[]
    for d in rv.get_editor_property('VisualParts'):
        mesh=d.mesh
        points=unreal.RVInteriorMotorhome.inspect_art_surfaces(mesh)
        parts.append({'name':str(d.name),'transform':str(d.transform),'bounds':str(mesh.get_bounds()),'horizontal':[vec(v) for v in points if v.z>280]})
    return {'collision':[{'name':str(d.name),'center':vec(d.center),'extent':vec(d.extent),'floor':d.get_editor_property('bPassengerFloor'),'visible':d.get_editor_property('bVisiblePrototype')} for d in rv.get_editor_property('InteriorCollision')],
            'floor':{'center':str(rv.get_editor_property('InteriorFloor').get_editor_property('RelativeLocation')),'extent':str(rv.get_editor_property('InteriorFloor').get_unscaled_box_extent())},
            'parts':parts,'rest':[{'name':str(a.get_editor_property('DisplayName')),'location':vec(rv.get_actor_transform().inverse_transform_location(a.get_actor_location()))} for a in actors if isinstance(a,unreal.RVRestPoint)],
            'entry':str(rv.get_editor_property('StandingEntryLocation'))}
(BASE/'saved-layout-before.json').write_text(json.dumps(inspect(),indent=2),encoding='utf-8')
unreal.SystemLibrary.quit_editor()
