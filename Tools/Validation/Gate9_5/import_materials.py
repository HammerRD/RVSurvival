"""Import free source textures and configure project-side materials, preserving original files."""
import unreal,json,traceback,gc
from pathlib import Path
root=Path('D:/GitHub/RVSurvival/RVSurvival');out=root/'Docs/Gate9_5Results'
def run():
 tools=unreal.AssetToolsHelpers.get_asset_tools();results=[]
 for meshname,groups in [('NonRigged_M1911',['Barrel','Frame','Grip','Slide']),('NonRigged_M1911_Magazine',['Mag'])]:
  mesh=unreal.load_asset('/Game/ThirdParty/Xeradev/M1911/'+meshname);slots=list(mesh.get_editor_property('StaticMaterials'));materials={}
  for group in groups:
   materialpath='/Game/Combat/Gate9_5/Materials/M_M1911_'+group
   mat=unreal.load_asset(materialpath)
   if not mat:
    mat=tools.create_asset('M_M1911_'+group,'/Game/Combat/Gate9_5/Materials',unreal.Material,unreal.MaterialFactoryNew())
    for suffix in ['BaseColor','Normal','OcclusionRoughnessMetallic']:
     files=list((root/'Saved/Gate9_5Assets/M1911/Textures').rglob('M1911_low_'+group+'_'+suffix+'.png'));assert len(files)==1,(group,suffix)
     name='T_M1911_'+group+'_'+suffix;path='/Game/ThirdParty/Xeradev/M1911/Textures/'+name;texture=unreal.load_asset(path)
     if not texture:
      task=unreal.AssetImportTask();task.filename=str(files[0]);task.destination_path='/Game/ThirdParty/Xeradev/M1911/Textures';task.destination_name=name;task.automated=True;task.save=True;tools.import_asset_tasks([task]);texture=unreal.load_asset(path)
     texture.modify()
     if suffix!='BaseColor':texture.set_editor_property('SRGB',False)
     if suffix=='Normal':texture.set_editor_property('CompressionSettings',unreal.TextureCompressionSettings.TC_NORMALMAP)
     unreal.EditorAssetLibrary.save_loaded_asset(texture,False)
     node=unreal.MaterialEditingLibrary.create_material_expression(mat,unreal.MaterialExpressionTextureSample);node.set_editor_property('Texture',texture)
     if suffix=='Normal':node.set_editor_property('SamplerType',unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
     if suffix=='OcclusionRoughnessMetallic':node.set_editor_property('SamplerType',unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR)
     if suffix=='BaseColor':unreal.MaterialEditingLibrary.connect_material_property(node,'RGB',unreal.MaterialProperty.MP_BASE_COLOR)
     elif suffix=='Normal':unreal.MaterialEditingLibrary.connect_material_property(node,'RGB',unreal.MaterialProperty.MP_NORMAL)
     else:
      for channel,prop in [('R',unreal.MaterialProperty.MP_AMBIENT_OCCLUSION),('G',unreal.MaterialProperty.MP_ROUGHNESS),('B',unreal.MaterialProperty.MP_METALLIC)]:unreal.MaterialEditingLibrary.connect_material_property(node,channel,prop)
    unreal.MaterialEditingLibrary.recompile_material(mat);assert unreal.EditorAssetLibrary.save_loaded_asset(mat,False)
   materials[group]=mat
  for index,slot in enumerate(slots):
   label=str(slot.get_editor_property('ImportedMaterialSlotName'))+' '+str(slot.get_editor_property('MaterialSlotName'));group=next((g for g in groups if g.lower() in label.lower()),groups[0] if len(groups)==1 else None)
   if group:mesh.set_material(index,materials[group])
   results.append({'mesh':meshname,'slot':index,'label':label,'material':group})
  assert unreal.EditorAssetLibrary.save_loaded_asset(mesh,False)
 return results
try:(out/'materials.json').write_text(json.dumps(run(),indent=2))
except Exception:(out/'materials-error.txt').write_text(traceback.format_exc());traceback.print_exc()
finally:gc.collect();unreal.SystemLibrary.quit_editor()
