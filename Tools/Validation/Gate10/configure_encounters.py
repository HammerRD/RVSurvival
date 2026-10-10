"""Project-side context assets, opt-in world rules and small encounter zones."""
import unreal,json,time,gc,traceback,uuid,importlib.util
from pathlib import Path
root=Path('D:/GitHub/RVSurvival/RVSurvival');out=root/'Saved/Gate10Validation';started=time.time();phase=0;handle=None

def configure():
 spec=importlib.util.spec_from_file_location('gate10_locations',root/'Tools/Validation/Gate10/author_locations.py')
 locations=importlib.util.module_from_spec(spec);spec.loader.exec_module(locations)
 receipt=locations.build();(out/'locations-foundation.json').write_text(json.dumps(receipt,indent=2))
 world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
 actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);tools=unreal.AssetToolsHelpers.get_asset_tools();folder='/Game/World/WNY'
 # Fix logical loot context without changing accepted item definitions.
 for name,tag in {'Kitchen':'FoodAndWater','Medical':'Medical','Garage':'Automotive','RoadSupplies':'RoadSupplies','Camp':'Camping'}.items():
  p=unreal.load_asset(folder+'/Loot/DA_'+name);p.modify();p.set_editor_property('Context',unreal.RVItemDefinition.find_registered_tag('Loot.Context.'+tag));assert unreal.EditorAssetLibrary.save_loaded_asset(p)
 def bp(name,parent):
  path=folder+'/Gameplay/'+name;asset=unreal.load_asset(path)
  if not asset:
   f=unreal.BlueprintFactory();f.set_editor_property('ParentClass',parent);asset=tools.create_asset(name,folder+'/Gameplay',unreal.Blueprint,f)
  unreal.BlueprintEditorLibrary.compile_blueprint(asset);asset.modify();cdo=unreal.get_default_object(unreal.EditorAssetLibrary.load_blueprint_class(path));cdo.modify();return asset,cdo
 cache,cdo=bp('BP_RoadsideSupplyCache',unreal.RVScavengeContainer)
 mesh=cdo.get_component_by_class(unreal.StaticMeshComponent);mesh.modify();mesh.set_relative_scale3d(unreal.Vector(1.2,.8,.8));mesh.set_material(0,unreal.load_asset(folder+'/Materials/M_Wood'));mesh.set_visibility(True);mesh.set_collision_profile_name('BlockAll')
 cdo.get_editor_property('Container').set_editor_property('DisplayName','Roadside supply crate');assert unreal.EditorAssetLibrary.save_loaded_asset(cache)
 presets=[]
 for name in ['Relaxed','Standard','Harsh']:
  path=folder+'/Difficulty/DA_'+name;source='/Game/Combat/Gate9_5/Difficulty/DA_'+name
  asset=unreal.load_asset(path) or unreal.EditorAssetLibrary.duplicate_asset(source,path);assert asset,source
  asset.modify();rules=asset.get_editor_property('Rules')
  for r in rules:
   key=str(r.get_editor_property('Id'))
   if key in ['Loot','Population']:
    r.set_editor_property('bPreparationOnly',False);r.set_editor_property('Group','World')
    r.set_editor_property('Description','Scales finite supplies in newly searched regional containers.' if key=='Loot' else 'Scales initial bounded infected groups in unvisited regional locations.')
  asset.set_editor_property('Rules',rules);assert unreal.EditorAssetLibrary.save_loaded_asset(asset);presets.append(asset)
 gs,cdo=bp('BP_WNYGameState',unreal.RVGameState);cdo.set_editor_property('DifficultyPresets',presets);assert unreal.EditorAssetLibrary.save_loaded_asset(gs)
 path=folder+'/Gameplay/BP_WNYGameMode';gm=unreal.load_asset(path) or unreal.EditorAssetLibrary.duplicate_asset('/Game/Combat/Gate9_5/BP_Gate9_5GameMode',path)
 unreal.BlueprintEditorLibrary.compile_blueprint(gm);gm.modify();cdo=unreal.get_default_object(unreal.EditorAssetLibrary.load_blueprint_class(path));cdo.modify();cdo.set_editor_property('GameStateClass',unreal.EditorAssetLibrary.load_blueprint_class(folder+'/Gameplay/BP_WNYGameState'));assert unreal.EditorAssetLibrary.save_loaded_asset(gm)
 world.get_world_settings().set_editor_property('DefaultGameMode',unreal.EditorAssetLibrary.load_blueprint_class(path))
 existing={a.get_actor_label():a for a in actors.get_all_level_actors()}
 # Remove only the OpenWorld template start in this new map. Authored start remains.
 for a in actors.get_all_level_actors():
  if isinstance(a,unreal.PlayerStart) and not a.actor_has_tag('WNYLocationsMilestone'):actors.destroy_actor(a)
 infected=unreal.load_asset('/Game/Combat/DA_PrototypeInfected');assert infected
 zones=[]
 configurations=[('Pine Creek','GasStation',-130000,6500,'RoadSupplies',.2,.65,.15,3),('Erie Service','AutomotiveGarage',-60000,-8500,'Garage',.3,.5,.2,2),('Hawthorne','Farmhouse',0,47000,'Kitchen',.5,.3,.2,2),('Maple Run','Campground',75000,47000,'Camp',.6,.2,.2,2),('Rowland','Crossroads',140000,8000,'Medical',.3,.5,.2,3),('Roadside West','Roadside',-100000,0,'RoadSupplies',.7,.1,.2,1),('Roadside East','Roadside',100000,0,'RoadSupplies',.7,.15,.15,1)]
 for name,context,x,y,supplies,quiet,cluster,cache_weight,count in configurations:
  asset_path=folder+'/Encounters/DA_'+name.replace(' ','');p=unreal.load_asset(asset_path)
  if not p:
   f=unreal.DataAssetFactory();f.set_editor_property('DataAssetClass',unreal.RVEncounterProfile);p=tools.create_asset('DA_'+name.replace(' ',''),folder+'/Encounters',unreal.RVEncounterProfile,f)
  p.modify();p.set_editor_property('Context',unreal.RVItemDefinition.find_registered_tag('World.Location.'+context));p.set_editor_property('InfectedProfile',infected);p.set_editor_property('SupplyProfile',unreal.load_asset(folder+'/Loot/DA_'+supplies));p.set_editor_property('EventCooldown',70)
  choices=[]
  for outcome,weight in [(unreal.RVEncounterOutcome.QUIET,quiet),(unreal.RVEncounterOutcome.INFECTED_CLUSTER,cluster),(unreal.RVEncounterOutcome.SUPPLY_CACHE,cache_weight)]:
   choice=unreal.RVEncounterChoice();choice.set_editor_property('Outcome',outcome);choice.set_editor_property('Weight',weight);choice.set_editor_property('InfectedCount',count);choices.append(choice)
  p.set_editor_property('Choices',choices);assert unreal.EditorAssetLibrary.save_loaded_asset(p)
  label='WNY encounter '+name;a=existing.get(label) or actors.spawn_actor_from_class(unreal.RVRegionEncounterZone,unreal.Vector(x,y,locations.terrain(x,y)))
  a.set_actor_label(label);a.tags=['WNYEncounterMilestone'];a.modify();ident=str(uuid.uuid5(uuid.NAMESPACE_URL,'RVSurvival/WNY/Encounter/'+name));guid,valid=unreal.GuidLibrary.parse_string_to_guid(ident);assert valid
  a.set_editor_property('ZoneId',guid);a.set_editor_property('Profile',p);a.set_editor_property('SupplyCacheClass',unreal.EditorAssetLibrary.load_blueprint_class(folder+'/Gameplay/BP_RoadsideSupplyCache'))
  a.set_editor_property('SpawnOffsets',[unreal.Vector(dx,dy,0) for dx,dy in [(-1400,1500),(1400,1500),(-1800,-1400),(1800,-1400),(0,2500),(0,-2500)]])
  zones.append({'name':name,'id':ident,'context':context,'quiet_weight':quiet,'cluster_weight':cluster,'supply_weight':cache_weight})
 assert unreal.RVCombatContentLibrary.build_navigation_editor(world)
 levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert levels.save_current_level();assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
 (out/'encounter-configuration.json').write_text(json.dumps({'saved':True,'zones':zones,'navigation':dict(unreal.RVCombatContentLibrary.inspect_navigation(world)),'runtime_and_manual_validation':'pending'},indent=2))
 assert unreal.RVWorldContentLibrary.set_region_authoring_loaded(world,False)

def tick(delta):
 global phase,handle
 if phase==0 and time.time()-started>5:
  phase=10
  try:configure()
  except Exception:(out/'encounter-configuration-error.txt').write_text(traceback.format_exc())
  gc.collect();phase=1
 elif phase==1 and time.time()-started>25:
  unreal.unregister_slate_post_tick_callback(handle);handle=None;phase=2;gc.collect();unreal.SystemLibrary.quit_editor()
handle=unreal.register_slate_post_tick_callback(tick)

