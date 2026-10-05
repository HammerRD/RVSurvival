import unreal,json
B='D:/GitHub/RVSurvival/RVSurvival/Saved/Gate3Validation/'
json.dump({'network':False},open(B+'case.json','w'))
exec(open(B+'play_settings.py').read(),{'__name__':'__main__'})
s=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.LevelEditorPlaySettings'));s.set_editor_property('RunUnderOneProcess',True);s.set_editor_property('AdditionalLaunchParameters','')
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
t=0;rows=[];sample=0
C=unreal.load_class(None,'/Script/RVSurvival.RVInteriorMotorhome')
def tick(dt):
 global t,sample
 t+=dt;sample+=dt
 if t>5 and sample>.1:
  sample=0
  worlds=sorted([w for w in unreal.ObjectIterator(unreal.World) if '/Game/Maps/UEDPIE_' in w.get_path_name() and w.get_name()=='Gate3MovingInteriorTest'],key=lambda w:w.get_path_name())
  if len(worlds)==2:
   vs=[unreal.GameplayStatics.get_all_actors_of_class(w,C)[0] for w in worlds];a,b=[v.get_actor_location() for v in vs]
   rows.append({'t':t,'server':[a.x,a.y,a.z],'client':[b.x,b.y,b.z],'error_cm':(a-b).length()})
 if t>20:
  json.dump({'samples':rows,'max_error_cm':max(r['error_cm'] for r in rows)},open(B+'parked_proxy.json','w'),indent=2)
  unreal.unregister_slate_post_tick_callback(h);unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play();unreal.log('GATE3_PARKED_DONE')
h=unreal.register_slate_post_tick_callback(tick)
