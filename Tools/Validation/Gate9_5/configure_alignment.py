"""Initial mesh-measured alignment; subsequent render validation required."""
import unreal,json
from pathlib import Path
def configure():
 d=unreal.load_asset('/Game/Combat/Gate9_5/Items/DA_M1911_45ACP');d.modify();c=d.get_editor_property('Combat')
 # OBJ export inspected: barrel points toward local -X; rear sight at X3.1/Z6.35, front near X-14.6/Z6.4.
 c.set_editor_property('GripOffset',unreal.Transform(location=unreal.Vector(-14,-1.5,3.5),rotation=unreal.Rotator()))
 c.set_editor_property('SightTransform',unreal.Transform(location=unreal.Vector(3.1,0,6.35),rotation=unreal.Rotator(pitch=.16,yaw=180)))
 c.set_editor_property('SightEyeReliefCm',30);c.set_editor_property('MuzzleTransform',unreal.Transform(location=unreal.Vector(-15.5,0,4),rotation=unreal.Rotator(yaw=180)))
 c.set_editor_property('EjectTransform',unreal.Transform(location=unreal.Vector(-3,1.6,4.8)));c.set_editor_property('SupportHandTarget',unreal.Transform(location=unreal.Vector(10,8,-5)))
 d.set_editor_property('Combat',c);assert unreal.EditorAssetLibrary.save_loaded_asset(d,False)
 d=unreal.load_asset('/Game/Combat/Gate9_5/Items/DA_PrototypeCrowbar');d.modify();c=d.get_editor_property('Combat');c.set_editor_property('GripOffset',unreal.Transform(location=unreal.Vector(-11,-1.5,-8)));d.set_editor_property('Combat',c);assert unreal.EditorAssetLibrary.save_loaded_asset(d,False)
 (Path('D:/GitHub/RVSurvival/RVSurvival/Docs/Gate9_5Results')/'initial-alignment.json').write_text(json.dumps({'handgun_grip_cm':[-14,-1.5,3.5],'rear_sight_cm':[3.1,0,6.35],'sight_pitch_yaw':[.16,180],'eye_relief_cm':30,'muzzle_cm':[-15.5,0,4],'crowbar_grip_cm':[-11,-1.5,-8],'status':'mesh-measured initial configuration; visual validation pending'},indent=2))
configure()




