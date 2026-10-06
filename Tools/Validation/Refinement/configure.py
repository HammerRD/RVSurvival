import unreal,json,gc
B='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate5Refinement/'
PATH='/Game/Vehicles/Gate5Refinement/BP_ClassCRefinedMotorhome'
def configure():
 level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert level.load_level('/Game/Maps/Gate5SurvivalTest');assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
 es=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);old=next(a for a in es.get_all_level_actors() if isinstance(a,unreal.RVInteriorMotorhome))
 bp=unreal.load_asset(PATH) or unreal.EditorAssetLibrary.duplicate_asset('/Game/Vehicles/Gate3/BP_ClassCMotorhome',PATH)
 cls=unreal.EditorAssetLibrary.load_blueprint_class(PATH);c=unreal.get_default_object(cls)
 arm=c.get_component_by_class(unreal.SpringArmComponent)
 arm.set_editor_property('TargetArmLength',1400);arm.set_editor_property('RelativeLocation',unreal.Vector(-70,0,340));arm.set_editor_property('RelativeRotation',unreal.Rotator(pitch=-12));arm.set_editor_property('SocketOffset',unreal.Vector(0,0,60));arm.set_editor_property('ProbeSize',16);arm.set_editor_property('bDoCollisionTest',True);arm.set_editor_property('bEnableCameraLag',False);arm.set_editor_property('bInheritPitch',False);arm.set_editor_property('bInheritRoll',False)
 c.get_component_by_class(unreal.CameraComponent).set_editor_property('FieldOfView',85)
 boxes=list(c.get_editor_property('InteriorCollision'))
 for d in boxes:
  name=str(d.name)
  if name.startswith('EntryStep'):
   d.set_editor_property('bVisiblePrototype',True)
   # Compact visible tread rise; broad lower approach has no abrupt 38+ cm invisible lip.
   if name=='EntryStepLow':d.center=unreal.Vector(122,220,2);d.extent=unreal.Vector(48,30,2)
   if name=='EntryStepMid':d.center=unreal.Vector(122,170,22);d.extent=unreal.Vector(48,25,22)
  # Collision approximations must not protrude into the front entry's capsule corridor.
  if name=='Dinette':d.center=unreal.Vector(10,85,130);d.extent=unreal.Vector(65,30,43)
 # Match the purchased recessed stairwell instead of covering it with a full-height slab.
 floor=c.get_editor_property('InteriorFloor');floor.set_editor_property('RelativeLocation',unreal.Vector(77,-30,82.19));floor.set_editor_property('BoxExtent',unreal.Vector(153,87,5))
 for d in boxes:
  name=str(d.name)
  if name=='RightWallRear':d.center=unreal.Vector(-150,122,190);d.extent=unreal.Vector(205,5,105)
  if name=='RightWallFront':d.center=unreal.Vector(177.5,122,190);d.extent=unreal.Vector(47.5,5,105)
  if name=='Dinette':d.center=unreal.Vector(-10,85,130);d.extent=unreal.Vector(65,30,43)
  if name=='EntryStepLow':d.center=unreal.Vector(92.4,145,4);d.extent=unreal.Vector(36,24,4);d.set_editor_property('bVisiblePrototype',True)
  if name=='EntryStepMid':d.center=unreal.Vector(92.4,104,14.45);d.extent=unreal.Vector(36,16,14.45);d.set_editor_property('bVisiblePrototype',False)
  if name=='EntryStepHigh':d.center=unreal.Vector(92.4,72,28.85);d.extent=unreal.Vector(36,16,28.85);d.set_editor_property('bVisiblePrototype',False)
 def box(name,pos,ext,floor=False):
  d=unreal.RVInteriorCollision();d.name=name;d.center=unreal.Vector(*pos);d.extent=unreal.Vector(*ext);d.set_editor_property('bPassengerFloor',floor);return d
 names={str(d.name) for d in boxes}
 additions=[box('EntryFloorRear',(-10.5,87,82.19),(65.5,30,5),True),box('EntryFloorFront',(180,87,82.19),(50,30,5),True),box('OpenHouseDoor',(126.4,158.4,140.9),(3,34,112)),box('FrontFascia',(402,0,95),(5,101,77)),box('HoodTop',(314,0,156),(90,97,6)),box('CabExteriorLeft',(310,-101,85),(90,5,70)),box('CabExteriorRight',(310,101,85),(90,5,70))]
 boxes += [d for d in additions if str(d.name) not in names]
 c.set_editor_property('InteriorCollision',boxes)
 parts=list(c.get_editor_property('VisualParts'))
 for part in parts:
  if str(part.name) in ['Art_RV_Van_Door_Back','Art_RV_Glass_Door_Back']:
   t=part.transform;t.rotation=unreal.Rotator(yaw=-90).quaternion();part.transform=t
 c.set_editor_property('VisualParts',parts)
 c.set_editor_property('OutsideDoorLocation',unreal.Vector(92.4,148,140));c.set_editor_property('InsideDoorLocation',unreal.Vector(92.4,50,150))
 c.set_editor_property('bEnableStandingDoor',True);c.set_editor_property('bInteriorSeatAccess',True)
 # Full default capsule clearance, then native floor detection/reference-frame membership.
 c.set_editor_property('StandingEntryLocation',unreal.Vector(130,0,180))
 defs=[]
 labels=['Tools / repair supplies','Fluids / spare supplies','Spare parts','Camping equipment','General cargo','Bulky gear','Service / electrical supplies']
 volumes=[70,70,90,70,100,140,100];weights=[80,80,100,80,100,120,80]
 for idx in range(1,8):
  part=next(p for p in c.get_editor_property('VisualParts') if str(p.name)=='Art_RV_Van_Compartment_%02d'%idx)
  bounds=part.mesh.get_bounds();o=part.transform.transform_location(bounds.origin);q=unreal.Vector(o.x,-130 if o.y<0 else 130,o.z)
  d=unreal.RVExteriorCompartmentDefinition();d.set_editor_property('DoorPartName',part.name);d.set_editor_property('DisplayName',unreal.Text('%02d %s'%(idx,labels[idx-1])));d.position=q;d.query_extent=unreal.Vector(max(10,bounds.box_extent.x-4),3,max(10,bounds.box_extent.z-4));d.max_weight_kg=weights[idx-1];d.max_volume_litres=volumes[idx-1];defs.append(d)
 c.set_editor_property('ExteriorCompartments',defs)
 unreal.BlueprintEditorLibrary.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,False)
 t=old.get_actor_transform();new=es.spawn_actor_from_class(cls,t.translation,t.rotation.rotator());new.set_actor_label('ClassC_RV_Gate5_Refined')
 attached=[a for a in es.get_all_level_actors() if a.get_attach_parent_actor()==old]
 for a in attached:
  pos=a.get_actor_transform();a.attach_to_component(new.get_component_by_class(unreal.SkeletalMeshComponent),'',unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,False)
  if isinstance(a,unreal.RVStoragePoint):
   container=a.get_editor_property('Container');name=str(container.get_editor_property('DisplayName'))
   if name in ['Tool storage','Exterior compartment']:
    assert not container.get_items(),'Refuse to remove a nonempty saved cabinet';es.destroy_actor(a)
   elif name=='General cabinet':
    container.set_editor_property('DisplayName',unreal.Text('Personal supplies'));container.set_editor_property('MaxWeightKg',10);container.set_editor_property('MaxVolumeLitres',12)
 es.destroy_actor(old);new.refresh_configuration()
 assert level.save_current_level();assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
 data={'camera':{n:str(arm.get_editor_property(n)) for n in ['TargetArmLength','RelativeLocation','RelativeRotation','SocketOffset','ProbeSize']},'compartments':[{'door':str(d.door_part_name),'name':str(d.display_name),'position':str(d.position),'extent':str(d.query_extent),'kg':d.max_weight_kg,'litres':d.max_volume_litres} for d in defs],'map_actors':len(es.get_all_level_actors())}
 json.dump(data,open(B+'configured.json','w'),indent=2)
 # Read-only original mesh geometry, for the measured collision/aisle audit.
 pts=unreal.RVInteriorMotorhome.inspect_art_surfaces(unreal.load_asset('/Game/RV/Meshes/SM_RV_Interior'))
 json.dump([[p.x,p.y,p.z] for p in pts],open(B+'interior-horizontal-surfaces.json','w'))
configure();gc.collect();unreal.SystemLibrary.collect_garbage();unreal.SystemLibrary.quit_editor()
