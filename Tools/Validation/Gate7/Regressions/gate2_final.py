def release_child_runners():
 import sys,gc
 current=globals()
 for name,module in list(sys.modules.items()):
  if name.startswith('rv_validation_') and module.__dict__ is not current:
   sys.modules.pop(name);module.__dict__.clear()
 gc.collect()
import unreal,json,time,os,shutil
from runner_runtime import load_runner
B='D:/GitHub/RVSurvival/RVSurvival/'
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level('/Game/Maps/Gate2VehicleTest')
s=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.LevelEditorPlaySettings'));s.set_editor_property('RunUnderOneProcess',True);s.set_editor_property('PlayNumberOfClients',2);s.set_editor_property('AdditionalLaunchParameters','')
n=s.get_editor_property('NetworkEmulationSettings');n.set_editor_property('bIsNetworkEmulationEnabled',False);s.set_editor_property('NetworkEmulationSettings',n)
unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings')).set_editor_property('bThrottleCPUWhenNotForeground',False)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
seed_ids={}
def seed_inventory_fixture():
 w=next(w for w in unreal.ObjectIterator(unreal.World) if '/Game/Maps/UEDPIE_' in w.get_path_name() and w.get_name()=='Gate2VehicleTest' and unreal.GameplayStatics.get_game_mode(w))
 for pawn in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.load_class(None,'/Script/RVSurvival.RVSurvivorCharacter')):
  item=unreal.RVItemInstance();item.set_editor_property('Id',unreal.GuidLibrary.new_guid());item.set_editor_property('Definition',unreal.load_asset('/Game/Items/DA_Water'));item.set_editor_property('Condition',.45)
  pawn.get_component_by_class(unreal.load_class(None,'/Script/RVSurvival.RVInventoryComponent')).add_authority(item);seed_ids[pawn.get_name()]=unreal.GuidLibrary.conv_guid_to_string(item.id)
def verify_inventory_fixture():
 results=[]
 for w in unreal.ObjectIterator(unreal.World):
  if '/Game/Maps/UEDPIE_' not in w.get_path_name() or w.get_name()!='Gate2VehicleTest':continue
  for pawn in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.load_class(None,'/Script/RVSurvival.RVSurvivorCharacter')):
   records=pawn.get_component_by_class(unreal.load_class(None,'/Script/RVSurvival.RVInventoryComponent')).get_items()
   results.append({'case':'inventory_survives_driver_passenger_possession','pass':len(records)==1 and unreal.GuidLibrary.conv_guid_to_string(records[0].id) in seed_ids.values() and records[0].quantity==1 and abs(records[0].condition-.45)<.001,'world':w.get_path_name(),'pawn':pawn.get_name()})
 json.dump(results,open(B+'Docs/Gate7Results/Regressions/Gate2Regression/inventory-possession.json','w'),indent=2)
t=0;loaded=False;ending=None;started=time.time()
def tick(dt):
 global t,loaded,ending
 t+=dt
 if t>6 and not loaded:loaded=True;seed_inventory_fixture();load_runner(B+'Saved/Gate2Validation/multi.py')
 p=B+'Saved/Gate2Validation/multi.json'
 if loaded and not ending and os.path.exists(p) and os.path.getmtime(p)>started:
  d=json.load(open(p));os.makedirs(B+'Docs/Gate7Results/Regressions/Gate2Regression',exist_ok=True);shutil.copyfile(p,B+'Docs/Gate7Results/Regressions/Gate2Regression/shared.json')
  verify_inventory_fixture();release_child_runners();unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play();ending=time.time()+4
 if ending and time.time()>ending:
  unreal.unregister_slate_post_tick_callback(h);quit=unreal.SystemLibrary.quit_editor
  from runner_runtime import release_runners
  release_runners();quit()
h=unreal.register_slate_post_tick_callback(tick)
