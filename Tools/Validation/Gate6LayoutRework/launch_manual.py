"""Normal-input visual session. No gameplay RPC shortcut; scoped UObject reacquisition."""
from pathlib import Path
root=Path('D:/GitHub/RVSurvival/RVSurvival')
exec(compile((root/'Tools/Validation/Gate6LayoutRework/manual_baseline.py').read_text(encoding='utf-8'),'manual_baseline.py','exec'))
exec(compile((root/'Tools/Validation/Gate6LayoutRework/controls_entry.py').read_text(encoding='utf-8'),'controls_entry.py','exec'))
