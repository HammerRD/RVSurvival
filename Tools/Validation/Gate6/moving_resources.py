
# Executed in the live moving runner's globals; adds events to its existing scheduler.
energy=v.get_editor_property('Electrical');tank=v.get_editor_property('PropulsionFuel');house=v.get_editor_property('HouseBattery')
resource_point=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.RVResourcePoint) if not a.get_editor_property('bFuelFill'))
def resources_setup():
 if isServer:
  cmd(own,'rv.Resources.AllowDebug 1');tank.debug_set_fuel(150);house.debug_set_energy(900);energy.debug_set_solar(.35)
def request_power(name,on):
 if walker:walker.request_resource_control(name,on,energy.get_editor_property('ControlRevision'))
def power_check(name,enabled,label):
 check(label,energy.is_load_powered(name)==enabled and frame_ok() and sv.get_velocity().length()>1000,
       {'powered':energy.is_load_powered(name),'speed':sv.get_velocity().length(),'frame':frame_ok(),'source':energy.get_source_summary()})
def generator_check(enabled,label):
 check(label,energy.get_editor_property('bGeneratorRunning')==enabled and frame_ok(),
       {'generator':energy.get_editor_property('bGeneratorRunning'),'fuel':tank.get_editor_property('Litres'),'house':house.get_editor_property('EnergyWh'),'speed':sv.get_velocity().length()})
def moving_panel_open():
 check('power_placeholder_opens_real_panel',walker.get_editor_property('ResourcePoint')==resource_point if walker else True)
def resource_summary():
 check('fuel_continues_during_travel',0<tank.get_editor_property('Litres')<149.9,tank.get_editor_property('Litres'))
 check('house_energy_charges_during_travel',900<house.get_editor_property('EnergyWh')<=2400,house.get_editor_property('EnergyWh'))
 check('resource_state_valid_during_riding',0<=tank.get_editor_property('Litres')<=200 and energy.get_editor_property('SolarInput')==.35)
 check('powered_navigation_configuration',str(st['Navigation'].get_editor_property('RequiredPowerLoad'))=='PoweredStation')
at(.35,resources_setup)
at(34,lambda:request_power('Generator',True));at(36,lambda:generator_check(True,'stationary_panel_generator'))
at(84.4,moving_panel_open)
at(84.5,lambda:key(walker,'H',True));at(84.65,lambda:key(walker,'H',False))
at(85.5,lambda:power_check('InteriorLights',True,'highway_panel_lights_on'))
at(85.6,lambda:cmd(walker,'shot filename=D:/GitHub/RVSurvival/RVSurvival/Saved/Gate6Validation/'+config['name']+'_panel.png -nosuffix') if walker else None)
at(86,lambda:request_power('Generator',False));at(87,lambda:generator_check(False,'highway_panel_generator_stop'))
at(87.5,lambda:request_power('Generator',True));at(88.5,lambda:generator_check(True,'highway_panel_generator_restart'))
at(95.1,lambda:key(walker,'H',True));at(95.25,lambda:key(walker,'H',False))
at(95.9,lambda:power_check('InteriorLights',False,'gentle_turn_lights_switch'))
at(171,resource_summary)
old_resource_snap=snap
def snap():
 old_resource_snap()
 rows[-1]['resources']={'fuel_litres':tank.get_editor_property('Litres'),'house_wh':house.get_editor_property('EnergyWh'),
   'chassis_wh':v.get_editor_property('ChassisBattery').get_editor_property('EnergyWh'),'generator':energy.get_editor_property('bGeneratorRunning'),
   'lights':energy.is_load_powered('InteriorLights'),'revision':energy.get_editor_property('ControlRevision'),'source':energy.get_source_summary(),'solar':energy.get_editor_property('SolarInput')}
