"""Owner-only pre-skinned head/neck masking; keep source material graphs and arms."""
import unreal
def create_owner_materials(mesh,folder):
 materials=[];parents={};edit=unreal.MaterialEditingLibrary
 def expression(material,kind):return edit.create_material_expression(material,kind)
 def connect(a,b,pin=''):assert edit.connect_material_expressions(a,'',b,pin)
 for index,slot in enumerate(mesh.get_editor_property('Materials')):
  source=slot.get_editor_property('MaterialInterface');assert source
  parent=source
  while isinstance(parent,unreal.MaterialInstance):parent=parent.get_editor_property('Parent')
  key=parent.get_path_name()
  if key not in parents:
   path=folder+'/M_Owner_'+parent.get_name();material=unreal.load_asset(path) or unreal.EditorAssetLibrary.duplicate_asset(key.split('.')[0],path);material.modify();material.set_editor_property('BlendMode',unreal.BlendMode.BLEND_MASKED)
   # Build once; editable scalar bounds are independent of animation pitch.
   if not any(isinstance(e,unreal.MaterialExpressionScalarParameter) and str(e.get_editor_property('ParameterName'))=='OwnerNeckMinZ' for e in edit.get_material_expressions(material)):
    position=expression(material,unreal.MaterialExpressionPreSkinnedPosition)
    one=expression(material,unreal.MaterialExpressionConstant);one.set_editor_property('R',1)
    zero=expression(material,unreal.MaterialExpressionConstant);zero.set_editor_property('R',0)
    conditions=[]
    for axis,name,value,greater in [(2,'OwnerNeckMinZ',140,True),(0,'OwnerHeadRadiusX',15,False),(1,'OwnerHeadRadiusY',20,False)]:
     mask=expression(material,unreal.MaterialExpressionComponentMask);mask.set_editor_property('R',axis==0);mask.set_editor_property('G',axis==1);mask.set_editor_property('B',axis==2);connect(position,mask)
     coordinate=mask
     if not greater:coordinate=expression(material,unreal.MaterialExpressionAbs);connect(mask,coordinate)
     threshold=expression(material,unreal.MaterialExpressionScalarParameter);threshold.set_editor_property('ParameterName',name);threshold.set_editor_property('DefaultValue',value)
     test=expression(material,unreal.MaterialExpressionIf);names=edit.get_material_expression_input_names(test)
     connect(coordinate,test,str(names[0]));connect(threshold,test,str(names[1]));connect(one if greater else zero,test,str(names[2]));connect(one,test,str(names[3]));connect(zero if greater else one,test,str(names[4]));conditions.append(test)
    product=expression(material,unreal.MaterialExpressionMultiply);connect(conditions[0],product,'A');connect(conditions[1],product,'B')
    total=expression(material,unreal.MaterialExpressionMultiply);connect(product,total,'A');connect(conditions[2],total,'B')
    visible=expression(material,unreal.MaterialExpressionOneMinus);connect(total,visible);assert edit.connect_material_property(visible,'',unreal.MaterialProperty.MP_OPACITY_MASK)
   expressions=edit.get_material_expressions(material)
   position=next(e for e in expressions if isinstance(e,unreal.MaterialExpressionPreSkinnedPosition))
   interpolator=next((e for e in expressions if isinstance(e,unreal.MaterialExpressionVertexInterpolator)),None) or expression(material,unreal.MaterialExpressionVertexInterpolator)
   connect(position,interpolator)
   for e in expressions:
    if isinstance(e,unreal.MaterialExpressionComponentMask):
     # Only replace the three masks authored for the owner head region.
     source_node=edit.get_inputs_for_material_expression(material,e)
     if position in source_node:connect(interpolator,e)
   edit.recompile_material(material);assert unreal.EditorAssetLibrary.save_loaded_asset(material,False);parents[key]=material
  if isinstance(source,unreal.MaterialInstanceConstant):
   path=folder+'/MI_Owner_'+str(index);instance=unreal.load_asset(path) or unreal.EditorAssetLibrary.duplicate_asset(source.get_path_name().split('.')[0],path);instance.modify();edit.set_material_instance_parent(instance,parents[key]);assert unreal.EditorAssetLibrary.save_loaded_asset(instance,False);materials.append(instance)
  else:materials.append(parents[key])
 return materials
