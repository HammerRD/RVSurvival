"""Fresh editor saved-content audit; scoped UObjects released before clean shutdown."""
import unreal,gc,json
from pathlib import Path
root=Path('D:/GitHub/RVSurvival/RVSurvival');rows=[]
def check(n,b,d=''):rows.append({'case':n,'pass':bool(b),'detail':str(d)})
def audit():
 levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert levels.load_level('/Game/Maps/Gate9CombatInfectedTest')
 world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
 check('saved map and actor count',world.get_name()=='Gate9CombatInfectedTest' and len(actors)==103,len(actors))
 gm=world.get_world_settings().get_editor_property('DefaultGameMode');check('Gate9 game mode',gm.get_name()=='BP_Gate9GameMode_C')
 pawn=unreal.get_default_object(unreal.get_default_object(gm).get_editor_property('DefaultPawnClass'));combat=pawn.get_component_by_class(unreal.RVCombatComponent);check('Gate9 combat opt-in',combat is not None and combat.get_editor_property('bEnabled'))
 profile=pawn.get_component_by_class(unreal.RVCharacterPresentationComponent).get_editor_property('Profile');offset=profile.get_editor_property('OwnerCameraOffset');check('saved first-person camera clearance',(offset.x,offset.y,offset.z)==(0,0,4))
 check('six logical regions',len(profile.get_editor_property('BodyRegions'))==6)
 check('seven replaceable equipment anchors',len(profile.get_editor_property('EquipmentAnchors'))==7)
 gun=unreal.load_asset('/Game/Combat/Items/DA_9mmHandgun');mag=unreal.load_asset('/Game/Combat/Items/DA_9mmMagazine');metadata=gun.get_editor_property('Combat')
 check('typed caliber compatibility',unreal.GameplayTagLibrary.equal_equal_gameplay_tag(metadata.get_editor_property('Caliber'),mag.get_editor_property('Combat').get_editor_property('Caliber')))
 check('15-round real magazine',mag.get_editor_property('Combat').get_editor_property('MagazineCapacity')==15 and not mag.get_editor_property('bStackable'))
 check('native recoil tuning',abs(metadata.get_editor_property('RecoilPitch')-.7)<.001 and abs(metadata.get_editor_property('RecoilYaw')-.12)<.001 and abs(metadata.get_editor_property('RecoilRecoverySeconds')-.18)<.001)
 for field in ['WorldMesh']:
  check('saved firearm '+field,gun.get_editor_property(field) is not None)
 for field in ['ShotSound','FireMontage','ReloadMontage']:check('saved firearm '+field,metadata.get_editor_property(field) is not None)
 pickups=[a for a in actors if isinstance(a,unreal.RVWorldItem)]
 guns=[a for a in pickups if a.get_editor_property('Item').definition==gun];mags=[a for a in pickups if a.get_editor_property('Item').definition==mag]
 check('two placed world firearms',len(guns)==2);check('eight placed GUID-backed magazines',len(mags)==8 and len({str(a.get_editor_property('Item').id) for a in mags})==8)
 check('full partial empty map specimens',sorted(a.get_editor_property('Item').magazine_rounds for a in mags)==[0,6,15,15,15,15,15,15])
 infected=[a for a in actors if isinstance(a,unreal.RVInfected)];check('three placed configurable infected',len(infected)==3 and all(a.get_editor_property('Profile') for a in infected))
 check('saved native NavMesh and bounds',any(isinstance(a,unreal.RecastNavMesh) for a in actors) and any(isinstance(a,unreal.NavMeshBoundsVolume) for a in actors))
 vehicle=next(a for a in actors if isinstance(a,unreal.RVMechanicalMotorhome));check('54 purchased visual parts preserved',len(vehicle.get_editor_property('VisualParts'))==54);check('seven exterior compartments preserved',len(vehicle.get_editor_property('ExteriorCompartments'))==7)
 check('physical side entry preserved',vehicle.get_editor_property('bPhysicalDoorEntry'));check('one reusable bed preserved',sum(isinstance(a,unreal.RVRestPoint) for a in actors)==1)
 assets=[]
 for directory in ['/Game/Combat','/Game/Characters/RV/Gate9']:
  for path in unreal.EditorAssetLibrary.list_assets(directory,True,False):
   asset=unreal.load_asset(path);check('saved asset loads '+path,asset is not None);assets.append(path)
   assert unreal.EditorAssetLibrary.save_loaded_asset(asset,True)
 check('explicit final map save',levels.save_current_level())
 return assets
try:assets=audit()
except Exception as e:check('audit error',False,repr(e));assets=[]
finally:
 (root/'Docs/Gate9Results/saved-audit.json').write_text(json.dumps({'results':rows,'assets':assets},indent=2));gc.collect();unreal.SystemLibrary.collect_garbage();unreal.SystemLibrary.quit_editor()

