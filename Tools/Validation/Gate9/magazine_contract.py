"""Transient wrong-caliber definition; real owned reload RPC and native inventory guards."""
import unreal,time,json,traceback
from pathlib import Path
out=Path('D:/GitHub/RVSurvival/RVSurvival/Docs/Gate9Results');results=[];events=[];index=0
w=next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='Gate9CombatInfectedTest' and unreal.GameplayStatics.get_player_controller(w,0) and unreal.GameplayStatics.get_player_controller(w,0).get_controlled_pawn())
pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn();inv=p.get_component_by_class(unreal.RVInventoryComponent);combat=p.get_component_by_class(unreal.RVCombatComponent)
def check(n,ok,d=''):results.append({'case':n,'pass':bool(ok),'detail':str(d)})
def add(definition):
 item=unreal.RVItemInstance();item.set_editor_property('Id',unreal.GuidLibrary.new_guid());item.set_editor_property('Definition',definition);error=inv.add_authority(item);assert not error,error;return item.id
gun=add(unreal.load_asset('/Game/Combat/Items/DA_9mmHandgun'));good=add(unreal.load_asset('/Game/Combat/Items/DA_9mmMagazine'))
wrong=unreal.load_asset('/Game/Combat/Tests/DA_IncompatibleMagazine');wrong_id=add(wrong)
def at(t,f):events.append((t,f))
def key(k,on):unreal.RVInteriorMotorhome.dispatch_development_key(pc,k,on)
def tap(t,k):at(t,lambda:key(k,True));at(t+.12,lambda:key(k,False))
def weapon():return next(i for i in inv.get_items() if unreal.GuidLibrary.equal_equal_guid_guid(i.id,gun))
tap(.2,'Four');tap(.8,'R')
at(3.2,lambda:check('compatible magazine loaded',combat.get_loaded_rounds()==15))
at(3.5,lambda:combat.debug_request_reload(wrong_id,weapon().combat_revision))
at(6,lambda:check('wrong caliber rejected without changing loaded rounds',combat.get_loaded_rounds()==15 and 'Compatible' in combat.feedback,combat.feedback))
def invalid_records():
 item=unreal.RVItemInstance();item.set_editor_property('Id',gun);item.set_editor_property('Definition',unreal.load_asset('/Game/Combat/Items/DA_9mmHandgun'))
 check('duplicate GUID admission rejected',bool(inv.can_accept(item)) and inv.add_authority(item) is None)
 item.set_editor_property('Id',unreal.GuidLibrary.new_guid());item.set_editor_property('Quantity',2);check('combat item cannot stack',bool(inv.can_accept(item)) and inv.add_authority(item) is None)
 item.set_editor_property('Quantity',1);item.set_editor_property('Definition',unreal.load_asset('/Game/Combat/Items/DA_9mmMagazine'));item.set_editor_property('bMagazineInitialized',True);item.set_editor_property('MagazineRounds',16);check('above capacity magazine rejected',bool(inv.can_accept(item)) and inv.add_authority(item) is None)
 item.set_editor_property('MagazineRounds',-1);check('negative magazine rounds rejected',bool(inv.can_accept(item)) and inv.add_authority(item) is None)
 check('rejected records did not duplicate ammo',len(inv.get_items())==3 and sum(i.magazine_rounds for i in inv.get_items() if i.get_editor_property('bMagazineInitialized'))==30)
at(6.2,invalid_records)
tap(7,'F10')
def remapping():
 labels={str(t.get_text()) for t in unreal.ObjectIterator(unreal.TextBlock)}
 check('normal F10 menu contains all remappable combat actions',{'Equip / holster handgun','Fire handgun','Aim handgun','Reload / stand up','Unload magazine to inventory'}.issubset(labels),sorted(labels))
 pc.toggle_controls()
at(8,remapping)
at(9,lambda:check('closing Controls restores look and move input',not pc.is_move_input_ignored() and not pc.is_look_input_ignored()))
def finish():
 global w,pc,p,inv,combat,wrong
 unreal.unregister_slate_post_tick_callback(handle);(out/'magazine-contract.json').write_text(json.dumps({'results':results},indent=2));w=pc=p=inv=combat=wrong=None
def tick(dt):
 global index
 try:
  while index<len(events) and time.time()-started>=events[index][0]:events[index][1]();index+=1
  if time.time()-started>10:finish()
 except Exception:check('runner error',False,traceback.format_exc());finish()
events.sort(key=lambda e:e[0]);started=time.time();handle=unreal.register_slate_post_tick_callback(tick)



