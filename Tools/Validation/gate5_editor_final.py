import unreal,json,gc
B='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate5Validation/'
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
 if path.endswith('Gate5SurvivalTest'):check('gate5_saved_fixture_intact',counts['actors']==64 and counts['pickups']==11 and counts['storage']==7 and counts['rest']==2 and counts['gamemode'].endswith('BP_Gate5GameMode_C'),counts)
 check('load_'+path,True);return {'path':path,'counts':counts}
def inspect_assets():
 for path in ['/Game/Items/DA_Food','/Game/Items/DA_Water','/Game/Survival/DA_NormalNeeds','/Game/Survival/BP_SurvivalPlayerState','/Game/Survival/BP_Gate5GameMode']:
  asset=unreal.load_asset(path);check('asset_'+path,asset is not None)
 for name,n,h in [('Food',25,0),('Water',0,35)]:
  m=unreal.load_asset('/Game/Items/DA_'+name).get_editor_property('Consumable');check('saved_consumable_'+name,m.get_editor_property('bConsumable') and m.nutrition==n and m.hydration==h)
 cls=unreal.EditorAssetLibrary.load_blueprint_class('/Game/Survival/BP_SurvivalPlayerState');profile=unreal.get_default_object(cls).get_editor_property('Needs').get_editor_property('TuningAsset');check('saved_tuning_reference',profile is not None and profile.get_name()=='DA_NormalNeeds')
for repeat in range(2):
 for path in ['/Game/Maps/Gate1Test','/Game/Maps/Gate2VehicleTest','/Game/Maps/Gate3MovingInteriorTest','/Game/Maps/Gate4InventoryTest','/Game/Maps/Gate5SurvivalTest']:
  # Every previous inspection returned primitives; no World/Actor wrappers cross LoadLevel.
  gc.collect();unreal.SystemLibrary.collect_garbage();maps.append(inspect(path))
inspect_assets();gc.collect();unreal.SystemLibrary.collect_garbage()
check('save_all_completed',unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True))
json.dump({'results':rows,'maps':maps},open(B+'editor-final.json','w'),indent=2)
unreal.SystemLibrary.quit_editor()
