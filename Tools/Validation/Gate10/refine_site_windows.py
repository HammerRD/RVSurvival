"""Project-only facade apertures, preserving saved terrain and gameplay IDs."""
import unreal,time,json,gc,traceback,sys
from pathlib import Path
out=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate10Validation');started=time.time();phase=0;handle=None

def refine():
 levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
 assert levels.load_level('/Game/Maps/WNY_PrototypeRegion')
 world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
 assert unreal.RVWorldContentLibrary.set_region_authoring_loaded(world,True)
 actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
 by_name={a.get_actor_label():a for a in actors.get_all_level_actors()}
 assert not any(a.actor_has_tag('WNYWindowAperturesV1') for a in by_name.values()),'Already saved: inspect, do not repeat.'
 assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
 cube=unreal.load_asset('/Engine/BasicShapes/Cube');edit=unreal.MaterialEditingLibrary
 glass_path='/Game/World/WNY/Materials/M_GlassWindow'
 if not unreal.EditorAssetLibrary.does_asset_exist(glass_path):
  assert unreal.EditorAssetLibrary.duplicate_asset('/Game/World/WNY/Materials/M_Window',glass_path)
 glass=unreal.load_asset(glass_path);glass.set_editor_property('blend_mode',unreal.BlendMode.BLEND_TRANSLUCENT);glass.set_editor_property('two_sided',True)
 alpha=edit.create_material_expression(glass,unreal.MaterialExpressionConstant);alpha.set_editor_property('r',.22)
 edit.connect_material_property(alpha,'',unreal.MaterialProperty.MP_OPACITY)
 edit.set_material_usage(glass,unreal.MaterialUsage.MATUSAGE_INSTANCED_STATIC_MESHES);edit.recompile_material(glass)
 assert unreal.EditorAssetLibrary.save_loaded_asset(glass,False)
 trim=unreal.load_asset('/Game/World/WNY/Materials/M_CreamTrim');created=[];old=[]
 def block(name,position,size,material):
  a=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*position));a.set_actor_label(name);a.tags=['WNYWindowAperturesV1']
  c=a.static_mesh_component;c.set_static_mesh(cube);c.set_material(0,material);c.set_mobility(unreal.ComponentMobility.STATIC);c.set_collision_profile_name('BlockAll')
  a.set_actor_scale3d(unreal.Vector(*(v/100 for v in size)));created.append(name)
 for name in ['PINE CREEK FUEL','ERIE ROAD SERVICE','HAWTHORNE FARM','HAWTHORNE OUTBUILDING','MAPLE RUN CAMPGROUND','ROWLAND CROSSROADS','ROWLAND GENERAL STORE']:
  floor=by_name[name+' floor'];p=floor.get_actor_location();w=floor.get_actor_scale3d().x*100;d=floor.get_actor_scale3d().y*100;front_y=p.y-d/2
  for side in [-1,1]:
   pier=by_name[name+' front pier'+str(side)];material=pier.static_mesh_component.get_material(0)
   lo,hi=(-w/2,-90) if side<0 else (90,w/2);center=p.x+side*w*.32;window_lo=center-85;window_hi=center+85
   assert p.x+lo<window_lo<window_hi<p.x+hi
   pier.modify();pier.static_mesh_component.set_visibility(False);pier.set_actor_hidden_in_game(True);pier.static_mesh_component.set_collision_profile_name('NoCollision');old.append(pier.get_actor_label())
   # Actual openings: wall bands above/below the glass, stiles beside it.
   block(name+' window lower '+str(side),(p.x+(lo+hi)/2,front_y,p.z+56.25),(hi-lo,18,112.5),material)
   block(name+' window upper '+str(side),(p.x+(lo+hi)/2,front_y,p.z+263.75),(hi-lo,18,72.5),material)
   for index,(left,right) in enumerate([(p.x+lo,window_lo),(window_hi,p.x+hi)]):
    block(name+' window stile %d %d'%(side,index),((left+right)/2,front_y,p.z+170),(right-left,18,115),material)
   pane=by_name[name+' glazing'+str(side)];pane.modify();pane.static_mesh_component.set_material(0,glass)
   for edge in [-1,1]:block(name+' window jamb %d %d'%(side,edge),(center+edge*88,front_y-14,p.z+170),(8,10,125),trim)
   block(name+' window head '+str(side),(center,front_y-14,p.z+232.5),(188,10,10),trim)
 assert levels.save_current_level() and unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
 assert unreal.RVWorldContentLibrary.set_region_authoring_loaded(world,False)
 (out/'window-aperture-authoring.json').write_text(json.dumps({'saved':True,'project_only':True,'replaced_wall_piers':old,'new_wall_frame_parts':created,'visual_collision_and_HLOD_refresh':'pending'},indent=2))

def tick(dt):
 global phase,handle
 if phase==0 and time.time()-started>5:
  phase=10
  try:refine()
  except Exception:(out/'window-aperture-error.txt').write_text(traceback.format_exc())
  for k in ['last_traceback','last_value','last_type','last_exc']:
   if hasattr(sys,k):setattr(sys,k,None)
  gc.collect();phase=1
 elif phase==1:
  unreal.unregister_slate_post_tick_callback(handle);handle=None;phase=2;unreal.SystemLibrary.quit_editor()
handle=unreal.register_slate_post_tick_callback(tick)
