import unreal,json
B='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate3Validation/'
config=json.load(open(B+'case.json'))
s=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.LevelEditorPlaySettings'))
s.set_editor_property('PlayNumberOfClients',2)
# UE 5.8 does not expose EPlayNetMode to Python; current UI configuration is Listen Server.
n=s.get_editor_property('NetworkEmulationSettings')
n.set_editor_property('bIsNetworkEmulationEnabled',bool(config.get('network')))
o=n.get_editor_property('OutPackets')
o.set_editor_property('MinLatency',100);o.set_editor_property('MaxLatency',100);o.set_editor_property('PacketLossPercentage',2)
n.set_editor_property('OutPackets',o);s.set_editor_property('NetworkEmulationSettings',n)
unreal.log('GATE3_PLAY_SETTINGS '+str(n))



