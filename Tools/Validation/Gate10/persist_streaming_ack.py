"""Preserve unrelated working-tree engine config; stage only the Gate10 delta."""
from pathlib import Path
import subprocess
p=Path('Config/DefaultEngine.ini')
delta='\n\n[ConsoleVariables]\n; Native client/server World Partition visibility acknowledgements.\nwp.Runtime.UseMakingVisibleTransactionRequests=1\nwp.Runtime.UseMakingInvisibleTransactionRequests=1\nLevelStreaming.DefaultAllowClientUseMakingVisibleTransactionRequests=1\n'
base=subprocess.check_output(['git','show','HEAD:Config/DefaultEngine.ini'])
current=p.read_bytes()
assert b'wp.Runtime.UseMakingVisibleTransactionRequests=' not in base
assert b'wp.Runtime.UseMakingVisibleTransactionRequests=' not in current
p.write_bytes(current.rstrip()+delta.encode())
staged=base.rstrip()+delta.encode()
blob=subprocess.check_output(['git','hash-object','-w','--stdin'],input=staged).decode().strip()
subprocess.run(['git','update-index','--cacheinfo','100644',blob,'Config/DefaultEngine.ini'],check=True)
print('Staged native acknowledgement settings only; unrelated engine config remains unstaged.')
