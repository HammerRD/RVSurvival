import unreal,json,gc
B='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate6Validation/'
rows=[];maps=[]
def check(name,ok,detail=''):rows.append({'case':name,'pass':bool(ok),'detail':str(detail)});unreal.log('GATE5_EDITOR '+json.dumps(rows[-1]))
def inspect(path):
 assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(path)
 actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
 world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
 counts={'actors':len(actors),'pickups':sum(isinstance(a,unreal.RVWorldItem) for a in actors),'storage':sum(isinstance(a,unreal.RVStoragePoint) for a in actors),'rest':sum(isinstance(a,unreal.RVRestPoint) for a in actors)}
 gm=world.get_world_settings().get_editor_property('DefaultGameMode')
 counts['gamemode']=gm.get_path_name() if gm else None
 if path.endswith('Gate4InventoryTest'):check('gate4_saved_fixture_intact',counts['actors']==61 and counts['pickups']==11 and counts['storage']==6 and counts['rest']==0,counts)
 if path.endswith('Gate5SurvivalTest'):check('gate5_saved_fixture_intact',counts['actors']==62 and counts['pickups']==11 and counts['storage']==5 and counts['rest']==2 and counts['gamemode'].endswith('BP_Gate5GameMode_C'),counts)
 check('load_'+path,True);return {'path':path,'counts':counts}
def inspect_assets():
 for path in ['/Game/Items/DA_Food','/Game/Items/DA_Water','/Game/Survival/DA_NormalNeeds','/Game/Survival/BP_SurvivalPlayerState','/Game/Survival/BP_Gate5GameMode']:
  asset=unreal.load_asset(path);check('asset_'+path,asset is not None)
 for name,n,h in [('Food',25,0),('Water',0,35)]:
  m=unreal.load_asset('/Game/Items/DA_'+name).get_editor_property('Consumable');check('saved_consumable_'+name,m.get_editor_property('bConsumable') and m.nutrition==n and m.hydration==h)
 cls=unreal.EditorAssetLibrary.load_blueprint_class('/Game/Survival/BP_SurvivalPlayerState');profile=unreal.get_default_object(cls).get_editor_property('Needs').get_editor_property('TuningAsset');check('saved_tuning_reference',profile is not None and profile.get_name()=='DA_NormalNeeds')
for repeat in range(2):
 for path in ['/Game/Maps/Gate1Test','/Game/Maps/Gate2VehicleTest','/Game/Maps/Gate3MovingInteriorTest','/Game/Maps/Gate4InventoryTest','/Game/Maps/Gate5SurvivalTest','/Game/Maps/Gate6FuelElectricalTest']:
  # Every previous inspection returned primitives; no World/Actor wrappers cross LoadLevel.
  gc.collect();unreal.SystemLibrary.collect_garbage();maps.append(inspect(path))
inspect_assets()
def inspect_refinement():
 cls=unreal.EditorAssetLibrary.load_blueprint_class('/Game/Vehicles/Gate5Refinement/BP_ClassCRefinedMotorhome')
 c=unreal.get_default_object(cls);arm=c.get_component_by_class(unreal.SpringArmComponent);camera=c.get_component_by_class(unreal.CameraComponent)
 check('refined_camera_saved',arm.get_editor_property('TargetArmLength')==1400 and arm.get_editor_property('RelativeLocation').z==340 and arm.get_editor_property('ProbeSize')==16 and arm.get_editor_property('bDoCollisionTest') and camera.get_editor_property('FieldOfView')==85)
 boxes={str(x.name):x for x in c.get_editor_property('InteriorCollision')}
 check('only_external_tread_has_prototype_visual',all(x.get_editor_property('bVisiblePrototype')==(name=='EntryStepLow') for name,x in boxes.items()))
 check('saved_actual_entry_stepwell',boxes['EntryStepMid'].center.x==92.4 and boxes['EntryStepHigh'].center.x==92.4 and 'EntryFloorRear' in boxes and 'EntryFloorFront' in boxes)
 check('saved_door_and_shell_collision',all(n in boxes for n in ['OpenHouseDoor','FrontFascia','HoodTop','CabExteriorLeft','CabExteriorRight']))
 check('standing_and_interior_seat_entry_enabled',c.get_editor_property('bEnableStandingDoor') and c.get_editor_property('bInteriorSeatAccess'))
 defs=c.get_editor_property('ExteriorCompartments');parts={str(x.name):x for x in c.get_editor_property('VisualParts')}
 check('seven_saved_real_door_containers',len(defs)==7 and len({str(x.door_part_name) for x in defs})==7 and all(str(x.door_part_name) in parts and 'SM_RV_Van_Compartment' in parts[str(x.door_part_name)].mesh.get_name() for x in defs))
 check('saved_capacities_configurable',all(x.max_weight_kg>0 and x.max_volume_litres>0 for x in defs))
inspect_refinement();gc.collect();unreal.SystemLibrary.collect_garbage()

def inspect_gate6():
 cls=unreal.EditorAssetLibrary.load_blueprint_class('/Game/Vehicles/Gate6/BP_ClassCSystemsMotorhome')
 c=unreal.get_default_object(cls)
 check('gate6_saved_class',isinstance(c,unreal.RVSystemsMotorhome))
 check('gate6_tank_and_separate_source',c.get_editor_property('PropulsionFuel').get_editor_property('CapacityLitres')==200 and c.get_editor_property('PropulsionFuel').get_editor_property('InitialLitres')==150 and c.get_editor_property('GeneratorFuel').get_editor_property('CapacityLitres')==30)
 check('distinct_battery_capacity',c.get_editor_property('HouseBattery').get_editor_property('CapacityWh')==2400 and c.get_editor_property('ChassisBattery').get_editor_property('CapacityWh')==800)
 check('normal_profile_saved',c.get_editor_property('Electrical').get_editor_property('Profile').get_name()=='DA_NormalRVEnergy')
 check('new_light_mobility_and_no_shadow',str(c.get_editor_property('FrontLight').get_editor_property('Mobility'))=='ComponentMobility.MOVABLE' and not c.get_editor_property('FrontLight').get_editor_property('CastShadows'),str(c.get_editor_property('FrontLight').get_editor_property('Mobility')))
 defs=list(c.get_editor_property('Stations'))
 check('optional_power_load_binding_saved',str(next(d for d in defs if str(d.name)=='Navigation').get_editor_property('RequiredPowerLoad'))=='PoweredStation' and all(str(d.get_editor_property('RequiredPowerLoad'))=='None' for d in defs if str(d.name)!='Navigation'))
 parts=list(c.get_editor_property('VisualParts'))
 check('purchased_54_parts_preserved',len(parts)==54,len(parts))
 boxes={str(x.name):x for x in c.get_editor_property('InteriorCollision')}
 check('gate6_front_shell_and_entry_preserved',all(n in boxes for n in ['FrontFascia','HoodTop','CabExteriorLeft','CabExteriorRight','FrontWall','EntryFloorFront','EntryFloorRear','EntryStepLow']))
 arm=c.get_component_by_class(unreal.SpringArmComponent)
 check('gate6_camera_preserved',arm.get_editor_property('TargetArmLength')==1400 and arm.get_editor_property('ProbeSize')==16 and c.get_component_by_class(unreal.CameraComponent).get_editor_property('FieldOfView')==85)
 check('gate6_seven_exterior_compartments',len(c.get_editor_property('ExteriorCompartments'))==7)
 for suffix,capacity,amount in [('Full',20,20),('Partial',10,3.75),('Empty',20,0),('Diesel',20,20)]:
  a=unreal.load_asset('/Game/Resources/DA_FuelCan'+suffix);f=a.get_editor_property('Fuel')
  check('saved_fuel_metadata_'+suffix,f.get_editor_property('bFuelContainer') and f.capacity_litres==capacity and f.initial_litres==amount and not a.get_editor_property('bStackable'))
 original=unreal.load_asset('/Game/Items/DA_FuelCan')
 check('accepted_gate4_fuel_definition_stays_inert',not original.get_editor_property('Fuel').get_editor_property('bFuelContainer'))
 return {'part_names':[str(p.name) for p in parts],'fuel_named_parts':[str(p.name) for p in parts if any(n in str(p.name).lower() for n in ['fuel','gas','petrol'])]}
gate6=inspect_gate6()
gc.collect();unreal.SystemLibrary.collect_garbage()
settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.LevelEditorPlaySettings'))
settings.set_editor_property('PlayNumberOfClients',1);settings.set_editor_property('RunUnderOneProcess',True);settings.set_editor_property('AdditionalLaunchParameters','')
network=settings.get_editor_property('NetworkEmulationSettings');network.set_editor_property('bIsNetworkEmulationEnabled',False);settings.set_editor_property('NetworkEmulationSettings',network)
unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings')).set_editor_property('bThrottleCPUWhenNotForeground',True)

check('save_all_completed',unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True))
json.dump({'results':rows,'maps':maps,'gate6':gate6},open(B+'editor-final.json','w'),indent=2)
unreal.SystemLibrary.quit_editor()
