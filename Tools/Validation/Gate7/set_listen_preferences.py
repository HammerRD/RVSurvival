"""Closed-editor native config: private PIE enum is not exposed to Python."""
from pathlib import Path
import re,datetime
r=Path('D:/GitHub/RVSurvival/RVSurvival')
p=r/'Saved/Config/WindowsEditor/EditorPerProjectUserSettings.ini'
b=p.read_bytes();s=b.decode('utf-8-sig');bom=b.startswith(b'\xef\xbb\xbf')
backup=r/'Saved/Gate7Resume'/('PIE-before-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'.ini');backup.write_bytes(b)
head='[/Script/UnrealEd.LevelEditorPlaySettings]'
start=s.index(head);end=s.find('\n[',start+len(head));end=len(s) if end<0 else end
section=s[start:end]
assert re.search(r'(?m)^PlayNetMode=',section)
section=re.sub(r'(?m)^PlayNetMode=[^\r\n]*','PlayNetMode=PIE_ListenServer',section)
s=s[:start]+section+s[end:];p.write_bytes((b'\xef\xbb\xbf' if bom else b'')+s.encode('utf-8'))
print('Closed-editor PIE mode set to listen server; backup preserved.')
