import unreal,gc
p=unreal.load_asset('/Game/Characters/RV/DA_MannyPresentation');p.modify();p.set_editor_property('BedMeshRotation',unreal.Rotator(yaw=90));p.set_editor_property('BedOffset',unreal.Vector(-85,0,-15));p.set_editor_property('DownedOffset',unreal.Vector(85,0,22));assert unreal.EditorAssetLibrary.save_loaded_asset(p,False)
p=None;gc.collect();unreal.SystemLibrary.quit_editor()
