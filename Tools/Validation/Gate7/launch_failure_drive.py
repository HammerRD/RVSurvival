from pathlib import Path
source=Path('D:/GitHub/RVSurvival/RVSurvival/Tools/Validation/Gate7/launch_single.py').read_text().replace('/single.py','/failure_drive.py').replace("'single.json'","'failure-drive.json'")
exec(compile(source,'launch_failure_drive.py','exec'))
