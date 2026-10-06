import unreal,json,gc
B='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate5Refinement/'
def inspect():
 assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level('/Game/Maps/Gate5SurvivalTest')
 actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors();v=next(a for a in actors if isinstance(a,unreal.RVInteriorMotorhome))
 def vec(v):return [v.x,v.y,v.z]
 d={'collision':[],'visuals':[],'components':[],'storage':[]}
 for a in v.get_editor_property('InteriorCollision'):d['collision'].append({'name':str(a.name),'center':vec(a.center),'extent':vec(a.extent),'floor':a.get_editor_property('bPassengerFloor')})
 for a in v.get_editor_property('VisualParts'):
  d['visuals'].append({'name':str(a.name),'mesh':a.mesh.get_path_name(),'transform':str(a.transform),'bounds':str(a.mesh.get_bounds())})
 for c in v.get_components_by_class(unreal.PrimitiveComponent):d['components'].append({'name':c.get_name(),'loc':vec(c.get_editor_property('RelativeLocation')),'bounds':str(c.get_local_bounds()) if isinstance(c,unreal.StaticMeshComponent) else str(c.get_editor_property('BoxExtent')) if isinstance(c,unreal.BoxComponent) else '','collision':str(c.get_collision_enabled())})
 for a in actors:
  if isinstance(a,unreal.RVStoragePoint):d['storage'].append({'name':a.get_actor_label(),'display':str(a.get_editor_property('Container').get_editor_property('DisplayName')),'relative':vec(a.get_editor_property('RootComponent').get_editor_property('RelativeLocation'))})
 cls=unreal.EditorAssetLibrary.load_blueprint_class('/Game/Vehicles/Gate3/BP_Gate3GameMode');ch=unreal.get_default_object(unreal.get_default_object(cls).get_editor_property('DefaultPawnClass'));cap=ch.get_component_by_class(unreal.CapsuleComponent)
 d['character']={'radius':cap.get_unscaled_capsule_radius(),'halfheight':cap.get_unscaled_capsule_half_height()}
 arm=v.get_component_by_class(unreal.SpringArmComponent);d['camera']={n:str(arm.get_editor_property(n)) for n in ['TargetArmLength','SocketOffset','TargetOffset','RelativeLocation','RelativeRotation','ProbeSize','bDoCollisionTest']}
 json.dump(d,open(B+'baseline-layout.json','w'),indent=2)
inspect();gc.collect();unreal.SystemLibrary.collect_garbage();unreal.SystemLibrary.quit_editor()



