from pathlib import Path
source=Path('D:/GitHub/RVSurvival/RVSurvival/Tools/Validation/Gate7/launch_single.py').read_text().replace('/single.py','/ui_probe.py').replace("'single.json'","'ui-probe.json'")
exec(compile(source,'launch_ui_probe.py','exec'))
