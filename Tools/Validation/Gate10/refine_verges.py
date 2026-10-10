"""Native saved PCG verge bounds and project-side visual refinement only."""
import unreal,time,gc,traceback,json,random,sys,math
from pathlib import Path
out=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate10Validation');started=time.time();phase=0;handle=None
def terrain(x,y):return (1800*math.sin(x/65000)*math.cos(y/72000)+650*math.sin(y/25000))*max(0,min(1,(abs(y)-3000)/12000))
def prepare():
 levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert levels.load_level('/Game/Maps/WNY_PrototypeRegion')
 world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert unreal.RVWorldContentLibrary.set_region_authoring_loaded(world,True)
 actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);loaded=actors.get_all_level_actors();labels={a.get_actor_label():a for a in loaded}
 edit=unreal.MaterialEditingLibrary;m=unreal.load_asset('/Game/World/WNY/Materials/M_WoodlandField');assert m
 # Select the first color lerp created by the prior script. Normal remains untouched.
 lerps=[e for e in edit.get_material_expressions(m) if isinstance(e,unreal.MaterialExpressionLinearInterpolate)]
 color=lerps[0]
 tint=next((e for e in edit.get_material_expressions(m) if isinstance(e,unreal.MaterialExpressionConstant3Vector)),None)
 if not tint:
  tint=edit.create_material_expression(m,unreal.MaterialExpressionConstant3Vector)
  multiply=edit.create_material_expression(m,unreal.MaterialExpressionMultiply)
  assert edit.connect_material_expressions(color,'',multiply,'A');assert edit.connect_material_expressions(tint,'',multiply,'B');assert edit.connect_material_property(multiply,'',unreal.MaterialProperty.MP_BASE_COLOR)
 tint.set_editor_property('constant',unreal.LinearColor(.48,.74,.39,1));edit.recompile_material(m);assert unreal.EditorAssetLibrary.save_loaded_asset(m)
 meshes=[unreal.load_asset('/Game/Megascans/3D_Plants/'+folder+'/SM_'+folder+'_01') for folder in ['CloverVarieties','GroundCover','Elderberry']];assert all(meshes)
 grass=unreal.RVWorldContentLibrary.create_biome_graph('/Game/World/WNY/PCG/PCG_FieldVerge',meshes[:2],.075,False)
 shrub=unreal.RVWorldContentLibrary.create_biome_graph('/Game/World/WNY/PCG/PCG_Hedgerow',[meshes[2]],.002,False)
 for g in [grass,shrub]:assert unreal.EditorAssetLibrary.save_loaded_asset(g)
 rng=random.Random(197711);count=0
 sites=[(-130000,6500),(-60000,-8500),(0,47000),(75000,47000),(140000,8000)]
 for index,x in enumerate(range(-165000,165001,15000)):
  for side in [-1,1]:
   y=side*2500
   if any(abs(x-sx)<5000 and abs(y-sy)<5000 for sx,sy in sites):continue
   for layer,graph in enumerate([grass,shrub]):
    name='WNY verge %02d %d %d'%(index,side,layer)
    a=labels.get(name) or actors.spawn_actor_from_class(unreal.RVBiomePatch,unreal.Vector(x,y,0));a.set_actor_label(name);a.tags=['WNYVergeMilestone']
    a.get_editor_property('bounds').set_box_extent(unreal.Vector(6000,900 if layer==0 else 400,20000))
    c=a.get_editor_property('dressing');c.set_graph(graph);c.set_editor_property('seed',4800+index*19+side*3+layer);count+=1
 # Native ground starts remain safe if the tagged mobile base is unavailable.
 rv=labels['WNY mobile survival base'];r=rv.get_actor_location()
 start=labels['WNY Player Start'];start.set_actor_location(r+unreal.Vector(0,750,-40),False,False);start.set_actor_rotation(unreal.Rotator(yaw=180),False)
 second=labels.get('WNY Second Player Start') or actors.spawn_actor_from_class(unreal.PlayerStart,r+unreal.Vector(-220,750,-40))
 second.set_actor_label('WNY Second Player Start');second.tags=['WNYLocationsMilestone'];second.modify();second.set_editor_property('bIsSpatiallyLoaded',False)
 cube=unreal.load_asset('/Engine/BasicShapes/Cube');roof_material=unreal.load_asset('/Game/World/WNY/Materials/M_Roof');trim=unreal.load_asset('/Game/World/WNY/Materials/M_CreamTrim')
 for name,x,y,w,d in [('HAWTHORNE FARM',0,47000,1100,1400),('MAPLE RUN CAMPGROUND',75000,47000,1000,900)]:
  base=terrain(x,y)+30;rise=math.tan(math.radians(25))*(w/4)
  for side in [-1,1]:
   label=name+' pitched roof '+str(side);a=labels.get(label) or actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(x+side*w/4,y,base+315+rise),unreal.Rotator(pitch=side*25))
   a.set_actor_label(label);a.tags=['WNYVergeMilestone'];a.set_actor_scale3d(unreal.Vector((w/2+65)/math.cos(math.radians(25))/100,(d+110)/100,.20))
   c=a.static_mesh_component;c.set_static_mesh(cube);c.set_material(0,roof_material);c.set_collision_profile_name('BlockAll')
  for row in range(5):
   width=w*(1-(row+.5)/5);height=rise*2/5
   for side in [-1,1]:
    label=name+' gable %d %d'%(row,side);a=labels.get(label) or actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(x,y+side*d/2,base+315+height*(row+.5)))
    a.set_actor_label(label);a.tags=['WNYVergeMilestone'];a.set_actor_scale3d(unreal.Vector(width/100,.18,height/100));c=a.static_mesh_component;c.set_static_mesh(cube);c.set_material(0,trim)
 assert unreal.EditorLoadingAndSavingUtils.save_map(world,'/Game/Maps/WNY_PrototypeRegion');assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
 assert unreal.RVWorldContentLibrary.set_region_authoring_loaded(world,False)
 (out/'verge-authoring.json').write_text(json.dumps({'saved':True,'verge_patches':count,'generation':'next clean session with saved partitions loaded','start':'safe ground fallback; native regional arrival uses current RV aisle','visual_validation':'pending'},indent=2))
def tick(dt):
 global phase,handle
 if phase==0 and time.time()-started>5:
  phase=10
  try:prepare()
  except Exception:
   (out/'verge-authoring-error.txt').write_text(traceback.format_exc())
   for k in ['last_traceback','last_value','last_type','last_exc']:
    if hasattr(sys,k):setattr(sys,k,None)
  gc.collect();phase=1
 elif phase==1:
  phase=2;unreal.unregister_slate_post_tick_callback(handle);handle=None;gc.collect();unreal.SystemLibrary.quit_editor()
handle=unreal.register_slate_post_tick_callback(tick)
