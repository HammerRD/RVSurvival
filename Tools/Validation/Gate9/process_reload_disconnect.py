"""Reload source moves, shared-magazine contention and client disconnect cleanup."""
import unreal,json,time,os,traceback
from pathlib import Path
B=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate9Validation');session=json.loads((B/'session.json').read_text());config=session['config'];start=session['start']
w=next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='Gate9CombatInfectedTest' and unreal.GameplayStatics.get_player_controller(w,0) and unreal.GameplayStatics.get_player_controller(w,0).get_controlled_pawn());authority=unreal.GameplayStatics.get_game_mode(w) is not None;role='server' if authority else 'client';pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn();other=next(c for c in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSurvivorCharacter) if c!=p);hp=p if authority else other;cp=other if authority else p
point=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVExteriorStoragePoint) if str(a.get_editor_property('DoorPartName')).endswith('_01'));container=point.container;results=[];events=[];idx=0;active=True;held=set();contested='';shared_before=[]
def inv(c):return c.get_component_by_class(unreal.RVInventoryComponent)
def combat(c):return c.get_component_by_class(unreal.RVCombatComponent)
def guid(g):return unreal.GuidLibrary.conv_guid_to_string(g)
def mags(c):return [i for i in inv(c).get_items() if i.definition.get_editor_property('Combat').get_editor_property('bMagazine')]
def check(n,ok,d=''):results.append({'case':n,'pass':bool(ok),'detail':str(d)})
def at(t,fn):events.append((t,fn))
def key(k,on):
 unreal.RVInteriorMotorhome.dispatch_development_key(pc,k,on)
 if on:held.add(k)
 else:held.discard(k)
def tap(t,k,client_only=False):
 at(t,lambda:key(k,True) if not client_only or not authority else None);at(t+.12,lambda:key(k,False) if not client_only or not authority else None)
def seed(c,name):
 i=unreal.RVItemInstance();i.set_editor_property('Id',unreal.GuidLibrary.new_guid());i.set_editor_property('Definition',unreal.load_asset('/Game/Combat/Items/'+name));i.set_editor_property('Condition',.76);assert not inv(c).add_authority(i)
def setup():
 p.character_movement.stop_movement_immediately();p.set_actor_location(unreal.Vector(0 if authority else 300,-6500,90),False,True);pc.set_control_rotation(unreal.Rotator(yaw=0 if authority else 180))
 if authority:
  cp.set_actor_location(unreal.Vector(300,-6500,90),False,True);point.detach_from_actor(unreal.DetachmentRule.KEEP_WORLD,unreal.DetachmentRule.KEEP_WORLD,unreal.DetachmentRule.KEEP_WORLD);point.set_actor_location(unreal.Vector(130,-6500,110),False,True)
  for c in [hp,cp]:
   for name in ['DA_9mmHandgun','DA_9mmMagazine','DA_9mmMagazine']:seed(c,name)
def aim():pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p.get_actor_eyes_view_point()[0],unreal.Vector(130,-6500,110)))
at(0,setup);tap(1,'Four');tap(2,'R');at(5,aim);at(5.2,lambda:key('E',True));at(6,lambda:key('E',False));at(7,lambda:check('normal E opens shared magazine fixture',inv(p).open_container==container));tap(7.5,'R')
at(8,lambda:check('reload timer begins before spare transfer',combat(p).reload_ends>0));at(8.2,lambda:inv(p).request_transfer(next(i.id for i in mags(p) if not unreal.GuidLibrary.is_valid_guid(i.loaded_in_weapon)),1,True))
at(10.2,lambda:check('moved spare cancels reload without losing loaded ammo',combat(p).reload_ends==0 and combat(p).get_loaded_rounds()==15,combat(p).feedback))
at(10.3,lambda:check('both spares replicated into shared container',len([i for i in container.get_items() if i.definition.get_editor_property('Combat').get_editor_property('bMagazine')])==2))
def claim():
 global contested
 i=sorted([i for i in container.get_items() if i.definition.get_editor_property('Combat').get_editor_property('bMagazine')],key=lambda i:guid(i.id))[0];contested=guid(i.id);inv(p).request_transfer(i.id,1,False)
at(11,claim)
at(12.3,lambda:check('shared-magazine concurrent transfer creates one owner',sum(guid(i.id)==contested for c in [hp,cp] for i in inv(c).get_items())==1 and not any(guid(i.id)==contested for i in container.get_items())))
at(12.4,lambda:check('all 60 rounds conserved across shared transactions',sum(i.magazine_rounds for c in [hp,cp] for i in inv(c).get_items())+sum(i.magazine_rounds for i in container.get_items())==60))
at(12.6,lambda:seed(cp,'DA_9mmMagazine') if authority else None);tap(13.5,'R',True)
def remember():
 global shared_before
 shared_before=[(guid(i.id),i.magazine_rounds) for i in container.get_items()]
at(14,remember)
def finish():
 global active,w,pc,p,other,hp,cp,point,container
 if not active:return
 active=False
 for k in list(held):key(k,False)
 unreal.unregister_slate_post_tick_callback(handle);(B/(config['name']+'_'+role+'.json')).write_text(json.dumps({'role':role,'process_id':os.getpid(),'results':results,'passed':sum(r['pass'] for r in results),'total':len(results)},indent=2));w=pc=p=other=hp=cp=point=container=None;events.clear()
def disconnect():
 if authority:return
 check('client disconnects during actual pending reload',combat(p).reload_ends>0);controller=pc;execute=unreal.SystemLibrary.execute_console_command;finish()
 from runner_runtime import release_runners
 release_runners();execute(controller,'disconnect',controller)
at(14.2,disconnect)
at(18,lambda:check('server removes disconnected survivor',len(unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSurvivorCharacter))==1) if authority else None)
at(18.1,lambda:check('disconnect leaves shared magazine identities and rounds intact',[(guid(i.id),i.magazine_rounds) for i in container.get_items()]==shared_before) if authority else None);at(19,finish)
events.sort(key=lambda e:e[0])
def tick(dt):
 global idx
 if not active:return
 try:
  while idx<len(events) and time.time()-start>=events[idx][0]:
   fn=events[idx][1];idx+=1;fn()
   if not active:return
 except Exception:check('runner error',False,traceback.format_exc());finish()
handle=unreal.register_slate_post_tick_callback(tick)

