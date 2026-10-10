"""Project-side native material/PCG refinement; save/release before delayed quit."""
import unreal,time,gc,traceback,json,random,math,sys
from pathlib import Path
out=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate10Validation');started=time.time();phase=0;handle=None

def prepare():
 levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
 assert levels.load_level('/Game/Maps/WNY_PrototypeRegion')
 world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
 assert unreal.RVWorldContentLibrary.set_region_authoring_loaded(world,True)
 tools=unreal.AssetToolsHelpers.get_asset_tools();edit=unreal.MaterialEditingLibrary
 path='/Game/World/WNY/Materials';textures=[]
 for folder,name in [('MossyGrass','T_MossyGrass_01_BC'),('MossyGrass','T_MossyGrass_01_N'),('DriedGrassOnDampSoil','T_DriedGrassOnDampSoil_01_BC'),('DriedGrassOnDampSoil','T_DriedGrassOnDampSoil_01_N')]:
  target=path+'/Textures/'+name+'_WNY'
  texture=unreal.load_asset(target)
  if not texture:
   assert unreal.EditorAssetLibrary.duplicate_asset('/Game/Megascans/Surfaces/'+folder+'/'+name,target)
   texture=unreal.load_asset(target)
  texture.set_editor_property('virtual_texture_streaming',False)
  assert unreal.EditorAssetLibrary.save_loaded_asset(texture);textures.append(texture)
 m=unreal.load_asset(path+'/M_WoodlandField') or tools.create_asset('M_WoodlandField',path,unreal.Material,unreal.MaterialFactoryNew())
 edit.delete_all_material_expressions(m)
 def expr(cls):return edit.create_material_expression(m,cls)
 def link(src,dst,input_name='',output=''):
  names=list(edit.get_material_expression_input_names(dst))
  if input_name=='Coordinates' and 'UVs' in names:input_name='UVs'
  if input_name=='Position' and 'World Position' in names:input_name='World Position'
  if input_name=='Input' and 'None' in names:input_name=''
  assert edit.connect_material_expressions(src,output,dst,input_name),(dst.get_class().get_name(),input_name,names)
 def scalar(value):
  n=expr(unreal.MaterialExpressionConstant);n.set_editor_property('r',value);return n
 position=expr(unreal.MaterialExpressionWorldPosition)
 mask=expr(unreal.MaterialExpressionComponentMask);mask.set_editor_property('r',True);mask.set_editor_property('g',True);link(position,mask)
 uv=expr(unreal.MaterialExpressionMultiply);link(mask,uv,'A');link(scalar(1/300),uv,'B')
 samples=[]
 for i,texture in enumerate(textures):
  n=expr(unreal.MaterialExpressionTextureSample);n.set_editor_property('texture',texture)
  n.set_editor_property('sampler_type',unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL if i%2 else unreal.MaterialSamplerType.SAMPLERTYPE_COLOR)
  link(uv,n,'Coordinates');samples.append(n)
 noise=expr(unreal.MaterialExpressionNoise);noise.set_editor_property('scale',.00015);noise.set_editor_property('levels',2);noise.set_editor_property('quality',1);link(position,noise,'Position')
 blend=expr(unreal.MaterialExpressionClamp);link(noise,blend,'Input')
 for slot,a,b in [(unreal.MaterialProperty.MP_BASE_COLOR,samples[0],samples[2]),(unreal.MaterialProperty.MP_NORMAL,samples[1],samples[3])]:
  lerp=expr(unreal.MaterialExpressionLinearInterpolate);link(a,lerp,'A','RGB');link(b,lerp,'B','RGB');link(blend,lerp,'Alpha');assert edit.connect_material_property(lerp,'',slot)
 assert edit.connect_material_property(scalar(.93),'',unreal.MaterialProperty.MP_ROUGHNESS)
 edit.recompile_material(m);assert unreal.EditorAssetLibrary.save_loaded_asset(m)
 actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);all_actors=actors.get_all_level_actors()
 labels={a.get_actor_label():a for a in all_actors}
 for a in all_actors:
  if isinstance(a,unreal.LandscapeProxy):a.set_editor_property('landscape_material',m)
  if isinstance(a,unreal.TextRenderActor) and a.actor_has_tag('WNYLocationsMilestone'):a.set_actor_rotation(unreal.Rotator(yaw=-90),False)
 graphs=[unreal.load_asset('/Game/World/WNY/PCG/PCG_'+s) for s in ['Deciduous','Undergrowth','Rocks']];assert all(graphs)
 rng=random.Random(197710)
 locations=[(-130000,6500),(-60000,-8500),(0,47000),(75000,47000),(140000,8000)]
 count=0
 for index,x in enumerate(range(-165000,165001,15000)):
  for side in [-1,1]:
   px=x+rng.uniform(-1800,1800);py=side*rng.uniform(6500,10500)
   if any(abs(px-lx)<7500 and abs(py-ly)<7500 for lx,ly in locations):continue
   for layer,graph in enumerate(graphs):
    label='WNY roadside %02d %d %d'%(index,side,layer)
    patch=labels.get(label) or actors.spawn_actor_from_class(unreal.RVBiomePatch,unreal.Vector(px,py,0))
    patch.set_actor_label(label);patch.tags=['WNYRoadsideDressing']
    patch.get_editor_property('bounds').set_box_extent(unreal.Vector(5500,2500,20000))
    pcg=patch.get_editor_property('dressing');pcg.set_editor_property('seed',3500+index*17+side*3+layer);pcg.set_graph(graph);count+=1
 assert levels.save_current_level();assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
 # Newly created partition parents need their saved local actors loaded first.
 # Generate in regenerate_loaded_biome.py in the next clean editor session.
 (out/'environment-refinement-request.json').write_text(json.dumps({'roadside_patches':count,'material':path+'/M_WoodlandField','source_textures_unchanged':True,'generation':'separate saved-state generation required','visual_validation':'pending'},indent=2))

def save():
 world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
 stats=dict(unreal.RVWorldContentLibrary.get_dressing_stats(world))
 assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
 assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
 (out/'environment-refinement-saved.json').write_text(json.dumps({'saved':True,'stats':stats,'visual_validation':'pending'},indent=2))
 assert unreal.RVWorldContentLibrary.set_region_authoring_loaded(world,False)

def tick(delta):
 global phase,handle
 try:
  if phase==0 and time.time()-started>5:
   phase=10;prepare();phase=1
  elif phase==1 and time.time()-started>40:
   world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
   pending=dict(unreal.RVWorldContentLibrary.get_dressing_stats(world))['Pending'];world=None
   if pending==0:phase=10;save();phase=2
   elif time.time()-started>240:raise RuntimeError('PCG refinement timeout')
  elif phase==2:
   unreal.unregister_slate_post_tick_callback(handle);handle=None;phase=3;gc.collect();unreal.SystemLibrary.quit_editor()
 except Exception:
  (out/'environment-refinement-error.txt').write_text(traceback.format_exc())
  for key in ['last_traceback','last_value','last_type','last_exc']:
   if hasattr(sys,key):setattr(sys,key,None)
  phase=2;gc.collect()
handle=unreal.register_slate_post_tick_callback(tick)
