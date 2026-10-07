from pathlib import Path
source=Path('D:/GitHub/RVSurvival/RVSurvival/Tools/Validation/Gate7/launch_single.py').read_text().replace('/single.py','/profiles.py').replace("'single.json'","'profiles.json'")
exec(compile(source,'launch_profiles.py','exec'))
