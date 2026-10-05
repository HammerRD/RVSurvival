import unreal,json
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
v=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.load_class(None,'/Script/RVSurvival.RVMotorhome'))[0]
m=v.get_component_by_class(unreal.load_class(None,'/Script/RVSurvival.RVVehicleMovementComponent'))
mesh=v.get_component_by_class(unreal.SkeletalMeshComponent)
def prop(obj,name):
    try:return str(obj.get_editor_property(name))
    except:return 'unavailable'
rows={'map':w.get_path_name(),'game_mode':prop(w.get_world_settings(),'default_game_mode'),'mesh':prop(mesh,'skeletal_mesh_asset'),'animation':prop(mesh,'anim_class'),'mass_kg':prop(m,'Mass'),'center_of_mass_override':prop(m,'CenterOfMassOverride'),'entry_exit_speed_cm_s':prop(v,'MaxEntryExitSpeed'),'physics_settings':{n:prop(unreal.get_default_object(unreal.load_class(None,'/Script/Engine.PhysicsSettings')),n) for n in ['bEnablePhysicsPrediction','bTickPhysicsAsync','DefaultGravityZ']},'wheels':[],'seats':[],'starts':[]}
for s in m.get_editor_property('WheelSetups'):
    wc=s.get_editor_property('wheel_class');cdo=unreal.get_default_object(wc)
    rows['wheels'].append({'bone':prop(s,'bone_name'),'class':str(wc),'settings':{n:prop(cdo,n) for n in ['WheelRadius','WheelWidth','SpringRate','SuspensionDampingRatio','SuspensionMaxRaise','SuspensionMaxDrop','MaxSteerAngle','bAffectedByEngine','bAffectedBySteering','bAffectedByHandbrake']}})
for s in v.get_seats():rows['seats'].append({n:prop(s,n) for n in ['bDriverSeat','EntryOffset','ExitOffset','SeatLabel']})
for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.PlayerStart):rows['starts'].append(str(a.get_actor_location()))
for n in ['EngineSetup','DifferentialSetup','TransmissionSetup']:rows[n]=prop(m,n)
json.dump(rows,open('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate2Validation/fixture.json','w'),indent=2)
unreal.log('GATE2_FIXTURE '+json.dumps(rows))
rows['physics_asset']=prop(mesh.get_editor_property('skeletal_mesh_asset'),'physics_asset')
for name,fields in {'EngineSetup':['MaxTorque','MaxRPM','EngineIdleRPM','EngineRevUpMOI','EngineRevDownRate'],'TransmissionSetup':['bUseAutomaticGears','bUseAutoReverse','GearChangeTime','FinalRatio','ForwardGearRatios','ReverseGearRatios'],'DifferentialSetup':['DifferentialType']}.items():
    setup=m.get_editor_property(name)
    rows[name]={n:prop(setup,n) for n in fields}
json.dump(rows,open('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate2Validation/fixture.json','w'),indent=2)

rows['physics_settings']['bEnablePhysicsPrediction']=prop(unreal.get_default_object(unreal.load_class(None,'/Script/Engine.PhysicsSettings')).get_editor_property('PhysicsPrediction'),'bEnablePhysicsPrediction')
json.dump(rows,open('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate2Validation/fixture.json','w'),indent=2)
