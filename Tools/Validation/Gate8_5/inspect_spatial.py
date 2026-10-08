import unreal,json,gc
from pathlib import Path
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors();rv=next(a for a in actors if isinstance(a,unreal.RVSystemsMotorhome));bed=next(a for a in actors if isinstance(a,unreal.RVRestPoint))
r={'bed_rotation':str(bed.get_actor_rotation()),'bed_location':str(rv.get_actor_transform().inverse_transform_location(bed.get_actor_location())),'lying_rotation':str(bed.get_editor_property('LyingRotation')),'lying_offset':str(bed.get_editor_property('LyingOffset')),'seats':[{'name':s.get_name(),'position':str(rv.get_actor_transform().inverse_transform_location(s.get_world_location()))} for s in rv.get_seats()]}
Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate8_5Validation/spatial.json').write_text(json.dumps(r,indent=2));actors=None;w=None;rv=None;bed=None;gc.collect();unreal.SystemLibrary.quit_editor()
