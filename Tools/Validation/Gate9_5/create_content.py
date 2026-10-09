"""Gate9.5 project-side derivatives. No previous map or vendor package writes."""
import unreal,json,gc,traceback
from pathlib import Path
root=Path('D:/GitHub/RVSurvival/RVSurvival');out=root/'Docs/Gate9_5Results';folder='/Game/Combat/Gate9_5';chars='/Game/Characters/RV/Gate9_5'
def save(a):
 assert a and unreal.EditorAssetLibrary.save_loaded_asset(a,False)
def duplicate(old,new):
 return unreal.load_asset(new) or unreal.EditorAssetLibrary.duplicate_asset(old,new)
def build():
 levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);target='/Game/Maps/Gate9_5CombatRefinementTest'
 if not unreal.EditorAssetLibrary.does_asset_exist(target):
  assert levels.load_level('/Game/Maps/Gate9CombatInfectedTest')
  assert unreal.EditorLoadingAndSavingUtils.save_map(unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world(),target)
 else:assert levels.load_level(target)
 tools=unreal.AssetToolsHelpers.get_asset_tools();actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
 meshes=[]
 for stem in ['NonRigged_M1911','NonRigged_M1911_Magazine']:
  path='/Game/ThirdParty/Xeradev/M1911/'+stem
  mesh=unreal.load_asset(path)
  if not mesh:
   options=unreal.FbxImportUI();options.set_editor_property('bImportMesh',True);options.set_editor_property('bImportAsSkeletal',False);options.set_editor_property('bImportMaterials',False);options.set_editor_property('bImportTextures',False);options.set_editor_property('MeshTypeToImport',unreal.FBXImportType.FBXIT_STATIC_MESH);options.set_editor_property('bAutomatedImportShouldDetectType',False)
   data=options.get_editor_property('StaticMeshImportData');data.set_editor_property('bCombineMeshes',True);data.set_editor_property('bAutoGenerateCollision',True)
   task=unreal.AssetImportTask();task.set_editor_property('Filename',str(root/'Saved/Gate9_5Assets/M1911/FBX/NonRigged'/f'{stem}.fbx'));task.set_editor_property('DestinationPath','/Game/ThirdParty/Xeradev/M1911');task.set_editor_property('DestinationName',stem);task.set_editor_property('Automated',True);task.set_editor_property('Save',True);task.set_editor_property('Options',options);tools.import_asset_tasks([task]);mesh=unreal.load_asset(path)
  assert mesh,path;meshes.append(mesh)
 cube=unreal.load_asset('/Engine/BasicShapes/Cube');crowbar=unreal.load_asset(folder+'/SM_SM_PrototypeCrowbar')
 if not crowbar:
  parts=[]
  for name,pos,scale,rotation in [('Shaft',(0,0,0),(.025,.025,.65),unreal.Rotator()),('Hook',(0,5,30),(.025,.12,.025),unreal.Rotator()),('Claw',(0,10,27),(.025,.025,.08),unreal.Rotator()),('PryTip',(0,0,-34),(.04,.025,.055),unreal.Rotator())]:
   a=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*pos),rotation);a.set_actor_label('TemporaryGate9_5Crowbar_'+name);a.static_mesh_component.set_static_mesh(cube);a.set_actor_scale3d(unreal.Vector(*scale));parts.append(a)
  opts=unreal.MergeStaticMeshActorsOptions();opts.set_editor_property('BasePackageName',folder+'/SM_PrototypeCrowbar');opts.set_editor_property('destroy_source_actors',True);opts.set_editor_property('spawn_merged_actor',True)
  merged=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem).merge_static_mesh_actors(parts,opts);assert merged;crowbar=merged.static_mesh_component.get_editor_property('StaticMesh');actors.destroy_actor(merged);save(crowbar)
 presets=[]
 for name in ['Relaxed','Standard','Harsh']:
  path=folder+'/Difficulty/DA_'+name;p=unreal.load_asset(path)
  if not p:
   f=unreal.DataAssetFactory();f.set_editor_property('DataAssetClass',unreal.RVDifficultyProfile);p=tools.create_asset('DA_'+name,folder+'/Difficulty',unreal.RVDifficultyProfile,f)
  p.modify();p.set_editor_property('Preset',name);rules=list(p.get_editor_property('Rules'))
  relaxed={'Recovery':1.5,'Loot':1.5,'InfectedDurability':.85,'InfectedPerception':.85};harsh={'Recovery':.75,'Loot':.65,'InfectedDurability':1.15,'InfectedPerception':1.2}
  for r in rules:
   key=str(r.get_editor_property('Id'));r.set_editor_property('Multiplier',1 if name=='Standard' else relaxed.get(key,.7) if name=='Relaxed' else harsh.get(key,1.4))
  p.set_editor_property('Rules',rules);save(p);presets.append(p)
 gs=unreal.load_asset(folder+'/BP_Gate9_5GameState')
 if not gs:
  f=unreal.BlueprintFactory();f.set_editor_property('ParentClass',unreal.RVGameState);gs=tools.create_asset('BP_Gate9_5GameState',folder,unreal.Blueprint,f)
 unreal.BlueprintEditorLibrary.compile_blueprint(gs);gs.modify();cdo=unreal.get_default_object(unreal.EditorAssetLibrary.load_blueprint_class(folder+'/BP_Gate9_5GameState'));cdo.modify();cdo.set_editor_property('DifficultyPresets',presets);save(gs)
 mesh=unreal.load_asset('/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple');base=unreal.load_asset('/Game/Characters/Mannequins/Anims/Pistol/MF_Pistol_Idle_ADS');montages=[]
 for name,shove in [('Shove',True),('CrowbarSwing',False)]:
  pose=unreal.RVCharacterContentLibrary.create_prototype_melee(chars+'/A_'+name,mesh,shove,base);save(pose)
  f=unreal.AnimMontageFactory();f.set_editor_property('TargetSkeleton',mesh.get_editor_property('Skeleton'));f.set_editor_property('SourceAnimation',pose)
  m=unreal.load_asset(chars+'/AM_'+name) or tools.create_asset('AM_'+name,chars,unreal.AnimMontage,f);m.modify();tracks=list(m.get_editor_property('SlotAnimTracks'))
  for track in tracks:track.set_editor_property('SlotName','DefaultSlot')
  m.set_editor_property('SlotAnimTracks',tracks);save(m);montages.append(m)
 definitions=[]
 for name,old,visual in [('DA_M1911_45ACP','/Game/Combat/Items/DA_9mmHandgun',meshes[0]),('DA_45ACPMagazine','/Game/Combat/Items/DA_9mmMagazine',meshes[1]),('DA_PrototypeCrowbar','/Game/Combat/Items/DA_9mmHandgun',crowbar)]:
  d=duplicate(old,folder+'/Items/'+name);d.modify();d.set_editor_property('CatalogId',name);d.set_editor_property('DisplayName','M1911 .45 ACP' if name=='DA_M1911_45ACP' else '.45 ACP magazine' if name=='DA_45ACPMagazine' else 'Prototype crowbar');d.set_editor_property('WorldMesh',visual);d.set_editor_property('WorldVisualScale',unreal.Vector(1,1,1));d.set_editor_property('PickupSeconds',0)
  c=d.get_editor_property('Combat');is_melee=name=='DA_PrototypeCrowbar';c.set_editor_property('bMelee',is_melee);c.set_editor_property('bFirearm',name=='DA_M1911_45ACP');c.set_editor_property('bMagazine',name=='DA_45ACPMagazine');c.set_editor_property('Caliber',unreal.RVItemDefinition.find_registered_tag('Item.Ammo.45ACP'));c.set_editor_property('MagazineCapacity',7);c.set_editor_property('InitialRounds',7);c.set_editor_property('Damage',24 if is_melee else 35);c.set_editor_property('MeleeMontage',montages[1]);c.set_editor_property('bSightADS',not is_melee and name=='DA_M1911_45ACP');d.set_editor_property('Combat',c);save(d);definitions.append(d)
 pawn=duplicate('/Game/Characters/RV/Gate9/BP_Gate9Survivor',chars+'/BP_Gate9_5Survivor');unreal.BlueprintEditorLibrary.compile_blueprint(pawn);pawn.modify();cdo=unreal.get_default_object(unreal.EditorAssetLibrary.load_blueprint_class(chars+'/BP_Gate9_5Survivor'));cdo.modify();combat=cdo.get_editor_property('Combat');combat.modify();combat.set_editor_property('ShoveMontage',montages[0]);save(pawn)
 gm=duplicate('/Game/Combat/BP_Gate9GameMode',folder+'/BP_Gate9_5GameMode');unreal.BlueprintEditorLibrary.compile_blueprint(gm);gm.modify();cdo=unreal.get_default_object(unreal.EditorAssetLibrary.load_blueprint_class(folder+'/BP_Gate9_5GameMode'));cdo.modify();cdo.set_editor_property('DefaultPawnClass',unreal.EditorAssetLibrary.load_blueprint_class(chars+'/BP_Gate9_5Survivor'));cdo.set_editor_property('GameStateClass',unreal.EditorAssetLibrary.load_blueprint_class(folder+'/BP_Gate9_5GameState'));save(gm)
 world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();ws=world.get_world_settings();ws.modify();ws.set_editor_property('DefaultGameMode',unreal.EditorAssetLibrary.load_blueprint_class(folder+'/BP_Gate9_5GameMode'))
 for a in actors.get_all_level_actors():
  label=a.get_actor_label()
  if isinstance(a,unreal.RVWorldItem) and (label.startswith('Gate9_Handgun_') or label.startswith('Gate9_Magazine_')):
   a.modify();item=a.get_editor_property('Item');item.set_editor_property('Definition',definitions[0] if 'Handgun' in label else definitions[1]);item.set_editor_property('MagazineRounds',7 if 'Magazine' in label and not label.endswith('_7') else 0);a.set_editor_property('Item',item);a.get_component_by_class(unreal.StaticMeshComponent).set_static_mesh(meshes[0] if 'Handgun' in label else meshes[1]);a.set_actor_scale3d(unreal.Vector(1,1,1))
 existing={a.get_actor_label():a for a in actors.get_all_level_actors()}
 for i in range(2):
  label='Gate9_5_Crowbar_'+str(i);a=existing.get(label) or actors.spawn_actor_from_class(unreal.RVWorldItem,unreal.Vector(-240+i*90,470,60));a.set_actor_label(label);a.modify();item=unreal.RVItemInstance();item.set_editor_property('Id',unreal.GuidLibrary.new_guid());item.set_editor_property('Definition',definitions[2]);a.set_editor_property('Item',item);a.get_component_by_class(unreal.StaticMeshComponent).set_static_mesh(crowbar);a.set_actor_scale3d(unreal.Vector(1,1,1))
 assert unreal.EditorLoadingAndSavingUtils.save_map(world,target)
 return {'map':target,'meshes':[{'path':m.get_path_name(),'bounds':str(m.get_bounds())} for m in meshes],'saved':True,'assets':list(unreal.EditorAssetLibrary.list_assets(folder,True,False))}
try:result=build();(out/'content.json').write_text(json.dumps(result,indent=2))
except Exception:(out/'content-error.txt').write_text(traceback.format_exc());traceback.print_exc()
finally:gc.collect();unreal.SystemLibrary.quit_editor()
