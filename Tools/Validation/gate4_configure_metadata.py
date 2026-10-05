import unreal,json,gc
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level('/Game/Maps/Gate4InventoryTest')
def tag(name):
 t=unreal.RVItemDefinition.find_registered_tag(name)
 assert unreal.GameplayTagLibrary.is_gameplay_tag_valid(t)
 return t
def tags(names):return unreal.GameplayTagLibrary.make_gameplay_tag_container_from_array([tag(n) for n in names])
def configure():
 categories={'Water':'Water','Food':'Food','Bandage':'Medical','Medication':'Medical','FuelCan':'Automotive','EnginePart':'Automotive','Scrap':'Material','Tool':'Tool','Ammo':'Ammunition','Bulky':'Bulky','Battery':'Automotive'}
 for key,category in categories.items():
  asset=unreal.load_asset('/Game/Items/DA_'+key);name='Item.Category.'+category
  asset.set_editor_property('Category',tag(name))
  asset.set_editor_property('Tags',tags([name]+(['Item.Capability.HandCarry'] if key=='Battery' else [])))
  asset.set_editor_property('bEquippable',key=='Tool')
  if key=='Scrap':asset.set_editor_property('CraftingTags',tags(['Crafting.Material.Metal']))
  if key=='Tool':asset.set_editor_property('CraftingTags',tags(['Crafting.Tool.General']))
  assert unreal.EditorAssetLibrary.save_loaded_asset(asset)
 subsystem=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
 PC=unreal.load_class(None,'/Script/RVSurvival.RVWorldItem');SC=unreal.load_class(None,'/Script/RVSurvival.RVStoragePoint')
 for actor in subsystem.get_all_level_actors():
  if actor.get_class()==PC:
   item=actor.get_editor_property('Item');state=unreal.RVItemStateEntry();state.set_editor_property('Key','Batch');state.set_editor_property('Value','Gate4Prototype');item.set_editor_property('CustomState',[state]);actor.set_editor_property('Item',item)
  if actor.get_class()==SC:
   c=actor.get_editor_property('Container');name=str(c.get_editor_property('DisplayName'))
   if name=='Pantry':c.set_editor_property('AllowedTags',tags(['Item.Category.Food','Item.Category.Water']))
   if name=='Medical storage':c.set_editor_property('AllowedTags',tags(['Item.Category.Medical']))
   if name=='Tool storage':c.set_editor_property('AllowedTags',tags(['Item.Category.Tool','Item.Category.Material','Item.Category.Automotive']))
 assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
 return {'definitions':len(categories),'map':'/Game/Maps/Gate4InventoryTest'}
result=configure();gc.collect();unreal.SystemLibrary.collect_garbage()
json.dump(result,open('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate4Validation/metadata.json','w'),indent=2)
unreal.log('GATE4_METADATA_SAVED');unreal.SystemLibrary.quit_editor()

