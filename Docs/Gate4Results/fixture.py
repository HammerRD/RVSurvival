import unreal,json
B='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate4Validation/'
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert level.load_level('/Game/Maps/Gate3MovingInteriorTest')
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert unreal.EditorLoadingAndSavingUtils.save_map(world,'/Game/Maps/Gate4InventoryTest')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
IC=unreal.load_class(None,'/Script/RVSurvival.RVItemDefinition')
PC=unreal.load_class(None,'/Script/RVSurvival.RVWorldItem')
SC=unreal.load_class(None,'/Script/RVSurvival.RVStoragePoint')
VC=unreal.load_class(None,'/Script/RVSurvival.RVInteriorMotorhome')
rv=next(a for a in actors.get_all_level_actors() if isinstance(a,unreal.WheeledVehiclePawn))
factory=unreal.DataAssetFactory();factory.set_editor_property('DataAssetClass',IC)
tools=unreal.AssetToolsHelpers.get_asset_tools()
records=[('Water','Bottled water',1.1,1.2,6,False),('Food','Canned food',.45,.5,10,False),('Bandage','Bandage',.05,.1,10,False),('Medication','Pain medication',.05,.1,5,False),('FuelCan','Fuel can',12,22,1,False),('EnginePart','Engine part',18,8,1,False),('Scrap','Scrap metal',2,1,10,False),('Tool','Hand tool',1.5,2,1,False),('Ammo','Inert ammunition box',1,1,5,False),('Bulky','Bulky supply crate',2,40,1,False),('Battery','Large battery',30,25,1,True)]
manifest=[]
for i,(key,name,kg,litres,stack,carry) in enumerate(records):
 path='/Game/Items/DA_'+key
 asset=tools.create_asset('DA_'+key,'/Game/Items',IC,factory)
 asset.set_editor_property('CatalogId',key);asset.set_editor_property('DisplayName',name)
 asset.set_editor_property('Description','Gate 4 inert logistics prototype; no survival effects.')
 asset.set_editor_property('WeightKg',kg);asset.set_editor_property('VolumeLitres',litres)
 asset.set_editor_property('bStackable',stack>1);asset.set_editor_property('MaxStackSize',stack)
 asset.set_editor_property('bSupportsCondition',True);asset.set_editor_property('bRequiresPhysicalCarry',carry)
 unreal.EditorAssetLibrary.save_loaded_asset(asset)
 pickup=actors.spawn_actor_from_class(PC,unreal.Vector(600+i*100,-650,30))
 pickup.set_actor_label('Gate4_'+key)
 item=pickup.get_editor_property('Item');item.set_editor_property('Definition',asset);item.set_editor_property('Condition',.73)
 item.set_editor_property('Quantity',min(3,stack));pickup.set_editor_property('Item',item)
 manifest.append({'id':key,'kg':kg,'litres':litres,'max_stack':stack,'physical_carry':carry})
positions=[('Pantry',unreal.Vector(-40,-62,155)),('General cabinet',unreal.Vector(-200,76,155)),('Medical storage',unreal.Vector(-145,80,155)),('Tool storage',unreal.Vector(-190,-100,155)),('Exterior compartment',unreal.Vector(-180,140,65))]
mesh=rv.get_editor_property('Mesh')
for name,pos in positions:
 point=actors.spawn_actor_from_class(SC,rv.get_actor_transform().transform_location(pos));point.set_actor_label('Gate4_'+name)
 point.attach_to_component(mesh,'',unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,False)
 c=point.get_editor_property('Container');c.set_editor_property('DisplayName',name);c.set_editor_property('MaxVolumeLitres',60)
point=actors.spawn_actor_from_class(SC,unreal.Vector(600,-350,100));point.set_actor_label('Gate4_ExternalStorage')
point.get_editor_property('Container').set_editor_property('DisplayName','External storage')
assert level.save_current_level()
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
json.dump({'map':'/Game/Maps/Gate4InventoryTest','definitions':manifest,'rv_storage':[p[0] for p in positions]},open(B+'fixture.json','w'),indent=2)
unreal.log('GATE4_FIXTURE_SAVED')
unreal.SystemLibrary.quit_editor()

