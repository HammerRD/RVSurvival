import unreal,json
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
changes=[]
starts=[]
for a in actors:
 if a.get_actor_label().startswith('Gate2_Reference_'):
  p=a.get_actor_location();p.y=5000 if p.y>0 else -5000;a.set_actor_location(p,False,False);changes.append(a.get_actor_label())
 if isinstance(a,unreal.PlayerStart):starts.append(a)
for i,a in enumerate(starts):a.set_actor_location(unreal.Vector(100,-430 if i==0 else 430,100),False,False)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
json.dump({'markers':changes,'starts':len(starts)},open('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate3Validation/lane_config.json','w'),indent=2)
