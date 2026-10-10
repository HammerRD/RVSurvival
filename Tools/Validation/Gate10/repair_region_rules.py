"""Audit saved defaults, persist new-region rules without touching accepted assets."""
import unreal,time,json,gc,traceback,sys
from pathlib import Path
out=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate10Validation');start=time.time();phase=0;handle=None
def audit_and_save():
 root='/Game/World/WNY';gs=unreal.load_asset(root+'/Gameplay/BP_WNYGameState');gm=unreal.load_asset(root+'/Gameplay/BP_WNYGameMode');gsc=unreal.get_default_object(gs.generated_class());gmc=unreal.get_default_object(gm.generated_class())
 before={'game_state':gmc.game_state_class.get_path_name(),'presets':[a.get_path_name() for a in gsc.difficulty_presets]}
 (out/'region-rules-before.json').write_text(json.dumps(before,indent=2))
 presets=[];details=[]
 for name in ['Relaxed','Standard','Harsh']:
  a=unreal.load_asset(root+'/Difficulty/DA_'+name);a.modify();rules=list(a.rules);updated=[]
  for r in rules:
   if str(r.id) in ['Loot','Population']:r.set_editor_property('bPreparationOnly',False);r.set_editor_property('Group','World')
   updated.append(r)
  a.set_editor_property('Rules',updated);assert unreal.EditorAssetLibrary.save_loaded_asset(a,False);presets.append(a);assert all(not r.preparation_only for r in a.rules if str(r.id) in ['Loot','Population']),name
  details.append({'asset':a.get_path_name(),'rules':[{'id':str(r.id),'future':r.preparation_only,'multiplier':r.multiplier} for r in a.rules if str(r.id) in ['Loot','Population']]})
 gs.modify();gsc.modify();gsc.set_editor_property('DifficultyPresets',presets);assert unreal.EditorAssetLibrary.save_loaded_asset(gs,False)
 gm.modify();gmc.modify();gmc.set_editor_property('GameStateClass',gs.generated_class());assert unreal.EditorAssetLibrary.save_loaded_asset(gm,False)
 assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
 (out/'region-rules-repair.json').write_text(json.dumps({'before':before,'saved':True,'after_game_state':gmc.game_state_class.get_path_name(),'presets':details},indent=2))
def tick(dt):
 global phase,handle
 if phase==0 and time.time()-start>5:
  phase=10
  try:audit_and_save()
  except Exception:(out/'region-rules-repair-error.txt').write_text(traceback.format_exc())
  for k in ['last_traceback','last_value','last_type','last_exc']:
   if hasattr(sys,k):setattr(sys,k,None)
  gc.collect();phase=1
 elif phase==1:unreal.unregister_slate_post_tick_callback(handle);handle=None;unreal.SystemLibrary.quit_editor()
handle=unreal.register_slate_post_tick_callback(tick)
