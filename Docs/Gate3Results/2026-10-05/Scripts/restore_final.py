import unreal,json
B='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate3Validation/'
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert level.load_level('/Game/Maps/Gate3MovingInteriorTest')
s=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.LevelEditorPlaySettings'));s.set_editor_property('RunUnderOneProcess',True);s.set_editor_property('PlayNumberOfClients',2);s.set_editor_property('AdditionalLaunchParameters','')
n=s.get_editor_property('NetworkEmulationSettings');n.set_editor_property('bIsNetworkEmulationEnabled',False);s.set_editor_property('NetworkEmulationSettings',n)
unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings')).set_editor_property('bThrottleCPUWhenNotForeground',True)
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();unreal.SystemLibrary.execute_console_command(w,'t.MaxFPS 0');unreal.SystemLibrary.execute_console_command(w,'rv.Passenger.Debug 0')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);c=unreal.load_asset('/Game/Vehicles/Gate3/BP_ClassCMotorhome').generated_class();rv=next(a for a in actors.get_all_level_actors() if a.get_class()==c)
cam=unreal.Vector(-1100,-900,650);look=unreal.MathLibrary.find_look_at_rotation(cam,rv.get_actor_location()+unreal.Vector(0,0,150));unreal.EditorLevelLibrary.set_level_viewport_camera_info(cam,look)
json.dump({'map':w.get_path_name(),'players':s.get_editor_property('PlayNumberOfClients'),'one_process':s.get_editor_property('RunUnderOneProcess'),'network_emulation':n.get_editor_property('bIsNetworkEmulationEnabled'),'additional_parameters':s.get_editor_property('AdditionalLaunchParameters'),'vendor_parts':len(rv.get_editor_property('VisualParts')),'stations':len(rv.get_editor_property('Stations'))},open(B+'final_editor_state.json','w'),indent=2)
unreal.log('GATE3_EDITOR_RESTORED')
