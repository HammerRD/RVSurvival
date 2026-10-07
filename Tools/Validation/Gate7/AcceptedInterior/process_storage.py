"""Moving pantry and shared exterior contention regression diagnostics.
Isolated exterior fixture placement is explicit; not manual walking evidence.
"""
from pathlib import Path
prefix=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate7AcceptedInterior/auxiliary_prefix.py').read_text(encoding='utf-8-sig').split('at(0,setup);')[0]
exec(compile(prefix,'auxiliary-fixture-prefix','exec'))
def key(k,on):unreal.RVInteriorMotorhome.dispatch_development_key(pc,k,on)
at(0,setup);at(1,lambda:aim(de if isdriver else pe));at(1.2,lambda:key('E',True));at(2.1,lambda:key('E',False))
at(3.5,lambda:check('E_driver_and_passenger',driver.get_editor_property('Occupant')==dp and passenger.get_editor_property('Occupant')==wp))
tap(4,'Three','walker');at(5.5,lambda:check('3_standing_walker',walking(wp)))
at(6,lambda:key('W',True) if isdriver else None)
at(8,lambda:aim(pantry) if not isdriver else None);at(8.2,lambda:key('E',True) if not isdriver else None);at(9.1,lambda:key('E',False) if not isdriver else None)
at(10.5,lambda:check('moving_pantry_E_owner_view',inventory(wp).get_editor_property('OpenContainer')==pantry.get_editor_property('Container')) if authority or not isdriver else None)
at(11,lambda:key('A',True) if isdriver else None);tap(11.3,'T','walker');at(12.5,lambda:key('A',False) if isdriver else None)
at(13,lambda:check('gentle_turn_transfer_to_pantry_T',quantity(pantry.get_editor_property('Container'))==1 and quantity(inventory(wp))==0 and v.get_velocity().length()>150,v.get_velocity().length()))
tap(13.5,'Tab','walker');tap(14.5,'T','walker')
at(16,lambda:check('pantry_return_preserves_condition',quantity(pantry.get_editor_property('Container'))==0 and quantity(inventory(wp))==1 and abs(inventory(wp).get_items()[0].condition-.62)<.001))
tap(16.5,'I','walker')
at(17,lambda:key('W',False) if isdriver else None);at(17.1,lambda:key('S',True) if isdriver else None)
at(23,lambda:key('S',False) if isdriver else None);at(23.2,lambda:key('SpaceBar',True) if isdriver else None);at(29,lambda:key('SpaceBar',False) if isdriver else None)
at(30,lambda:check('stopped_before_exterior_fixture',v.get_velocity().length()<10,v.get_velocity().length()))
tap(30.2,'Three','driver')
def exterior_fixture():
 if authority:
  q=v.get_actor_transform().inverse_transform_location(exterior.get_actor_location());side=1 if q.y>0 else -1
  place(hp,(q.x-45,side*300,75));place(cp,(q.x+45,side*300,75));seed(exterior.get_editor_property('Container'),'Tool')
at(33,exterior_fixture);at(34,lambda:aim(exterior));at(34.2,lambda:key('E',True));at(35.1,lambda:key('E',False))
at(36.5,lambda:check('shared_exterior_E_owner_view',inventory(p).get_editor_property('OpenContainer')==exterior.get_editor_property('Container')))
tap(37,'Tab','driver');tap(38,'T')
def conserved():
 records=[i for c in [inventory(hp),inventory(cp),exterior.get_editor_property('Container')] for i in c.get_items() if str(i.definition.get_editor_property('CatalogId'))=='Tool']
 check('simultaneous_T_conserves_one_tool_and_GUID',sum(i.quantity for i in records)==1 and len({unreal.GuidLibrary.conv_guid_to_string(i.id) for i in records})==len(records) and quantity(exterior.get_editor_property('Container'))==0)
at(40,conserved);tap(40.5,'I')
def finish():
 global active
 for name in ['E','W','S','A','I','T','Tab','Three','SpaceBar']:key(name,False)
 active=False;unreal.unregister_slate_post_tick_callback(h)
 (B/(config['name']+('_server.json' if authority else '_client.json'))).write_text(json.dumps({'pid':os.getpid(),'config':config,'evidence_kind':'native-input regression diagnostics with isolated fixtures','results':results,'samples':samples},indent=2))
 from runner_runtime import release_runners
 release_runners()
at(42,finish);events.sort(key=lambda pair:pair[0])
def tick(dt):
 global idx,input_frame,nextsample,hp,cp,dp,wp
 if not active:return
 input_frame+=1
 if not authority:
  remote=next((c for c in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSurvivorCharacter) if c!=p),None)
  if remote:hp=remote;cp=p;dp=p if isdriver else remote;wp=remote if isdriver else p
 elapsed=time.time()-start
 if elapsed<0:return
 try:
  for name,(deadline,frame) in list(pulses.items()):
   if time.time()>=deadline and input_frame>=frame:key(name,False);del pulses[name]
  while idx<len(events) and elapsed>=events[idx][0] and not pulses:
   fn=events[idx][1];idx+=1;ending=fn.__name__=='finish';fn()
   if ending:return
  if elapsed>=nextsample:
   nextsample=elapsed+.1;samples.append({'t':elapsed,'driver':local(dp),'walker':local(wp),'speed':v.get_velocity().length()})
 except Exception as error:check('harness_exception',False,repr(error));finish()
h=unreal.register_slate_post_tick_callback(tick)
