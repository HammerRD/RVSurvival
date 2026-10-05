import unreal,json,gc
B='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate4Validation/'
rows=[]
def check(name,ok,detail=''):
 rows.append({'case':name,'pass':bool(ok),'detail':str(detail)})
 unreal.log('GATE4_RECOVERY '+json.dumps(rows[-1]))
def save_copy(path):
 # World wrapper is scoped to this operation and never crosses LoadLevel.
 world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
 assert unreal.EditorLoadingAndSavingUtils.save_map(world,path)
def inspect():
 actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
 storage=unreal.load_class(None,'/Script/RVSurvival.RVStoragePoint')
 pickups=unreal.load_class(None,'/Script/RVSurvival.RVWorldItem')
 return {'actors':len(actors),'storage':sum(a.get_class()==storage for a in actors),'pickups':sum(a.get_class()==pickups for a in actors)}
def load(path):
 # No UObject arrays, world wrappers, callbacks or PIE state are retained here.
 gc.collect();unreal.SystemLibrary.collect_garbage()
 assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(path)
 check('load_'+path,True)
for i in range(3):
 load('/Game/Maps/Gate3MovingInteriorTest')
 scratch='/Game/Maps/ValidationRecovery/Gate4Copy_'+str(i)
 save_copy(scratch)
 load(scratch)
 check('saved_copy_reopened_'+str(i),True)
 for path in ['/Game/Maps/Gate1Test','/Game/Maps/Gate2VehicleTest','/Game/Maps/Gate3MovingInteriorTest','/Game/Maps/Gate4InventoryTest']:
  load(path)
 data=inspect();check('gate4_fixture_'+str(i),data['storage']==6 and data['pickups']==11,data)
json.dump({'results':rows},open(B+'recovery-repeat.json','w'),indent=2)
gc.collect();unreal.SystemLibrary.collect_garbage()
unreal.log('GATE4_RECOVERY_REPEAT_COMPLETE')
unreal.SystemLibrary.quit_editor()
