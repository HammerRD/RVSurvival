"""Authored static roadside choices with existing Epic vehicle art and finite loot."""
import unreal,time,gc,traceback,json,uuid,math,sys
from pathlib import Path
out=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate10Validation');started=time.time();phase=0;handle=None
def terrain(x,y):return (1800*math.sin(x/65000)*math.cos(y/72000)+650*math.sin(y/25000))*max(0,min(1,(abs(y)-3000)/12000))

def build():
 levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert levels.load_level('/Game/Maps/WNY_PrototypeRegion')
 world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert unreal.RVWorldContentLibrary.set_region_authoring_loaded(world,True)
 actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
 existing={a.get_actor_label():a for a in actors.get_all_level_actors() if a.actor_has_tag('WNYRoadsideMilestone')}
 def spawn(cls,name,pos,rotation=None):
  a=existing.get(name) or actors.spawn_actor_from_class(cls,unreal.Vector(*pos),rotation or unreal.Rotator())
  a.set_actor_label(name);a.tags=['WNYRoadsideMilestone'];existing[name]=a;return a
 cube=unreal.load_asset('/Engine/BasicShapes/Cube');metal=unreal.load_asset('/Game/World/WNY/Materials/M_Metal');wood=unreal.load_asset('/Game/World/WNY/Materials/M_Wood')
 def box(name,pos,size,material=metal,rotation=None,hidden=False):
  a=spawn(unreal.StaticMeshActor,name,pos,rotation);a.set_actor_scale3d(unreal.Vector(*(s/100 for s in size)))
  c=a.static_mesh_component;c.set_static_mesh(cube);c.set_material(0,material);c.set_mobility(unreal.ComponentMobility.STATIC);c.set_collision_profile_name('BlockAll');c.set_visibility(not hidden);a.set_actor_hidden_in_game(hidden);return a
 vehicle_mesh=unreal.load_asset('/Game/Vehicles/OffroadCar/SKM_Offroad');assert vehicle_mesh
 entries=[]
 # Static abandoned trail/utility vehicles reuse existing Epic template content.
 # Simplified project collision, no drivable pawn/Chaos duplication or vendor edits.
 for index,(x,y,yaw) in enumerate([(-129000,3400,12),(-61600,-11000,170),(73500,49200,35),(35000,-150,65),(35350,100,-70)]):
  z=terrain(x,y)+18;rotation=unreal.Rotator(yaw=yaw)
  a=spawn(unreal.SkeletalMeshActor,'Abandoned trail vehicle '+str(index),(x,y,z),rotation)
  c=a.get_component_by_class(unreal.SkeletalMeshComponent);c.set_skeletal_mesh_asset(vehicle_mesh);c.set_mobility(unreal.ComponentMobility.STATIC);c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
  box('Abandoned vehicle body collision '+str(index),(x,y,z+85),(360,190,150),rotation=rotation,hidden=True)
  # Separate trunk query point at rear, clear of vehicle's simplified body.
  rear=a.get_actor_transform().transform_location(unreal.Vector(-240,0,95))
  target=spawn(unreal.RVScavengeContainer,'Trail vehicle cargo '+str(index),(rear.x,rear.y,rear.z),rotation)
  mesh=target.get_component_by_class(unreal.StaticMeshComponent);mesh.set_visibility(False);mesh.set_relative_scale3d(unreal.Vector(.25,.8,.6))
  ident=str(uuid.uuid5(uuid.NAMESPACE_URL,'RVSurvival/WNY/AbandonedVehicle/'+str(index)));guid,valid=unreal.GuidLibrary.parse_string_to_guid(ident);assert valid
  target.set_editor_property('container_id',guid);target.set_editor_property('loot_profile',unreal.load_asset('/Game/World/WNY/Loot/DA_RoadSupplies'))
  target.container.set_editor_property('display_name','Abandoned trail vehicle cargo')
  entries.append({'label':a.get_actor_label(),'container_id':ident,'position':[x,y,z]})
 # Partial lane obstruction offers slow bypass or the previously authored rural loop.
 for i in range(3):box('Road obstruction barrier '+str(i),(34900+i*180,320,60),(120,45,85),wood,unreal.Rotator(yaw=20))
 sign=spawn(unreal.TextRenderActor,'Road choice warning',(31000,900,170),unreal.Rotator(yaw=-90))
 text=sign.get_component_by_class(unreal.TextRenderComponent);text.set_text('OBSTRUCTION AHEAD\nRURAL LOOP / SLOW BYPASS');text.set_world_size(30)
 # Sparse telephone poles and fence edges, avoiding RV lane and authored entrances.
 for i,x in enumerate(range(-160000,160001,12000)):
  y=-1900;z=terrain(x,y)
  box('Utility pole '+str(i),(x,y,z+475),(24,24,950),wood)
  box('Utility crossarm '+str(i),(x,y,z+855),(180,18,18),wood)
  if not (-70000<x<-50000):
   for j in range(4):
    fx=x+j*900;fz=terrain(fx,-3500)
    box('Field fence post %d %d'%(i,j),(fx,-3500,fz+65),(14,14,130),wood)
    if j<3:
     for rail in [45,95]:box('Field fence rail %d %d %d'%(i,j,rail),(fx+450,-3500,fz+rail),(900,10,10),wood)
 assert levels.save_current_level();assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
 (out/'roadside-authored.json').write_text(json.dumps({'saved':True,'abandoned_vehicles':entries,'visual_and_player_collision_validation':'pending','source':'existing Epic vehicle template; original assets unchanged'},indent=2))
 assert unreal.RVWorldContentLibrary.set_region_authoring_loaded(world,False)

def tick(delta):
 global phase,handle
 if phase==0 and time.time()-started>5:
  phase=10
  try:build()
  except Exception:
   (out/'roadside-authoring-error.txt').write_text(traceback.format_exc())
   for key in ['last_traceback','last_value','last_type','last_exc']:
    if hasattr(sys,key):setattr(sys,key,None)
  gc.collect();phase=1
 elif phase==1:
  unreal.unregister_slate_post_tick_callback(handle);handle=None;phase=2;gc.collect();unreal.SystemLibrary.quit_editor()
handle=unreal.register_slate_post_tick_callback(tick)
