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
           'Medical':(-185,-65,196),'Power':(224,14,126),'Navigation':(224,0,141)}
    stations=rv.get_editor_property('Stations')
    # Gate6 replaces the old generic storage counter with the real shared cabinet below.
    # Prior maps retain their original six workstation placeholders.
    stations=[d for d in stations if str(d.name)!='Storage']
    for index,d in enumerate(stations):
        if str(d.name) in roles:
            d.set_editor_property('Position',unreal.Vector(*roles[str(d.name)]));stations[index]=d
    rv.set_editor_property('Stations',stations)
    rv.set_editor_property('PowerPanelLocation',unreal.Vector(224,-14,126))
    storage={'Water supplies':(45,60,176),'Personal supplies':(-185,-65,262),
             'Pantry':(15,62,269),'Medical storage':(-110,-57,256)}
    changed=[]
    light_tags=['Item.Category.Food','Item.Category.Water','Item.Category.Medical','Item.Category.Tool']
    interior_limits={'Pantry':(8,18,['Item.Category.Food','Item.Category.Water']),
                     'Personal supplies':(6,12,light_tags),'Medical storage':(4,8,['Item.Category.Medical']),
                     'Water supplies':(12,20,['Item.Category.Water'])}
    for actor in actors:
        if isinstance(actor,unreal.RVStoragePoint) and actor.get_attach_parent_actor()==rv:
            c=actor.get_editor_property('Container');name=str(c.get_editor_property('DisplayName'))
            if name in storage:
                actor.set_actor_location(rv.get_actor_transform().transform_location(unreal.Vector(*storage[name])),False,True)
                kg,litres,tags=interior_limits[name]
                c.set_editor_property('MaxWeightKg',kg);c.set_editor_property('MaxVolumeLitres',litres);c.set_editor_property('bAllowPhysicalCarry',False)
                c.set_editor_property('AllowedTags',unreal.GameplayTagLibrary.make_gameplay_tag_container_from_array([unreal.RVItemDefinition.find_registered_tag(t) for t in tags]))
                changed.append({'role':name,'local':storage[name]})
        if isinstance(actor,unreal.RVRestPoint) and actor.get_attach_parent_actor()==rv:
            name=str(actor.get_editor_property('DisplayName'))
            if name=='Rear bed':
                actor.set_actor_location(rv.get_actor_transform().transform_location(unreal.Vector(-255,48,183)),False,True)
                actor.set_editor_property('InteractionExtent',unreal.Vector(90,48,3))
                actor.set_editor_property('LyingOffset',unreal.Vector(10,0,12))
                actor.set_editor_property('LyingSupportCollisionName','Bed')
                actor.set_editor_property('LyingRotation',unreal.Rotator(yaw=180))
                actor.set_editor_property('WakeAisleLocation',unreal.Vector(-115,0,185))
            elif name=='Dinette rest':
                actor.set_actor_location(rv.get_actor_transform().transform_location(unreal.Vector(45,-28,155)),False,True)
                actor.set_editor_property('InteractionExtent',unreal.Vector(12,8,3))
    # Individually named light-cargo cabinets; no unrestricted heavy automotive cargo.
    overhead=[('Bed-end cabinet',(-110,-57,190),['Item.Category.Food','Item.Category.Water','Item.Category.Medical','Item.Category.Tool'],10,20),
              ('Dinette overhead - dry food',(25,-62,273),['Item.Category.Food','Item.Category.Water'],6,14),
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
    # Keep the seated body between the measured wardrobe side (x=-83.3)
    # and table edge, on the actual rear cushion rather than its back edge.
    rear=rv.get_editor_property('DinetteRearSeat')
    rear.set_editor_property('RelativeLocation',unreal.Vector(-55,-82,138))
    rear.set_editor_property('StandingAisleLocation',unreal.Vector(-55,0,180))
    collision=rv.get_editor_property('InteriorCollision')
    corrected={'KitchenCabinet':((20,80,130),(65,35,43)),
               'Dinette':((15,-80,125),(45,30,27)),
               'Bathroom':((-175,-100,200),(65,20,100)),
               'Bed':((-255,48,140),(100,70,40))}
    for index,d in enumerate(collision):
        if str(d.name) in corrected:
            center,extent=corrected[str(d.name)]
            d.set_editor_property('Center',unreal.Vector(*center));d.set_editor_property('Extent',unreal.Vector(*extent))
            collision[index]=d
    # Read-only vendor vertices put the wardrobe side at x=-83.3 above
    # cushion height, and cabinet handles around y=-58.3. Retain this wall.
    for name,center,extent in [('DinetteFrontBench',(105,-82,123),(20,30,13)),('DinetteRearBench',(-55,-82,123),(15,30,13)),('BedEndWardrobe',(-118.5,-89,199),(35.5,31,101))]:
        d=next((d for d in collision if str(d.name)==name),None)
        if d is None:d=unreal.RVInteriorCollision()
        d.set_editor_property('Name',name);d.set_editor_property('Center',unreal.Vector(*center));d.set_editor_property('Extent',unreal.Vector(*extent))
        index=next((i for i,item in enumerate(collision) if str(item.name)==name),None)
        if index is None:collision.append(d)
        else:collision[index]=d
    rv.set_editor_property('InteriorCollision',collision);rv.refresh_configuration()
    ladder=next((a for a in actors if isinstance(a,unreal.RVLadder)),None)
    if ladder is None:
        ladder=subsystem.spawn_actor_from_class(unreal.RVLadder,rv.get_actor_transform().transform_location(unreal.Vector(-374,75,155)))
        ladder.attach_to_actor(rv,'',unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,False)
    ladder.set_editor_property('BottomLocal',unreal.Vector(-415,75,78))
    ladder.set_editor_property('GroundExitLocal',unreal.Vector(-455,75,110))
    ladder.set_editor_property('ClimbHeight',180)
    ladder.set_actor_label('Gate6_RearLadder_ControlledEndpoint')
    assert levels.save_current_level()
    assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    (B/'layout-configured.json').write_text(json.dumps({'saved':True,'changed':changed,'stations':roles,'visual_validation':'pending'},indent=2),encoding='utf-8')
configure()
unreal.SystemLibrary.quit_editor()
