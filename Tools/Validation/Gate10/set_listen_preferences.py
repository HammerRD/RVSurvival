"""Run with editor CLOSED. Preserve other native preferences and backup bytes."""
from pathlib import Path
import re,datetime
root=Path('D:/GitHub/RVSurvival/RVSurvival');p=root/'Saved/Config/WindowsEditor/EditorPerProjectUserSettings.ini';b=p.read_bytes();s=b.decode('utf-8-sig');bom=b.startswith(b'\xef\xbb\xbf')
(root/'Saved/Gate10Validation'/('PIE-before-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'.ini')).write_bytes(b)
head='[/Script/UnrealEd.LevelEditorPlaySettings]';start=s.index(head);end=s.find('\n[',start+len(head));end=len(s) if end<0 else end;section=s[start:end]
assert re.search(r'(?m)^PlayNetMode=',section)
section=re.sub(r'(?m)^PlayNetMode=[^\r\n]*','PlayNetMode=PIE_ListenServer',section);s=s[:start]+section+s[end:];p.write_bytes((b'\xef\xbb\xbf' if bom else b'')+s.encode('utf-8'))
print('Native listen-server preference saved; original backed up.')
