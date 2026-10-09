"""Fresh saved-content inspection; no map reload loop or retained world references."""
import unreal, gc, json, traceback
from pathlib import Path
root = Path('D:/GitHub/RVSurvival/RVSurvival')
out = root/'Docs/Gate9_5Results'
def inspect():
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    assert levels.load_level('/Game/Maps/Gate9_5CombatRefinementTest')
    loaded = []
    for folder in ['/Game/Combat/Gate9_5', '/Game/Characters/RV/Gate9_5', '/Game/ThirdParty/Xeradev/M1911', '/Game/ThirdParty/RED2000/Crowbar']:
        for path in unreal.EditorAssetLibrary.list_assets(folder, True, False):
            asset = unreal.load_asset(path)
            assert asset, path
            loaded.append(path)
    pistol = unreal.load_asset('/Game/Combat/Gate9_5/Items/DA_M1911_45ACP')
    combat = pistol.get_editor_property('Combat')
    assert combat.get_editor_property('bSightADS')
    assert str(combat.get_editor_property('Caliber')) != 'None'
    assert combat.get_editor_property('MagazineCapacity') == 7
    profiles = {}
    for name in ['Relaxed', 'Standard', 'Harsh']:
        profile = unreal.load_asset('/Game/Combat/Gate9_5/Difficulty/DA_'+name)
        rules = profile.get_editor_property('Rules')
        assert len(rules) == 16
        profiles[name] = {str(r.get_editor_property('Id')): r.get_editor_property('Multiplier') for r in rules}
        assert all(r.get_editor_property('Minimum') <= r.get_editor_property('Multiplier') <= r.get_editor_property('Maximum') for r in rules)
    assert profiles['Relaxed']['Hunger'] < profiles['Standard']['Hunger'] < profiles['Harsh']['Hunger']
    assert levels.save_current_level()
    assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    return {'saved': True, 'assets_loaded': loaded, 'sight_ads': True, 'caliber': str(combat.get_editor_property('Caliber')), 'capacity': 7, 'profiles': profiles}
try:
    (out/'final-saved-audit.json').write_text(json.dumps(inspect(), indent=2))
except Exception:
    (out/'final-saved-audit-error.txt').write_text(traceback.format_exc())
    traceback.print_exc()
finally:
    gc.collect()
    unreal.SystemLibrary.quit_editor()
