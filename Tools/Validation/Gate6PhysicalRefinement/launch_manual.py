import unreal,sys
sys.path.insert(0,'D:/GitHub/RVSurvival/RVSurvival/Saved/Gate3Validation')
from runner_runtime import load_runner
def prepare():
    levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    assert levels.load_level('/Game/Maps/Gate6FuelElectricalTest')
    assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.LevelEditorPlaySettings'))
    settings.set_editor_property('PlayNumberOfClients',1);settings.set_editor_property('RunUnderOneProcess',True)
    settings.set_editor_property('AdditionalLaunchParameters','-FPS=60')
    network=settings.get_editor_property('NetworkEmulationSettings');network.set_editor_property('bIsNetworkEmulationEnabled',False);settings.set_editor_property('NetworkEmulationSettings',network)
    levels.editor_request_begin_play()
prepare()
load_runner('D:/GitHub/RVSurvival/RVSurvival/Tools/Validation/Gate6PhysicalRefinement/manual_session.py')
