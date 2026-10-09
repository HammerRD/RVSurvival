"""Correct packed-mask texture compression in project copies, preserving imported source."""
import unreal
def configure():
 edit=unreal.MaterialEditingLibrary;folder='/Game/Combat/Gate9_5/Materials'
 for path in unreal.EditorAssetLibrary.list_assets(folder,True,False):
  material=unreal.load_asset(path)
  if not isinstance(material,unreal.Material):continue
  for expression in edit.get_material_expressions(material):
   if not isinstance(expression,unreal.MaterialExpressionTextureSample):continue
   texture=expression.get_editor_property('Texture')
   if not texture or 'OcclusionRoughnessMetallic' not in texture.get_name():continue
   copy_path='/Game/Combat/Gate9_5/Textures/'+texture.get_name().replace('OcclusionRoughnessMetallic','ORM')
   copy=unreal.load_asset(copy_path) or unreal.EditorAssetLibrary.duplicate_asset(texture.get_path_name().split('.')[0],copy_path)
   copy.modify();copy.set_editor_property('CompressionSettings',unreal.TextureCompressionSettings.TC_MASKS);copy.set_editor_property('SRGB',False);assert unreal.EditorAssetLibrary.save_loaded_asset(copy,False)
   material.modify();expression.modify();expression.set_editor_property('Texture',copy);expression.set_editor_property('SamplerType',unreal.MaterialSamplerType.SAMPLERTYPE_MASKS)
  edit.recompile_material(material);assert unreal.EditorAssetLibrary.save_loaded_asset(material,False)
