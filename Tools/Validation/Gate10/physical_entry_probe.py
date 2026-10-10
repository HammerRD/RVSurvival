"""Normal-key physical door/step entry inspection, not direct entry RPC calls."""
import unreal,time,json,traceback
from pathlib import Path
out=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate10Validation');started=time.time();phase=-1;handle=None

def world():return next(w for w in unreal.ObjectIterator(unreal.World) if w.get_name()=='WNY_PrototypeRegion' and unreal.GameplayStatics.get_game_mode(w) and unreal.GameplayStatics.get_player_controller(w,0))
def input_key(name,on):unreal.RVInteriorMotorhome.dispatch_development_key(unreal.GameplayStatics.get_player_controller(world(),0),name,on)
def face_door():
 w=world();pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn();door=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVInteractiveDoor)[0]
 pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(p.get_actor_location()+unreal.Vector(0,0,68),door.get_editor_property('DoorCollision').get_world_location()))
def sample(name):
 w=world();pc=unreal.GameplayStatics.get_player_controller(w,0);p=pc.get_controlled_pawn();rv=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVInteriorMotorhome)[0];door=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVInteractiveDoor)[0]
 pos=p.get_actor_location();rpos=rv.get_actor_location();mesh=rv.get_component_by_class(unreal.SkeletalMeshComponent);frame=p.get_component_by_class(unreal.RVPassengerReferenceFrameComponent)
 result={'step':name,'pawn_position':[pos.x,pos.y,pos.z],'vehicle_position':[rpos.x,rpos.y,rpos.z],'vehicle_physics':mesh.is_simulating_physics(),'movement_mode':str(p.character_movement.movement_mode),'prompt':str(p.get_component_by_class(unreal.RVInteractionComponent).get_prompt()),'trace':p.get_component_by_class(unreal.RVInteractionComponent).debug_trace_description(),'door_open':door.get_editor_property('bOpen'),'frame_registered':frame.reference_frame==rv}
 (out/('physical-entry-'+name+'.json')).write_text(json.dumps(result,indent=2))
def tick(delta):
 global phase,handle
 t=time.time()-started
 try:
  if phase==-1:input_key('S',True);phase=-2
  elif phase==-2 and t>.8:input_key('S',False);face_door();input_key('W',True);phase=1
  elif phase==1 and t>1.4:input_key('W',False);face_door();sample('approach');phase=2
  elif phase==2 and t>1.7:input_key('E',True);phase=3
  elif phase==3 and t>1.8:input_key('E',False);sample('open');input_key('W',True);phase=4
  elif phase==4 and t>3.3:input_key('W',False);sample('crossing');phase=5
  elif phase==5 and t>3.6:unreal.unregister_slate_post_tick_callback(handle);handle=None
 except Exception:
  input_key('W',False);input_key('E',False);(out/'physical-entry-error.txt').write_text(traceback.format_exc());unreal.unregister_slate_post_tick_callback(handle);handle=None
handle=unreal.register_slate_post_tick_callback(tick)



