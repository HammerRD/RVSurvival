"""Fresh-editor map-specific copy, scoped references, immutable vendor/prior content."""
import unreal, gc, json
from pathlib import Path
B=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate7Validation')
MAP='/Game/Maps/Gate7MechanicalTest'
BP='/Game/Vehicles/Gate7/BP_ClassCMechanicalMotorhome'

def copy_map():
    levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if unreal.EditorAssetLibrary.does_asset_exist(MAP):return
    assert levels.load_level('/Game/Maps/Gate6FuelElectricalTest')
    assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    assert unreal.EditorLoadingAndSavingUtils.save_map(unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world(),MAP)

def configure():
    levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    assert levels.load_level(MAP)
    assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    bp=unreal.load_asset(BP) or unreal.EditorAssetLibrary.duplicate_asset('/Game/Vehicles/Gate6/BP_ClassCSystemsMotorhome',BP)
    unreal.BlueprintEditorLibrary.reparent_blueprint(bp,unreal.RVMechanicalMotorhome)
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    cls=unreal.EditorAssetLibrary.load_blueprint_class(BP);cdo=unreal.get_default_object(cls)
    factory=unreal.DataAssetFactory();factory.set_editor_property('DataAssetClass',unreal.RVMechanicalProfile)
    profile=unreal.load_asset('/Game/Mechanical/DA_NormalMechanical') or unreal.AssetToolsHelpers.get_asset_tools().create_asset('DA_NormalMechanical','/Game/Mechanical',unreal.RVMechanicalProfile,factory)
    def req(tag,consume=True,quantity=1):
        r=unreal.RVRepairRequirement();r.set_editor_property('Tag',unreal.RVItemDefinition.find_registered_tag(tag));r.set_editor_property('DisplayName',unreal.Text({'Repair.Tool.Mechanic':'mechanic tool kit','Repair.Part.RadiatorPatch':'radiator patch kit','Repair.Part.RadiatorReplacement':'replacement radiator','Repair.Part.EngineService':'engine service parts'}[tag]));r.set_editor_property('Quantity',quantity);r.set_editor_property('bConsume',consume);return r
    repairs=[]
    for ident,label,duration,target,leak,temp,part in [('Patch','Roadside radiator patch',8,.65,.15,True,'Repair.Part.RadiatorPatch'),('ReplaceRadiator','Replace radiator',15,1,1,False,'Repair.Part.RadiatorReplacement'),('EngineService','Recoverable engine service',20,0,1,False,'Repair.Part.EngineService')]:
        r=unreal.RVRepairDefinition();r.set_editor_property('Id',ident);r.set_editor_property('DisplayName',unreal.Text(label));r.set_editor_property('DurationSeconds',duration);r.set_editor_property('RadiatorConditionTarget',target);r.set_editor_property('LeakMultiplier',leak);r.set_editor_property('bTemporary',temp)
        r.set_editor_property('bAffectsCooling',ident!='EngineService');r.set_editor_property('bAffectsEngine',ident=='EngineService');r.set_editor_property('EngineConditionTarget',.65 if ident=='EngineService' else 0)
        r.set_editor_property('Requirements',[req('Repair.Tool.Mechanic',False),req(part)]);repairs.append(r)
    profile.set_editor_property('Repairs',repairs);assert unreal.EditorAssetLibrary.save_loaded_asset(profile,False)
    cdo.get_editor_property('CoolingSystem').set_editor_property('Profile',profile)
    unreal.BlueprintEditorLibrary.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,False)
    es=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    old=next(a for a in es.get_all_level_actors() if isinstance(a,unreal.RVSystemsMotorhome))
    if not isinstance(old,unreal.RVMechanicalMotorhome):
        transform=old.get_actor_transform();new=es.spawn_actor_from_class(cls,transform.translation,transform.rotation.rotator());new.set_actor_label('ClassC_RV_Gate7_Mechanical')
        for a in es.get_all_level_actors():
            if a.get_attach_parent_actor()==old:a.attach_to_component(new.get_component_by_class(unreal.SkeletalMeshComponent),'',unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,False)
        es.destroy_actor(old);new.refresh_configuration()
    assets=[]
    specs=[('MechanicTools','Mechanic tool kit','Tool','Repair.Tool.Mechanic'),('RadiatorPatch','Radiator patch kit','Scrap','Repair.Part.RadiatorPatch'),('RadiatorReplacement','Replacement radiator','EnginePart','Repair.Part.RadiatorReplacement'),('EngineService','Engine service parts','EnginePart','Repair.Part.EngineService')]
    for name,label,source,tag in specs:
        path='/Game/Mechanical/DA_'+name
        asset=unreal.load_asset(path) or unreal.EditorAssetLibrary.duplicate_asset('/Game/Items/DA_'+source,path)
        asset.set_editor_property('CatalogId',name);asset.set_editor_property('DisplayName',unreal.Text(label));asset.set_editor_property('WeightKg',2);asset.set_editor_property('VolumeLitres',3)
        tags=asset.get_editor_property('Tags');tags=unreal.GameplayTagLibrary.make_gameplay_tag_container_from_array([unreal.RVItemDefinition.find_registered_tag('Item.Category.Tool' if name=='MechanicTools' else 'Item.Category.Automotive'),unreal.RVItemDefinition.find_registered_tag(tag)])
        asset.set_editor_property('Tags',tags);asset.set_editor_property('bStackable',name=='RadiatorPatch');asset.set_editor_property('MaxStackSize',10 if name=='RadiatorPatch' else 1);asset.set_editor_property('bSupportsCondition',True)
        assert unreal.EditorAssetLibrary.save_loaded_asset(asset,False);assets.append(asset)
    for name,amount in [('Full',5.),('Partial',1.75),('Empty',0.)]:
        path='/Game/Mechanical/DA_Coolant'+name;asset=unreal.load_asset(path) or unreal.EditorAssetLibrary.duplicate_asset('/Game/Resources/DA_FuelCanPartial',path)
        asset.set_editor_property('CatalogId','Coolant'+name);asset.set_editor_property('DisplayName',unreal.Text(name+' coolant container'));asset.set_editor_property('WeightKg',5);asset.set_editor_property('VolumeLitres',6)
        meta=asset.get_editor_property('Fuel');meta.set_editor_property('FuelType',unreal.RVItemDefinition.find_registered_tag('Resource.Fluid.Coolant'));meta.set_editor_property('CapacityLitres',5);meta.set_editor_property('InitialLitres',amount);asset.set_editor_property('Fuel',meta)
        assert unreal.EditorAssetLibrary.save_loaded_asset(asset,False);assets.append(asset)
    for index,asset in enumerate(assets):
        label='Gate7_'+str(asset.get_editor_property('CatalogId'))
        pickup=next((a for a in es.get_all_level_actors() if a.get_actor_label()==label),None) or es.spawn_actor_from_class(unreal.RVWorldItem,unreal.Vector(650+index*110,-1150,35))
        pickup.set_actor_label(label);item=pickup.get_editor_property('Item');item.set_editor_property('Definition',asset);item.set_editor_property('Condition',.83);item.set_editor_property('Quantity',3 if index==1 else 1);pickup.set_editor_property('Item',item)
    assert levels.save_current_level();assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    return {'map':MAP,'blueprint':BP,'profile':profile.get_path_name(),'actors':len(es.get_all_level_actors()),'definitions':[a.get_path_name() for a in assets]}

try:
    copy_map();gc.collect();unreal.SystemLibrary.collect_garbage()
    receipt=configure();(B/'configured.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
    gc.collect();unreal.SystemLibrary.collect_garbage();unreal.log('GATE7_ASSETS_SAVED')
except Exception:
    import traceback
    unreal.log_error(traceback.format_exc())
finally:unreal.SystemLibrary.quit_editor()
