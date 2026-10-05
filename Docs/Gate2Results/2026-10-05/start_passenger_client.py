import unreal
def ready(dt):
    worlds=[w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='Gate2VehicleTest' and unreal.GameplayStatics.get_player_controller(w,0) and unreal.GameplayStatics.get_player_controller(w,0).get_controlled_pawn()]
    if not worlds:return
    unreal.unregister_slate_post_tick_callback(h)
    exec(open('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate2Validation/passenger_disconnect.py').read(),{'__name__':'__main__'})
h=unreal.register_slate_post_tick_callback(ready)

