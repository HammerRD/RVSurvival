"""Read the final saved character/map in a fresh editor; no reload loop or PIE."""
import unreal, gc, json
from pathlib import Path
root=Path('D:/GitHub/RVSurvival/RVSurvival')
rows=[]
def check(name,ok,detail=''):
    rows.append({'case':name,'pass':bool(ok),'detail':str(detail)})
def audit():
    world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    check('saved_new_map',world.get_name()=='Gate8_5CharacterTest')
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    check('saved_86_actors',len(actors)==86,len(actors))
    gm=world.get_world_settings().get_editor_property('DefaultGameMode')
    check('saved_presentation_game_mode',gm.get_name()=='BP_Gate8_5GameMode_C',gm.get_name())
    pawn=unreal.get_default_object(unreal.get_default_object(gm).get_editor_property('DefaultPawnClass'))
    component=pawn.get_editor_property('CharacterPresentation');profile=component.get_editor_property('Profile')
    check('saved_opt_in_profile',profile is not None and component.has_configured_visuals())
    check('epic_mesh_and_skeleton',profile.get_editor_property('Body').get_name()=='SKM_Manny_Simple' and profile.get_editor_property('Body').get_editor_property('Skeleton').get_name()=='SK_Mannequin')
    for prop,expected in [('OwnerCameraOffset',(20,0,0)),('SeatedOffset',(0,0,-25)),('InteriorSeatedOffset',(0,0,0)),('BedOffset',(-85,0,0)),('DownedOffset',(85,0,15))]:
        value=profile.get_editor_property(prop);check('saved_'+prop,(value.x,value.y,value.z)==expected,value)
    check('saved_bed_orientation',profile.get_editor_property('BedMeshRotation').yaw==90)
    for bone,region in [('head','HEAD'),('spine_03','TORSO'),('hand_l','LEFT_ARM'),('hand_r','RIGHT_ARM'),('foot_l','LEFT_LEG'),('foot_r','RIGHT_LEG')]:
        check('logical_bone_'+region,component.resolve_body_region(bone)==getattr(unreal.RVBodyRegion,region))
    anchors=profile.get_editor_property('EquipmentAnchors')
    check('seven_named_attachment_specs',len(anchors)==7 and len({str(a.id) for a in anchors})==7)
    vehicle=next(a for a in actors if isinstance(a,unreal.RVMechanicalMotorhome))
    check('accepted_54_part_art',len(vehicle.get_editor_property('VisualParts'))==54)
    check('seven_exterior_containers',len(vehicle.get_editor_property('ExteriorCompartments'))==7)
    check('physical_side_entry',vehicle.get_editor_property('bPhysicalDoorEntry'))
    check('sole_rear_bed',sum(isinstance(a,unreal.RVRestPoint) for a in actors)==1)
    check('roof_access',all(a.get_editor_property('bRoofAccess') for a in actors if isinstance(a,unreal.RVLadder)))
    check('medical_station_preserved',sum(isinstance(a,unreal.RVMedicalStation) for a in actors)==1)
    for name in ['Driver','Passenger','Bed','Downed','DownedSeated','Ladder','Treatment']:
        check('saved_sequence_'+name,unreal.load_asset('/Game/Characters/RV/Animations/A_Prototype'+name) is not None)
    check('saved_anim_blueprint',unreal.load_asset('/Game/Characters/RV/Animations/ABP_RVHumanoid') is not None)
    check('saved_blend_space',unreal.load_asset('/Game/Characters/RV/Animations/BS_RVLocomotion') is not None)
    check('assets_save',unreal.EditorLoadingAndSavingUtils.save_dirty_packages(False,True))
    check('new_map_save',unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level())
try:
    audit()
except Exception as e:
    check('audit_exception',False,repr(e))
finally:
    (root/'Docs/Gate8_5Results/saved-audit.json').write_text(json.dumps({'results':rows},indent=2))
    gc.collect();unreal.SystemLibrary.collect_garbage();unreal.SystemLibrary.quit_editor()
