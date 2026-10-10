"""Authored, enterable location shells and logical storage using existing gameplay."""
import unreal,math,json,gc,traceback,uuid
from pathlib import Path
root=Path('D:/GitHub/RVSurvival/RVSurvival');out=root/'Saved/Gate10Validation'

def terrain(x,y):return (1800*math.sin(x/65000)*math.cos(y/72000)+650*math.sin(y/25000))*max(0,min(1,(abs(y)-3000)/12000))

def build():
 levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert levels.load_level('/Game/Maps/WNY_PrototypeRegion')
 world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
 assert unreal.RVWorldContentLibrary.set_region_authoring_loaded(world,True)
 actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);tools=unreal.AssetToolsHelpers.get_asset_tools()
 existing={a.get_actor_label():a for a in actors.get_all_level_actors() if a.actor_has_tag('WNYLocationsMilestone')}
 def spawn(cls,name,pos,rotation=None):
  a=existing.get(name)
  if not a:
   a=actors.spawn_actor_from_class(cls,unreal.Vector(*pos),rotation or unreal.Rotator());a.set_actor_label(name);a.tags=['WNYLocationsMilestone'];existing[name]=a
  return a
 cube=unreal.load_asset('/Engine/BasicShapes/Cube');cylinder=unreal.load_asset('/Engine/BasicShapes/Cylinder')
 def mat(name,rgba):
  path='/Game/World/WNY/Materials';m=unreal.load_asset(path+'/'+name)
  if m:return m
  m=tools.create_asset(name,path,unreal.Material,unreal.MaterialFactoryNew())
  n=unreal.MaterialEditingLibrary.create_material_expression(m,unreal.MaterialExpressionConstant3Vector);n.set_editor_property('constant',unreal.LinearColor(*rgba))
  unreal.MaterialEditingLibrary.connect_material_property(n,'',unreal.MaterialProperty.MP_BASE_COLOR)
  rough=unreal.MaterialEditingLibrary.create_material_expression(m,unreal.MaterialExpressionConstant);rough.set_editor_property('r',.82)
  unreal.MaterialEditingLibrary.connect_material_property(rough,'',unreal.MaterialProperty.MP_ROUGHNESS)
  unreal.MaterialEditingLibrary.recompile_material(m);unreal.EditorAssetLibrary.save_loaded_asset(m);return m
 mats={k:mat('M_'+k,v) for k,v in {'WeatheredSiding':(.34,.37,.30,1),'CreamTrim':(.58,.55,.43,1),'RedBarn':(.32,.075,.045,1),'Concrete':(.22,.23,.21,1),'Roof':(.075,.09,.10,1),'Window':(.055,.10,.12,1),'Wood':(.23,.15,.085,1),'Metal':(.12,.14,.15,1),'PumpRed':(.42,.04,.025,1)}.items()}
 def block(name,pos,size,material='Wood',mesh=None,rotation=None):
  a=spawn(unreal.StaticMeshActor,name,pos,rotation)
  a.tags=['WNYLocationsMilestone'];c=a.static_mesh_component;c.set_static_mesh(mesh or cube);c.set_material(0,mats[material]);c.set_mobility(unreal.ComponentMobility.STATIC)
  a.set_actor_scale3d(unreal.Vector(*(v/100 for v in size)));return a
 def label(text,pos):
  a=spawn(unreal.TextRenderActor,'Sign '+text,pos,unreal.Rotator(0,-90,0))
  c=a.get_component_by_class(unreal.TextRenderComponent);c.set_text(text);c.set_world_size(38);c.set_horizontal_alignment(unreal.HorizTextAligment.EHTA_CENTER)
 def profile(name,paths):
  path='/Game/World/WNY/Loot';f=unreal.DataAssetFactory();f.set_editor_property('DataAssetClass',unreal.RVLootProfile)
  p=unreal.load_asset(path+'/DA_'+name) or tools.create_asset('DA_'+name,path,unreal.RVLootProfile,f)
  entries=[]
  for asset in paths:
   definition=unreal.load_asset(asset);assert definition,asset
   e=unreal.RVLootEntry();e.set_editor_property('definition',definition);e.set_editor_property('chance',.8)
   e.set_editor_property('minimum_quantity',1);e.set_editor_property('maximum_quantity',2 if definition.get_editor_property('bStackable') else 1);entries.append(e)
  p.set_editor_property('entries',entries);unreal.EditorAssetLibrary.save_loaded_asset(p);return p
 profiles={
 'Kitchen':profile('Kitchen',['/Game/Items/DA_Food','/Game/Items/DA_Water']),
 'Medical':profile('Medical',['/Game/Medical/DA_Bandage','/Game/Medical/DA_PainMedication','/Game/Medical/DA_Antiseptic']),
 'Garage':profile('Garage',['/Game/Mechanical/DA_MechanicTools','/Game/Mechanical/DA_CoolantPartial','/Game/Mechanical/DA_RadiatorPatch','/Game/Items/DA_Scrap']),
 'RoadSupplies':profile('RoadSupplies',['/Game/Items/DA_Water','/Game/Items/DA_Food','/Game/Resources/DA_FuelCanPartial','/Game/Items/DA_Tool']),
 'Camp':profile('Camp',['/Game/Items/DA_Water','/Game/Items/DA_Food','/Game/Medical/DA_Gauze','/Game/Items/DA_Tool'])}
 ids=[]
 def storage(name,pos,role,size=(100,55,95)):
  block(name+' furniture',pos,size,'Metal' if role=='Garage' else 'Wood')
  # Hidden query volume is flush with the approach-facing surface; real furniture remains visible.
  target=spawn(unreal.RVScavengeContainer,name,(pos[0],pos[1]-size[1]/2-4,pos[2]));mesh=target.get_component_by_class(unreal.StaticMeshComponent)
  mesh.set_visibility(False);mesh.set_relative_scale3d(unreal.Vector(size[0]/100,.12,size[2]/100))
  ident=str(uuid.uuid5(uuid.NAMESPACE_URL,'RVSurvival/WNY/'+name));guid,valid=unreal.GuidLibrary.parse_string_to_guid(ident);assert valid
  target.set_editor_property('container_id',guid);target.set_editor_property('loot_profile',profiles[role]);target.container.set_editor_property('display_name',name)
  ids.append({'name':name,'id':ident,'profile':role,'position':pos})
 def shell(name,x,y,w,d,wall='WeatheredSiding'):
  z=terrain(x,y)+30
  block(name+' foundation',(x,y,z-25),(w+100,d+100,50),'Concrete')
  block(name+' floor',(x,y,z),(w,d,12),'Wood')
  # Open 180 cm entrance, distinct window openings and trim, clear 300 cm interior height.
  block(name+' west wall',(x-w/2,y,z+150),(18,d,300),wall);block(name+' east wall',(x+w/2,y,z+150),(18,d,300),wall)
  block(name+' rear wall',(x,y+d/2,z+150),(w,18,300),wall)
  for side in [-1,1]:block(name+' front pier'+str(side),(x+side*(w/4+45),y-d/2,z+150),(w/2-90,18,300),wall)
  block(name+' entrance lintel',(x,y-d/2,z+270),(180,18,60),wall)
  for side in [-1,1]:
   block(name+' glazing'+str(side),(x+side*w*.32,y-d/2-12,z+170),(170,5,115),'Window')
   block(name+' sill'+str(side),(x+side*w*.32,y-d/2-16,z+105),(195,12,15),'CreamTrim')
  block(name+' roof',(x,y,z+315),(w+90,d+90,25),'Roof')
  block(name+' porch',(x,y-d/2-140,z-10),(w+80,260,20),'Concrete')
  block(name+' entry step',(x,y-d/2-290,z-25),(240,90,20),'Concrete')
  label(name,(x,y-d/2-22,z+270));return z
 locations=[('PINE CREEK FUEL',-130000,6500,1500,1200),('ERIE ROAD SERVICE',-60000,-8500,1800,1600),('HAWTHORNE FARM',0,47000,1100,1400),('MAPLE RUN CAMPGROUND',75000,47000,1000,900),('ROWLAND CROSSROADS',140000,8000,1400,1200)]
 for name,x,y,w,d in locations:
  z=shell(name,x,y,w,d,'RedBarn' if 'FARM' in name else 'WeatheredSiding')
  block(name+' RV parking',(x,y-d/2-2000,terrain(x,y-d/2-2000)+10),(3200,2600,18),'Concrete')
  if 'FUEL' in name:
   for col in [-1,1]:
    block('Fuel canopy post '+str(col),(x+col*700,y-2200,z+200),(30,30,400),'Metal')
    block('Inactive pump '+str(col),(x+col*700,y-2000,z+75),(70,70,150),'PumpRed')
   block('Fuel canopy',(x,y-2200,z+410),(2300,900,30),'CreamTrim')
   storage('Pine Creek packaged supplies',(x-400,y+300,z+55),'Kitchen');storage('Pine Creek first aid cabinet',(x+400,y+300,z+120),'Medical',(70,35,90))
   storage('Pine Creek road supplies',(x+400,y,z+55),'RoadSupplies')
  elif 'SERVICE' in name:
   storage('Erie Service tool chest',(x-450,y+400,z+55),'Garage',(140,65,110));storage('Erie Service parts shelf',(x+450,y+400,z+55),'Garage',(140,65,110))
   block('Garage service bench',(x,y+500,z+70),(260,90,25),'Metal')
  elif 'FARM' in name:
   storage('Hawthorne kitchen cupboard',(x-250,y+400,z+55),'Kitchen');storage('Hawthorne medicine cabinet',(x+280,y+400,z+130),'Medical',(70,35,90))
   block('Farm dining table',(x,y,z+75),(180,110,15));block('Farm dining bench',(x,y-110,z+45),(180,45,15))
   shell('HAWTHORNE OUTBUILDING',x+2000,y+800,900,1000,'RedBarn')
  elif 'CAMPGROUND' in name:
   storage('Maple Run camp office supplies',(x,y+200,z+55),'Camp')
   for i in range(5):
    cx=x+(i-2)*1600;cy=y+2200;cz=terrain(cx,cy)
    block('Campsite picnic tabletop '+str(i),(cx,cy,cz+80),(180,110,15));block('Campsite bench '+str(i),(cx,cy-100,cz+45),(180,40,12))
    for side in [-1,1]:block('Picnic support %d %d'%(i,side),(cx+side*65,cy,cz+40),(12,90,80))
    block('Fire ring '+str(i),(cx+350,cy,cz+18),(100,100,35),'Metal',cylinder)
  else:
   storage('Rowland diner pantry',(x-350,y+300,z+55),'Kitchen');storage('Rowland community supplies',(x+350,y+300,z+55),'RoadSupplies')
   shell('ROWLAND GENERAL STORE',x+2500,y+150,1200,1100)
  nav=spawn(unreal.NavMeshBoundsVolume,name+' navigation',(x,y,z+150));nav.set_actor_scale3d(unreal.Vector(32,32,10))
  assert levels.save_current_level() and unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
 # RV and spawn start preserve accepted content classes, with no vendor/old-map mutation.
 rvclass=unreal.EditorAssetLibrary.load_blueprint_class('/Game/Vehicles/Gate7/BP_ClassCMechanicalMotorhome');assert rvclass
 rv=spawn(rvclass,'WNY mobile survival base',(-160000,1600,190))
 start=spawn(unreal.PlayerStart,'WNY Player Start',(-160000,2350,150))
 for i,path in enumerate(['/Game/Combat/Gate9_5/Items/DA_M1911_45ACP','/Game/Combat/Gate9_5/Items/DA_45ACPMagazine','/Game/Combat/Gate9_5/Items/DA_PrototypeCrowbar','/Game/Items/DA_Water','/Game/Items/DA_Food']):
  definition=unreal.load_asset(path);assert definition,path
  pickup=spawn(unreal.RVWorldItem,'Starting supply '+str(definition.get_editor_property('DisplayName')),(-160400+i*100,2550,70))
  item=pickup.get_editor_property('Item');item.set_editor_property('Definition',definition);item.set_editor_property('Quantity',1);pickup.set_editor_property('Item',item)
 world.get_world_settings().set_editor_property('DefaultGameMode',unreal.EditorAssetLibrary.load_blueprint_class('/Game/Combat/Gate9_5/BP_Gate9_5GameMode'))
 assert levels.save_current_level() and unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
 return {'saved':True,'locations':[v[0] for v in locations],'containers':ids,'manual_navigation_and_visual_validation':'pending','asset_refinement':'rural cabin acquisition awaiting Epic sign-in'}
if __name__=='__main__':
 try:(out/'locations-foundation.json').write_text(json.dumps(build(),indent=2))
 except Exception:(out/'locations-foundation-error.txt').write_text(traceback.format_exc());traceback.print_exc()
 finally:gc.collect();unreal.SystemLibrary.quit_editor()


