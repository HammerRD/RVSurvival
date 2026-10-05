import unreal,json
B='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate3Validation/'
bp=unreal.load_asset('/Game/Vehicles/Gate3/BP_ClassCMotorhome');c=unreal.get_default_object(bp.generated_class());m=c.get_component_by_class(unreal.load_class(None,'/Script/RVSurvival.RVVehicleMovementComponent'))
def vec(v):return [v.x,v.y,v.z]
def props(o,names):return {n:str(o.get_editor_property(n)) for n in names}
d={'vehicle':props(m,['Mass','EngineSetup','TransmissionSetup','DifferentialSetup','WheelSetups','CenterOfMassOverride','bEnableCenterOfMassOverride']),'visuals':[], 'collision':[], 'stations':[], 'wheels':{}}
for v in c.get_editor_property('VisualParts'):d['visuals'].append({'name':str(v.get_editor_property('Name')),'mesh':v.get_editor_property('Mesh').get_path_name(),'transform':str(v.get_editor_property('Transform')),'materials':[a.get_path_name() for a in v.get_editor_property('Materials')],'disallow_nanite':v.get_editor_property('bDisallowNanite')})
for v in c.get_editor_property('InteriorCollision'):d['collision'].append({'name':str(v.get_editor_property('Name')),'center':vec(v.get_editor_property('Center')),'extent':vec(v.get_editor_property('Extent')),'floor':v.get_editor_property('bPassengerFloor')})
for v in c.get_editor_property('Stations'):d['stations'].append({'name':str(v.get_editor_property('Name')),'position':vec(v.get_editor_property('Position'))})
for k in ['Front','Rear']:
 w=unreal.get_default_object(unreal.load_asset('/Game/Vehicles/Gate3/BP_ClassCWheel'+k).generated_class());d['wheels'][k]=props(w,['WheelRadius','WheelWidth','SpringRate','SuspensionDampingRatio','SuspensionMaxRaise','SuspensionMaxDrop','MaxSteerAngle'])
d['vehicle']['engine']=props(m.get_editor_property('EngineSetup'),['MaxTorque','MaxRPM','EngineIdleRPM','EngineBrakeEffect','EngineRevUpMOI','EngineRevDownRate'])
d['vehicle']['transmission']=props(m.get_editor_property('TransmissionSetup'),['bUseAutomaticGears','bUseAutoReverse','FinalRatio','ForwardGearRatios','ReverseGearRatios','ChangeUpRPM','ChangeDownRPM','GearChangeTime','TransmissionEfficiency'])
d['vehicle']['differential']=props(m.get_editor_property('DifferentialSetup'),['DifferentialType','FrontRearSplit'])
json.dump(d,open(B+'final_configuration.json','w'),indent=2)
