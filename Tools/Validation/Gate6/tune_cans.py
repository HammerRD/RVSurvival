import unreal
a=unreal.load_asset('/Game/Resources/DA_FuelCanPartial')
a.set_editor_property('WeightKg',6);a.set_editor_property('VolumeLitres',12)
assert unreal.EditorAssetLibrary.save_loaded_asset(a,False)
unreal.log('GATE6_CANS_SAVED')
unreal.SystemLibrary.quit_editor()
