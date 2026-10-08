"""100 normal semiauto presses and seven real reloads; bounded invariant stress."""
import unreal,json,time,traceback
from pathlib import Path
out=Path('D:/GitHub/RVSurvival/RVSurvival/Docs/Gate9Results');results=[];events=[];started=time.time();index=0
w=next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='Gate9CombatInfectedTest' and unreal.GameplayStatics.get_player_controller(w,0) and unreal.GameplayStatics.get_player_controller(w,0).get_controlled_pawn())
pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn();inv=p.get_component_by_class(unreal.RVInventoryComponent);combat=p.get_component_by_class(unreal.RVCombatComponent)
p.set_actor_location(unreal.Vector(0,-6500,90),False,True);pc.set_control_rotation(unreal.Rotator(yaw=180))
def check(name,ok,detail=''):results.append({'case':name,'pass':bool(ok),'detail':str(detail)})
def at(t,fn):events.append((t,fn))
def key(k,on):unreal.RVInteriorMotorhome.dispatch_development_key(pc,k,on)
def tap(t,k):at(t,lambda:key(k,True));at(t+.12,lambda:key(k,False))
for path in ['/Game/Combat/Items/DA_9mmHandgun']+['/Game/Combat/Items/DA_9mmMagazine']*8:
 i=unreal.RVItemInstance();i.set_editor_property('Id',unreal.GuidLibrary.new_guid());i.set_editor_property('Definition',unreal.load_asset(path));i.set_editor_property('Condition',.73);assert not inv.add_authority(i)
ids={unreal.GuidLibrary.conv_guid_to_string(i.id) for i in inv.get_items()}
tap(.2,'Four');t=.6;shots=0
while shots<100:
 tap(t,'R');t+=2.5
 for _ in range(min(15,100-shots)):
  tap(t,'LeftMouseButton');t+=.4;shots+=1
at(t+.5,lambda:check('100 normal presses accepted exactly once each',combat.shot_sequence==100,combat.shot_sequence))
at(t+.6,lambda:check('120 initial rounds less 100 shots equals 20',sum(i.magazine_rounds for i in inv.get_items())==20))
at(t+.7,lambda:check('no GUID loss or duplication across seven reloads',{unreal.GuidLibrary.conv_guid_to_string(i.id) for i in inv.get_items()}==ids and len(inv.get_items())==9))
at(t+.8,lambda:check('all quantities, conditions and magazine bounds valid',all(i.quantity==1 and abs(i.condition-.73)<.001 and 0<=i.magazine_rounds<=15 for i in inv.get_items())))
at(t+.9,lambda:check('only one real magazine reserved',sum(unreal.GuidLibrary.is_valid_guid(i.loaded_in_weapon) for i in inv.get_items())==1))
tap(t+1,'U');at(t+1.5,lambda:check('final unload preserves 20 rounds without reserved GUID',sum(i.magazine_rounds for i in inv.get_items())==20 and not any(unreal.GuidLibrary.is_valid_guid(i.loaded_in_weapon) for i in inv.get_items())))
def finish():
 global w,pc,p,inv,combat
 unreal.unregister_slate_post_tick_callback(handle);(out/'combat-stress.json').write_text(json.dumps({'results':results,'passed':sum(r['pass'] for r in results),'total':len(results),'duration':time.time()-started},indent=2));w=pc=p=inv=combat=None
end=t+2
def tick(dt):
 global index
 try:
  while index<len(events) and time.time()-started>=events[index][0]:events[index][1]();index+=1
  if time.time()-started>end:finish()
 except Exception:check('runner error',False,traceback.format_exc());finish()
events.sort(key=lambda e:e[0]);handle=unreal.register_slate_post_tick_callback(tick)
