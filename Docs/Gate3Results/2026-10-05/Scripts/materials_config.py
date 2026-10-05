import unreal,json
B='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate3Validation/'
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);level.load_level('/Game/Maps/Gate3MovingInteriorTest')
data={r['component']:r for r in json.load(open(B+'materials_audit.json'))}
bp=unreal.load_asset('/Game/Vehicles/Gate3/BP_ClassCMotorhome')
def configure(a,refresh=False):
 parts=list(a.get_editor_property('VisualParts'))
 for p in parts:
  n=str(p.get_editor_property('Name')).removeprefix('Art_');r=data[n]
  p.set_editor_property('Materials',[unreal.load_asset(m) if m else None for m in r['vendor_materials']])
  p.set_editor_property('bDisallowNanite',any(m and 'MI_RV_Glass' in m for m in r['vendor_materials']))
 a.set_editor_property('VisualParts',parts)
 for label in a.get_components_by_class(unreal.TextRenderComponent):
  if label.get_name()=='PrototypeLabel':label.set_visibility(False)
 if refresh:a.refresh_configuration()
configure(unreal.get_default_object(bp.generated_class()))
unreal.BlueprintEditorLibrary.compile_blueprint(bp);unreal.EditorAssetLibrary.save_loaded_asset(bp,False)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
rv=next(a for a in actors.get_all_level_actors() if a.get_class()==bp.generated_class());configure(rv,True)
assert level.save_current_level()
rows=[]
for co in rv.get_components_by_class(unreal.StaticMeshComponent):
 if not co.get_name().startswith('Art_'):continue
 n=co.get_name().removeprefix('Art_');materials=[co.get_material(i).get_path_name() if co.get_material(i) else None for i in range(co.get_num_materials())]
 rows.append({'part':co.get_name(),'materials':materials,'matches_vendor':materials==data[n]['vendor_materials'],'disallow_nanite':co.get_editor_property('bDisallowNanite'),'collision':str(co.get_collision_enabled())})
json.dump(rows,open(B+'materials_configured.json','w'),indent=2)
assert len(rows)==54 and all(r['matches_vendor'] for r in rows)
unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings')).set_editor_property('bThrottleCPUWhenNotForeground',False)
exec(open(B+'jobs.py').read(),{'__name__':'__main__'})
unreal.log('GATE3_MATERIALS_CONFIGURED '+str(len(rows)))
