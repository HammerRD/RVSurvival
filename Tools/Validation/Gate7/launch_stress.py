from pathlib import Path
# Same safe launcher lifecycle, unique receipt and longer bounded session.
source=(Path('D:/GitHub/RVSurvival/RVSurvival/Tools/Validation/Gate7/launch_single.py').read_text()).replace("/single.py'","/stress.py'").replace("'single.json'","'stress.json'").replace('>120','>300')
exec(compile(source,'launch_stress.py','exec'))
