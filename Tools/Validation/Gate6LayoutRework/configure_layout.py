"""Gate 6 project-side layout only. Run in a fresh, non-PIE editor.
All UObject references are scoped to configure(); never reload a live world.
"""
import unreal, json
from pathlib import Path
B=Path('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate6LayoutRework')
def configure():
    levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    assert levels.load_level('/Game/Maps/Gate6FuelElectricalTest')
    assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    subsystem=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors=subsystem.get_all_level_actors()
    rv=next(a for a in actors if isinstance(a,unreal.RVSystemsMotorhome))
    roles={'Kitchen':(-40,60,179),'Workbench':(-18,-30,154),
           'Storage':(-185,-70,155),'Medical':(-130,-70,258)}
    stations=rv.get_editor_property('Stations')
    for d in stations:
        if str(d.name) in roles:d.set_editor_property('Position',unreal.Vector(*roles[str(d.name)]))
    rv.set_editor_property('Stations',stations)
    storage={'Water supplies':(45,60,176),'Personal supplies':(-185,-65,262),
             'Pantry':(15,62,269),'Medical storage':(-130,-65,258)}
    changed=[]
    for actor in actors:
        if isinstance(actor,unreal.RVStoragePoint) and actor.get_attach_parent_actor()==rv:
            c=actor.get_editor_property('Container');name=str(c.get_editor_property('DisplayName'))
            if name in storage:
                actor.set_actor_location(rv.get_actor_transform().transform_location(unreal.Vector(*storage[name])),False,True)
                changed.append({'role':name,'local':storage[name]})
        if isinstance(actor,unreal.RVRestPoint) and actor.get_attach_parent_actor()==rv:
            name=str(actor.get_editor_property('DisplayName'))
            if name=='Rear bed':
                actor.set_actor_location(rv.get_actor_transform().transform_location(unreal.Vector(-255,48,183)),False,True)
                actor.set_editor_property('InteractionExtent',unreal.Vector(90,48,3))
                actor.set_editor_property('LyingOffset',unreal.Vector(10,0,19))
                actor.set_editor_property('LyingRotation',unreal.Rotator(yaw=180))
                actor.set_editor_property('WakeAisleLocation',unreal.Vector(-115,0,185))
            elif name=='Dinette rest':
                actor.set_actor_location(rv.get_actor_transform().transform_location(unreal.Vector(45,-28,155)),False,True)
                actor.set_editor_property('InteractionExtent',unreal.Vector(12,8,3))
    # Individually named light-cargo cabinets; no unrestricted heavy automotive cargo.
    overhead=[('Dinette overhead - dry food',(25,-62,273),['Item.Category.Food','Item.Category.Water'],6,14),
              ('Rear overhead - medical backup',(-290,62,274),['Item.Category.Medical'],4,10),
              ('Kitchen overhead - small tools',(-40,62,273),['Item.Category.Tool'],5,10)]
    for name,local,allowed,weight,volume in overhead:
        actor=next((a for a in actors if isinstance(a,unreal.RVStoragePoint) and str(a.get_editor_property('Container').get_editor_property('DisplayName')) in [name,'Dinette overhead - household supplies' if name=='Dinette overhead - dry food' else name]),None)
        if actor is None:
            actor=subsystem.spawn_actor_from_class(unreal.RVStoragePoint,rv.get_actor_transform().transform_location(unreal.Vector(*local)))
            actor.attach_to_actor(rv,'',unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,False)
        c=actor.get_editor_property('Container');c.set_editor_property('DisplayName',unreal.Text(name))
        c.set_editor_property('MaxWeightKg',weight);c.set_editor_property('MaxVolumeLitres',volume);c.set_editor_property('bAllowPhysicalCarry',False)
        c.set_editor_property('AllowedTags',unreal.GameplayTagLibrary.make_gameplay_tag_container_from_array([unreal.RVItemDefinition.find_registered_tag(t) for t in allowed]))
        actor.set_actor_location(rv.get_actor_transform().transform_location(unreal.Vector(*local)),False,True)
        changed.append({'role':name,'local':local,'weight':weight,'volume':volume,'allowed':allowed})
    for prop in ['DinetteFrontSeat','DinetteRearSeat']:
        rv.get_editor_property(prop).set_editor_property('bEnabled',True)
    collision=rv.get_editor_property('InteriorCollision')
    corrected={'KitchenCabinet':((20,80,130),(65,35,43)),
               'Dinette':((15,-80,125),(45,30,27)),
               'Bathroom':((-175,-100,200),(65,20,100)),
               'Bed':((-255,48,140),(100,70,40))}
    for d in collision:
        if str(d.name) in corrected:
            center,extent=corrected[str(d.name)]
            d.set_editor_property('Center',unreal.Vector(*center));d.set_editor_property('Extent',unreal.Vector(*extent))
    for name,center,extent in [('DinetteFrontBench',(105,-82,123),(20,30,13)),('DinetteRearBench',(-70,-82,123),(20,30,13))]:
        d=next((d for d in collision if str(d.name)==name),None)
        if d is None:d=unreal.RVInteriorCollision();collision.append(d)
        d.set_editor_property('Name',name);d.set_editor_property('Center',unreal.Vector(*center));d.set_editor_property('Extent',unreal.Vector(*extent))
    rv.set_editor_property('InteriorCollision',collision);rv.refresh_configuration()
    assert levels.save_current_level()
    assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    (B/'layout-configured.json').write_text(json.dumps({'saved':True,'changed':changed,'stations':roles,'visual_validation':'pending'},indent=2),encoding='utf-8')
configure()
unreal.SystemLibrary.quit_editor()
