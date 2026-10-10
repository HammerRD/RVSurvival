"""Saved spline roads in bounded World Partition actors; editor-only construction."""
import unreal,math,json,gc,traceback
from pathlib import Path
root=Path('D:/GitHub/RVSurvival/RVSurvival');out=root/'Saved/Gate10Validation'

def height(x,y):
 return (1800*math.sin(x/65000)*math.cos(y/72000)+650*math.sin(y/25000))*max(0,min(1,(abs(y)-3000)/12000))

def material(name,color):
 path='/Game/World/WNY/Materials'
 existing=unreal.load_asset(path+'/'+name)
 if existing:return existing
 m=unreal.AssetToolsHelpers.get_asset_tools().create_asset(name,path,unreal.Material,unreal.MaterialFactoryNew())
 v=unreal.MaterialEditingLibrary.create_material_expression(m,unreal.MaterialExpressionConstant3Vector)
 v.set_editor_property('constant',unreal.LinearColor(*color))
 unreal.MaterialEditingLibrary.connect_material_property(v,'',unreal.MaterialProperty.MP_BASE_COLOR)
 r=unreal.MaterialEditingLibrary.create_material_expression(m,unreal.MaterialExpressionConstant)
 r.set_editor_property('r',.9);unreal.MaterialEditingLibrary.connect_material_property(r,'',unreal.MaterialProperty.MP_ROUGHNESS)
 unreal.MaterialEditingLibrary.recompile_material(m);unreal.EditorAssetLibrary.save_loaded_asset(m)
 return m

def run():
 levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
 assert levels.load_level('/Game/Maps/WNY_PrototypeRegion')
 actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
 if any(a.actor_has_tag('WNYRoadMilestone') for a in actors.get_all_level_actors()):
  raise RuntimeError('Road milestone already saved; inspect instead of recreating')
 asphalt=material('M_Asphalt',(.045,.05,.052,1));paint=material('M_CenterYellow',(.65,.42,.035,1))
 ground=material('M_RollingField',(.115,.16,.055,1))
 for a in actors.get_all_level_actors():
  if isinstance(a,unreal.LandscapeProxy):a.set_editor_property('landscape_material',ground)
 def road(points,label,width=900):
  origin=points[0]
  a=actors.spawn_actor_from_class(unreal.RVRegionRoad,unreal.Vector(origin[0],origin[1],height(*origin)+12))
  a.set_actor_label(label);a.tags=['WNYRoadMilestone','RoadExclusion']
  a.set_editor_property('asphalt',asphalt);a.set_editor_property('center_paint',paint);a.set_editor_property('width_cm',width)
  spline=a.get_editor_property('route');spline.clear_spline_points(False)
  for x,y in points:
   spline.add_spline_point(unreal.Vector(x-origin[0],y-origin[1],height(x,y)-height(*origin)),unreal.SplineCoordinateSpace.LOCAL,False)
  spline.update_spline();a.rebuild_road()
 total=0
 # Two-lane main state-highway corridor with broad shoulders added at authored locations.
 for index,x in enumerate(range(-170000,170000,10000)):
  pts=[(x+j*2000,0) for j in range(6)];road(pts,'NY county highway %02d'%index,1200);total+=10000
 controls=[(-80000,0),(-60000,22000),(0,45000),(75000,45000),(120000,18000),(130000,0)]
 # Sample native curved splines in adjacent short actor sections; shared endpoints remove gaps.
 for idx in range(len(controls)-1):
  start,end=controls[idx],controls[idx+1];distance=math.dist(start,end);steps=max(2,math.ceil(distance/2000))
  pts=[(start[0]+(end[0]-start[0])*j/steps,start[1]+(end[1]-start[1])*j/steps) for j in range(steps+1)]
  for j in range(0,steps,5):road(pts[j:min(j+6,steps+1)],'Rural loop %d-%d'%(idx,j),900)
  total+=distance
 # RV-sized access spurs: avoid narrow passenger-car parking assumptions.
 for label,x,y in [('Gas station',-130000,5500),('Garage',-60000,-7000),('Town',140000,6500)]:
  points=[(x,y*j/5) for j in range(6)];road(points,label+' approach',1000);total+=abs(y)
 assert levels.save_current_level() and unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
 return {'map':'/Game/Maps/WNY_PrototypeRegion','useful_route_km':total/100000,'main_width_m':12,'secondary_width_m':9,'saved':True,'driving_validation':'pending'}
try:(out/'road-foundation.json').write_text(json.dumps(run(),indent=2))
except Exception:(out/'road-foundation-error.txt').write_text(traceback.format_exc());traceback.print_exc()
finally:gc.collect();unreal.SystemLibrary.quit_editor()
