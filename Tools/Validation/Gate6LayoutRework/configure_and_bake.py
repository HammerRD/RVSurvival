"""Fresh-editor save milestones, with one initial map load and no reload cleanup."""
from pathlib import Path
base=Path('D:/GitHub/RVSurvival/RVSurvival/Tools/Validation/Gate6LayoutRework')
source=(base/'configure_layout.py').read_text(encoding='utf-8-sig').replace('unreal.SystemLibrary.quit_editor()','')
exec(compile(source,'configure_layout.py','exec'))
exec(compile((base/'bake_defaults.py').read_text(encoding='utf-8-sig'),'bake_defaults.py','exec'))
