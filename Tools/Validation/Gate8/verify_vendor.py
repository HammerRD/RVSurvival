"""Compare purchased packages with the accepted Gate 7 checkpoint, without editing them."""
from pathlib import Path
import subprocess, hashlib, json, datetime
root=Path(__file__).resolve().parents[3]
def git(*args):
    return subprocess.check_output(['git','-c','core.fsmonitor=false',*args],cwd=root)
paths=git('ls-tree','-r','--name-only','0b6eff6','--','Content/RV').decode().splitlines()
changed=[]
for name in paths:
    expected=hashlib.sha256(git('show','0b6eff6:'+name)).digest()
    if not (root/name).is_file() or hashlib.sha256((root/name).read_bytes()).digest()!=expected:
        changed.append(name)
receipt={'baseline':'0b6eff6','count':len(paths),'changed':changed,'checked_at':datetime.datetime.now().isoformat()}
(root/'Docs/Gate8Results/vendor-final.json').write_text(json.dumps(receipt,indent=2))
assert len(paths)==108 and not changed,receipt
print('108 vendor files match the accepted checkpoint')
