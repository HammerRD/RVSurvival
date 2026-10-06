import unreal,json,gc
B='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate6Validation/'
BP='/Game/Vehicles/Gate6/BP_ClassCSystemsMotorhome'
def make():
 level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
 if unreal.EditorAssetLibrary.does_asset_exist('/Game/Maps/Gate6FuelElectricalTest'):
  assert level.load_level('/Game/Maps/Gate6FuelElectricalTest')
 else:
  assert level.load_level('/Game/Maps/Gate5SurvivalTest')
  assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
  assert unreal.EditorLoadingAndSavingUtils.save_map(unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world(),'/Game/Maps/Gate6FuelElectricalTest')
 tools=unreal.AssetToolsHelpers.get_asset_tools()
 bp=unreal.load_asset(BP) or unreal.EditorAssetLibrary.duplicate_asset('/Game/Vehicles/Gate5Refinement/BP_ClassCRefinedMotorhome',BP)
 unreal.BlueprintEditorLibrary.reparent_blueprint(bp,unreal.RVSystemsMotorhome)
 unreal.BlueprintEditorLibrary.compile_blueprint(bp)
 cls=unreal.EditorAssetLibrary.load_blueprint_class(BP);c=unreal.get_default_object(cls)
 factory=unreal.DataAssetFactory();factory.set_editor_property('DataAssetClass',unreal.RVEnergyProfile)
 profile=unreal.load_asset('/Game/Resources/DA_NormalRVEnergy') or tools.create_asset('DA_NormalRVEnergy','/Game/Resources',unreal.RVEnergyProfile,factory)
 profile.set_editor_property('Values',c.get_editor_property('Electrical').get_editor_property('Tuning'))
 assert unreal.EditorAssetLibrary.save_loaded_asset(profile,False)
 c.get_editor_property('Electrical').set_editor_property('Profile',profile)
 # Distinct panel next to existing power marker; all six placeholder checks remain available.
 c.set_editor_property('PowerPanelLocation',unreal.Vector(65,65,190))
 c.set_editor_property('FuelFillLocation',unreal.Vector(-155,-137,120))
 unreal.BlueprintEditorLibrary.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,False)
 es=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
 old=next(a for a in es.get_all_level_actors() if isinstance(a,unreal.RVInteriorMotorhome))
 t=old.get_actor_transform();new=es.spawn_actor_from_class(cls,t.translation,t.rotation.rotator());new.set_actor_label('ClassC_RV_Gate6_Systems')
 for a in list(es.get_all_level_actors()):
  if a.get_attach_parent_actor()==old:
   a.attach_to_component(new.get_component_by_class(unreal.SkeletalMeshComponent),'',unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,False)
 es.destroy_actor(old);new.refresh_configuration()
 defs=[]
 for name,capacity,amount,ftype in [('Full',20,20,'Gasoline'),('Partial',10,3.75,'Gasoline'),('Empty',20,0,'Gasoline'),('Diesel',20,20,'Diesel')]:
  path='/Game/Resources/DA_FuelCan'+name
  asset=unreal.load_asset(path) or unreal.EditorAssetLibrary.duplicate_asset('/Game/Items/DA_FuelCan',path)
  asset.set_editor_property('CatalogId','FuelCan'+name);asset.set_editor_property('DisplayName',unreal.Text(name+' fuel can'))
  meta=asset.get_editor_property('Fuel');meta.set_editor_property('bFuelContainer',True);meta.set_editor_property('FuelType',unreal.RVItemDefinition.find_registered_tag('Resource.Fuel.'+ftype));meta.set_editor_property('CapacityLitres',capacity);meta.set_editor_property('InitialLitres',amount)
  asset.set_editor_property('Fuel',meta);assert unreal.EditorAssetLibrary.save_loaded_asset(asset,False)
  pickup=next((a for a in es.get_all_level_actors() if a.get_actor_label()=='Gate6_Fuel_'+name),None) or es.spawn_actor_from_class(unreal.RVWorldItem,unreal.Vector(500+len(defs)*130,-950,35));pickup.set_actor_label('Gate6_Fuel_'+name)
  item=pickup.get_editor_property('Item');item.set_editor_property('Definition',asset);item.set_editor_property('Condition',.73);pickup.set_editor_property('Item',item)
  defs.append({'asset':path,'capacity_litres':capacity,'initial_litres':amount,'type':ftype})
 assert level.save_current_level();assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
 json.dump({'map':'/Game/Maps/Gate6FuelElectricalTest','blueprint':BP,'fuel_cans':defs,'actors':len(es.get_all_level_actors()),'profile':profile.get_path_name()},open(B+'configured.json','w'),indent=2)
try:
 make()
 gc.collect();unreal.SystemLibrary.collect_garbage();unreal.log('GATE6_FIXTURE_SAVED')
except Exception:
 import traceback
 unreal.log_error(traceback.format_exc())
finally:
 unreal.SystemLibrary.quit_editor()
