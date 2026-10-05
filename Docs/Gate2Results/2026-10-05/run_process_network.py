import unreal
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.LevelEditorPlaySettings'))
n=settings.get_editor_property('NetworkEmulationSettings');n.set_editor_property('bIsNetworkEmulationEnabled',True)
o=n.get_editor_property('OutPackets');o.set_editor_property('MinLatency',100);o.set_editor_property('MaxLatency',100);o.set_editor_property('PacketLossPercentage',2)
n.set_editor_property('OutPackets',o);settings.set_editor_property('NetworkEmulationSettings',n)
unreal.log('GATE2_NETWORK_SETTINGS enabled=%s min=%s max=%s loss=%s' % (n.get_editor_property('bIsNetworkEmulationEnabled'),o.get_editor_property('MinLatency'),o.get_editor_property('MaxLatency'),o.get_editor_property('PacketLossPercentage')))
exec(open('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate2Validation/run_process.py').read(),{'__name__':'__main__'})
