"""Project-side medical catalog; scoped references are released before PIE/map change."""
import unreal
def configure():
 tools=unreal.AssetToolsHelpers.get_asset_tools()
 factory=unreal.DataAssetFactory();factory.set_editor_property('DataAssetClass',unreal.RVItemDefinition)
 specs=[('Bandage',unreal.RVTreatmentKind.BANDAGE,4,2,1,False),
 ('Gauze',unreal.RVTreatmentKind.BANDAGE,5,2,.6,False),
 ('PressureDressing',unreal.RVTreatmentKind.PRESSURE_DRESSING,8,3,1,False),
 ('Antiseptic',unreal.RVTreatmentKind.ANTISEPTIC,5,3,0,False),
 ('Splint',unreal.RVTreatmentKind.SPLINT,10,3,0,False),
 ('BurnDressing',unreal.RVTreatmentKind.BURN_DRESSING,8,3,0,False),
 ('PainMedication',unreal.RVTreatmentKind.ANALGESIC,2,3,0,False),
 ('FirstAidKit',unreal.RVTreatmentKind.REVIVE,12,3,0,False),
 ('AdvancedKit',unreal.RVTreatmentKind.PRESSURE_DRESSING,6,3,1,True),
 ('DiagnosticBandage',unreal.RVTreatmentKind.BANDAGE,1,2,1,False)]
 for name,kind,duration,severity,reduction,station in specs:
  folder='/Game/Development/Medical' if name.startswith('Diagnostic') else '/Game/Medical'
  asset=unreal.load_asset(folder+'/DA_'+name) or tools.create_asset('DA_'+name,folder,unreal.RVItemDefinition,factory)
  asset.set_editor_property('CatalogId','Medical_'+name)
  asset.set_editor_property('DisplayName',unreal.Text(name))
  asset.set_editor_property('Category',unreal.RVItemDefinition.find_registered_tag('Item.Category.Medical'))
  asset.set_editor_property('WeightKg',.5 if kind==unreal.RVTreatmentKind.REVIVE else .1)
  asset.set_editor_property('VolumeLitres',1 if kind==unreal.RVTreatmentKind.REVIVE else .2)
  asset.set_editor_property('bStackable',True);asset.set_editor_property('MaxStackSize',10)
  asset.set_editor_property('bSupportsCondition',True)
  medical=asset.get_editor_property('Medical');medical.set_editor_property('bMedicalSupply',True)
  medical.set_editor_property('Treatment',kind);medical.set_editor_property('DurationSeconds',duration)
  medical.set_editor_property('MaximumSeverity',severity);medical.set_editor_property('BleedingReduction',reduction)
  medical.set_editor_property('bRequiresStation',station);medical.set_editor_property('bRequiresParked',station)
  asset.set_editor_property('Medical',medical)
  assert unreal.EditorAssetLibrary.save_loaded_asset(asset)
configure()
