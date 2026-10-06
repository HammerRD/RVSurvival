import unreal,json
w=next(w for w in unreal.ObjectIterator(unreal.World) if 'UEDPIE_' in w.get_path_name() and w.get_name()=='Gate6FuelElectricalTest')
pc=unreal.GameplayStatics.get_player_controller(w,0);v=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVSystemsMotorhome)[0]
bus=v.get_editor_property('Electrical');battery=v.get_editor_property('HouseBattery')
unreal.SystemLibrary.execute_console_command(w,'rv.Resources.AllowDebug 1',pc)
loads=list(bus.get_editor_property('Loads'))
for load in loads:load.set_editor_property('bEnabled',True)
bus.set_editor_property('Loads',loads);battery.debug_set_energy(2400);bus.debug_set_solar(0)
bus.debug_advance(86400,False,0,0)
data={'energy_wh':battery.get_editor_property('EnergyWh'),'has_house_power':bus.has_house_power(),'loads':[{'id':str(l.id),'watts':l.watts,'powered':l.get_editor_property('bPowered')} for l in bus.get_editor_property('Loads')],'flow_supplied_w':bus.get_editor_property('Flow').supplied_watts}
unreal.log('GATE6_BOUNDARY '+json.dumps(data))
json.dump({'results':[{'case':'boundary_inspection','pass':True,'detail':data}]},open('D:/GitHub/RVSurvival/RVSurvival/Saved/Gate6Validation/single.json','w'),indent=2)
