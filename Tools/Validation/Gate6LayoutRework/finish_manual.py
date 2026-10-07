"""Release manual input/callbacks before Stop PIE. Does not reload a world."""
import sys, unreal

def finish():
    released = 0
    # Console exec globals own the baseline callback; module runners own controls.
    if globals().get('h'):
        unreal.unregister_slate_post_tick_callback(globals()['h'])
        globals()['h'] = None
        released += 1
    for name, module in list(sys.modules.items()):
        if not name.startswith('rv_validation_'):
            continue
        state = module.__dict__
        if state.get('held'):
            for world in unreal.ObjectIterator(unreal.World):
                if 'UEDPIE_' in world.get_path_name() and world.get_name() == 'Gate6FuelElectricalTest':
                    pc = unreal.GameplayStatics.get_player_controller(world, 0)
                    unreal.RVInteriorMotorhome.dispatch_development_key(pc, state['held'][0], False)
            state['held'] = None
        assert not state.get('observer_name'), 'Restore observer before final cleanup'
        if state.get('h'):
            unreal.unregister_slate_post_tick_callback(state['h'])
            state['h'] = None
            released += 1
    # All scoped world/controller references return before runner globals clear.
    unreal.log('FINAL_MANUAL_CALLBACKS_RELEASED ' + str(released))

finish()
from runner_runtime import release_runners
release_runners()
