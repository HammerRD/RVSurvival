"""PIE foundation checks through normal Enhanced Input; fixture admission only."""
import unreal,json,time,traceback
from pathlib import Path
out=Path('D:/GitHub/RVSurvival/RVSurvival/Docs/Gate9_5Results');results=[];events=[];started=time.time();index=0
w=next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='Gate9_5CombatRefinementTest' and unreal.GameplayStatics.get_player_controller(w,0) and unreal.GameplayStatics.get_player_controller(w,0).get_controlled_pawn())
pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn();inv=p.get_component_by_class(unreal.RVInventoryComponent);combat=p.get_component_by_class(unreal.RVCombatComponent)
def check(name,ok,detail=''):
 row={'case':name,'pass':bool(ok),'detail':str(detail)};results.append(row);unreal.log('GATE9 '+json.dumps(row))
def at(t,fn):events.append((t,fn))
def key(name,on):unreal.RVInteriorMotorhome.dispatch_development_key(pc,name,on)
def tap(t,name):at(t,lambda:key(name,True));at(t+.12,lambda:key(name,False))
def rounds():return combat.get_loaded_rounds()
def items():return inv.get_items()
def weapon():return next(i for i in items() if i.definition.get_editor_property('Combat').get_editor_property('bFirearm'))
def magazines():return [i for i in items() if i.definition.get_editor_property('Combat').get_editor_property('bMagazine')]
def add(path,quantity=1):
 i=unreal.RVItemInstance();i.set_editor_property('Id',unreal.GuidLibrary.new_guid());i.set_editor_property('Definition',unreal.load_asset(path));i.set_editor_property('Quantity',quantity)
 error=inv.add_authority(i);check('fixture item admitted',not error,error)
add('/Game/Combat/Gate9_5/Items/DA_M1911_45ACP')
for _ in range(3):add('/Game/Combat/Gate9_5/Items/DA_45ACPMagazine')
check('Gate 9 opt-in saved',combat.get_editor_property('bEnabled'))
check('ordinary actor movement remains walking',p.character_movement.movement_mode==unreal.MovementMode.MOVE_WALKING)
tap(.2,'Four');at(.6,lambda:check('normal 4 equips owned GUID',unreal.GuidLibrary.equal_equal_guid_guid(combat.equipped_weapon,weapon().id)))
tap(.8,'R');at(1.3,lambda:check('normal R starts authoritative reload',combat.reload_ends>0))
at(3.2,lambda:check('reload loads real magazine',rounds()==7))
tap(3.4,'LeftMouseButton');at(3.9,lambda:check('normal LMB consumes exactly one round',rounds()==6 and combat.shot_sequence==1))
at(4.1,lambda:key('LeftMouseButton',True));at(5.1,lambda:key('LeftMouseButton',False));at(5.4,lambda:check('semi-auto held button does not repeat',rounds()==5 and combat.shot_sequence==2))
tap(5.6,'R');at(8.0,lambda:check('partial reload conserves total ammunition',rounds()==7 and sum(m.magazine_rounds for m in magazines())==19))
at(8.2,lambda:key('RightMouseButton',True));at(8.6,lambda:check('normal RMB applies aim',combat.get_editor_property('bAiming')))
at(8.8,lambda:key('RightMouseButton',False));at(9.1,lambda:check('aim release restores',not combat.get_editor_property('bAiming')))
tap(9.3,'Four');at(9.8,lambda:check('holster preserves loaded magazine and rounds',not unreal.GuidLibrary.is_valid_guid(combat.equipped_weapon) and sum(m.magazine_rounds for m in magazines())==19 and any(unreal.GuidLibrary.is_valid_guid(m.loaded_in_weapon) for m in magazines())))
tap(10,'Four');at(10.4,lambda:check('reequip retains loaded magazine',rounds()==7));tap(10.6,'U');at(11.0,lambda:check('normal U unload preserves every round',rounds()==0 and sum(m.magazine_rounds for m in magazines())==19))
at(11.2,lambda:check('all GUIDs remain unique',len({unreal.GuidLibrary.conv_guid_to_string(i.id) for i in items()})==len(items())))
def finish():
 global w,pc,p,inv,combat
 unreal.unregister_slate_post_tick_callback(handle)
 (out/'foundation-input.json').write_text(json.dumps({'results':results,'passed':sum(r['pass'] for r in results),'total':len(results)},indent=2))
 w=pc=p=inv=combat=None
def tick(dt):
 global index
 try:
  while index<len(events) and time.time()-started>=events[index][0]:
   events[index][1]();index+=1
  if time.time()-started>12:finish()
 except Exception:
  check('runner error',False,traceback.format_exc());finish()
handle=unreal.register_slate_post_tick_callback(tick)
