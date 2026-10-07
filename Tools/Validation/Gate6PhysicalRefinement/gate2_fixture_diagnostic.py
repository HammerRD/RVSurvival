"""Preserve the historical test and inspect its blocked-exit prerequisites."""
from pathlib import Path
source=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate2Validation/multi.py').read_text(encoding='utf-8-sig')
probe='''
def inspect_block_prerequisites():
    check('blocked_exit_prerequisite_host_reentered_driver',host.get_controlled_pawn()==sv and sv.get_controller()==host and host.get_editor_property('SeatedVehicle')==sv and seats(sv)['DriverSeat']==hp,sample())
    check('blocked_exit_prerequisite_six_blockers',len(blockers)==6,len(blockers))
    unreal.log('EXIT_FIXTURE ' + json.dumps({'host_location':str(hp.get_actor_location()),'host_collision':str(hp.get_component_by_class(unreal.CapsuleComponent).get_collision_enabled()),'driver_exit':str(next(s for s in sv.get_seats() if s.get_editor_property('bDriverSeat')).get_editor_property('ExitOffset')),'blocks':[{'name':a.get_actor_label(),'location':str(a.get_actor_location()),'bounds':str(a.get_actor_bounds(False)),'collision':str(a.get_component_by_class(unreal.StaticMeshComponent).get_collision_enabled())} for a in blockers]}))
at(55.5,inspect_block_prerequisites)
def inspect_held_reentry():
    unreal.log('EXIT_REENTRY_FOCUS '+json.dumps({'prompt':str(hp.get_component_by_class(unreal.RVInteractionComponent).get_prompt()),'character':str(hp.get_actor_location()),'vehicle_rotation':str(sv.get_actor_rotation()),'controlled_pawn':str(host.get_controlled_pawn())}))
at(54.3,inspect_held_reentry)
def inspect_block_coverage():
    seat=next(s for s in sv.get_seats() if s.get_editor_property('bDriverSeat'))
    preferred=seat.get_editor_property('ExitOffset')
    offsets=[preferred,preferred+unreal.Vector(-100,0,0),preferred+unreal.Vector(100,0,0),unreal.Vector(-450,0,0),unreal.Vector(0,-350,0),unreal.Vector(0,350,0)]
    coverage=[]
    for off in offsets:
        point=sv.get_actor_transform().transform_location(off)
        covering=[]
        for actor in blockers:
            centre,extent=actor.get_actor_bounds(False)
            if abs(point.x-centre.x)<=extent.x and abs(point.y-centre.y)<=extent.y:covering.append(actor.get_actor_label())
        coverage.append({'candidate':str(off),'covering':covering})
    check('blocked_exit_fixture_covers_all_six_candidate_rays',all(c['covering'] for c in coverage),coverage)
    check('blocked_exit_fixture_still_seated_before_E',host.get_controlled_pawn()==sv and sv.get_controller()==host and host.get_editor_property('SeatedVehicle')==sv and seats(sv)['DriverSeat']==hp,sample())
    components=[a.get_component_by_class(unreal.StaticMeshComponent) for a in blockers]
    check('blocked_exit_fixture_collision_blocks_pawn_and_visibility',all(c.get_collision_enabled()==unreal.CollisionEnabled.QUERY_AND_PHYSICS and c.get_collision_response_to_channel(unreal.CollisionChannel.ECC_PAWN)==unreal.CollisionResponseType.ECR_BLOCK and c.get_collision_response_to_channel(unreal.CollisionChannel.ECC_VISIBILITY)==unreal.CollisionResponseType.ECR_BLOCK for c in components),len(components))
at(56.5,inspect_block_coverage)
def inspect_clear_restoration():
    movement=hp.get_component_by_class(unreal.CharacterMovementComponent)
    check('clear_exit_restores_active_walking_collision',host.get_controlled_pawn()==hp and hp.get_editor_property('SeatedVehicle') is None and movement.is_active() and movement.is_component_tick_enabled() and movement.get_editor_property('MovementMode')==unreal.MovementMode.MOVE_WALKING and hp.get_component_by_class(unreal.CapsuleComponent).get_collision_enabled()==unreal.CollisionEnabled.QUERY_AND_PHYSICS,hp.get_actor_location())
at(61.2,inspect_clear_restoration)
'''
source=source.replace('events.sort(key=lambda e:e[0]);',probe+'\nevents.sort(key=lambda e:e[0]);')
exec(compile(source,'historical-gate2-fixture-with-prerequisite-evidence','exec'))
