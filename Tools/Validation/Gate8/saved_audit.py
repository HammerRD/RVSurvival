"""Saved packages reload twice, with primitive-only receipts crossing map changes."""
import unreal,gc,json
from pathlib import Path
B=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate8Validation');rows=[];maps=[]
def check(n,ok,d=''):rows.append({'case':n,'pass':bool(ok),'detail':str(d)})
def inspect(path):
 assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(path)
 actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
 world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
 check('load_'+path,world.get_name()==path.rsplit('/',1)[1] and len(actors)>2,len(actors))
 if path.endswith('Gate7MechanicalTest'):
  vehicle=next(a for a in actors if isinstance(a,unreal.RVMechanicalMotorhome));profile=vehicle.get_editor_property('CoolingSystem').get_editor_property('Profile')
  check('saved_normal_mechanical_profile',profile is not None and profile.get_name()=='DA_NormalMechanical')
  check('saved_normal_repair_durations',[r.duration_seconds for r in profile.get_editor_property('Repairs')]==[8,15,20])
  check('saved_engine_tuning',profile.get_editor_property('Tuning').engine_maximum_condition==1 and profile.get_editor_property('Tuning').engine_warning_fraction==.75)
  check('saved_76_actor_fixture_after_dinette_rest_removal',len(actors)==76,len(actors))
  check('accepted_physical_door_entry',vehicle.get_editor_property('bPhysicalDoorEntry'))
  check('sole_bed_rest_location',sum(isinstance(a,unreal.RVRestPoint) for a in actors)==1)
  check('accepted_roof_access',all(a.get_editor_property('bRoofAccess') for a in actors if isinstance(a,unreal.RVLadder)))
  check('saved_seven_mechanical_pickups',sum(isinstance(a,unreal.RVWorldItem) and a.get_actor_label().startswith('Gate7_') for a in actors)==7)
  check('saved_real_54_part_art',len(vehicle.get_editor_property('VisualParts'))==54)
  check('saved_seven_independent_exterior_compartments',len(vehicle.get_editor_property('ExteriorCompartments'))==7)
  check('saved_rear_seats',all(vehicle.get_editor_property(n).get_editor_property('bEnabled') for n in ['DinetteFrontSeat','DinetteRearSeat']))
  arm=vehicle.get_component_by_class(unreal.SpringArmComponent);camera=vehicle.get_component_by_class(unreal.CameraComponent)
  check('accepted_camera_preserved',arm.get_editor_property('TargetArmLength')==1400 and camera.get_editor_property('FieldOfView')==85 and arm.get_editor_property('bDoCollisionTest'))
  boxes={str(x.name):x for x in vehicle.get_editor_property('InteriorCollision')}
  check('front_firewall_side_step_collision_preserved',{'FrontFascia','HoodTop','FrontWall','CabExteriorLeft','CabExteriorRight','EntryStepLow','BedEndWardrobe'}.issubset(boxes))
  check('no_invisible_stair_player_solution',all(x.get_editor_property('bVisiblePrototype')==(name=='EntryStepLow') for name,x in boxes.items()))
  bed=next(a for a in actors if isinstance(a,unreal.RVRestPoint) and str(a.get_editor_property('DisplayName'))=='Rear bed')
  check('saved_lying_pose_and_wake_aisle',bed.get_editor_property('bUseLyingPose') and bed.get_editor_property('WakeAisleLocation').x==-115)
  check('saved_ladder',sum(isinstance(a,unreal.RVLadder) for a in actors)==1)
  labels={str(a.get_editor_property('Container').get_editor_property('DisplayName')) for a in actors if isinstance(a,unreal.RVStoragePoint)}
  check('saved_interior_layout_roles',{'Pantry','Water supplies','Personal supplies','Medical storage','Bed-end cabinet','Dinette overhead - dry food','Kitchen overhead - small tools','Rear overhead - medical backup'}.issubset(labels),labels)
 return {'map':path,'actors':len(actors)}
try:
 for repeat in range(1):
  for name in ['Gate1Test','Gate2VehicleTest','Gate3MovingInteriorTest','Gate4InventoryTest','Gate5SurvivalTest','Gate6FuelElectricalTest','Gate7MechanicalTest','Gate8MedicalTest']:
   gc.collect();unreal.SystemLibrary.collect_garbage();maps.append(inspect('/Game/Maps/'+name))
 # New medical assets and map are inspected in a scoped call before any further world change.
 def medical_saved():
  actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors();v=next(a for a in actors if isinstance(a,unreal.RVMechanicalMotorhome));station=next(a for a in actors if isinstance(a,unreal.RVMedicalStation))
  check('Gate8_real_art_preserved',len(v.get_editor_property('VisualParts'))==54)
  check('Gate8_exterior_compartments_preserved',len(v.get_editor_property('ExteriorCompartments'))==7)
  check('Gate8_station_linked_medical_storage',str(station.get_editor_property('LinkedStorage').get_editor_property('DisplayName'))=='Medical storage')
  check('Gate8_station_single',sum(isinstance(a,unreal.RVMedicalStation) for a in actors)==1)
  check('Gate8_medical_pickups',sum(isinstance(a,unreal.RVWorldItem) and a.get_actor_label().startswith('Gate8_') for a in actors)==9)
  check('Gate8_game_mode',unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_world_settings().get_editor_property('DefaultGameMode').get_name()=='BP_Gate8GameMode_C')
  for name in ['NormalMedical','Bandage','Gauze','PressureDressing','Antiseptic','Splint','BurnDressing','PainMedication','FirstAidKit','AdvancedKit']:
   asset=unreal.load_asset('/Game/Medical/DA_'+name);check('saved_medical_'+name,asset is not None)
 medical_saved()
 gc.collect();unreal.SystemLibrary.collect_garbage()
 check('save_clean_packages',unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True))
 (B/'saved-audit.json').write_text(json.dumps({'results':rows,'maps':maps},indent=2,default=str))
except Exception as e:
 rows.append({'case':'saved_audit_exception','pass':False,'detail':repr(e)});(B/'saved-audit.json').write_text(json.dumps({'results':rows,'maps':maps},indent=2,default=str))
finally:
 gc.collect();unreal.SystemLibrary.collect_garbage();unreal.SystemLibrary.quit_editor()
