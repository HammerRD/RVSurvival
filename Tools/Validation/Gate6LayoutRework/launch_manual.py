"""Normal-input visual session. No gameplay RPC shortcut; scoped UObject reacquisition."""
import sys
sys.path.insert(0,'D:/GitHub/RVSurvival/RVSurvival/Saved/Gate3Validation')
from runner_runtime import load_runner
# Own both callback handles in releasable modules, not script-exec globals.
load_runner('D:/GitHub/RVSurvival/RVSurvival/Tools/Validation/Gate6LayoutRework/manual_baseline.py')
load_runner('D:/GitHub/RVSurvival/RVSurvival/Tools/Validation/Gate6LayoutRework/manual_controls.py')
