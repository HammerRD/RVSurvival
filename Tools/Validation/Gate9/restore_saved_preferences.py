"""Normalize native editor config after the editor has exited, preserving other sections."""
from pathlib import Path
import re,json,datetime,hashlib
root=Path('D:/GitHub/RVSurvival/RVSurvival')
path=root/'Saved/Config/WindowsEditor/EditorPerProjectUserSettings.ini'
original=path.read_bytes();bom=original.startswith(b'\xef\xbb\xbf')
text=original.decode('utf-8-sig');newline='\r\n' if '\r\n' in text else '\n'
backup=root/'Saved/Gate9Validation'/('EditorPreferences-before-cleanup-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'.ini')
backup.write_bytes(original)
heading='[/Script/UnrealEd.LevelEditorPlaySettings]'
match=re.search(r'(?m)^'+re.escape(heading)+r'\r?\n',text)
assert match,'Missing native PIE settings section'
next_section=re.search(r'(?m)^\[',text[match.end():])
end=match.end()+next_section.start() if next_section else len(text)
body=text[match.end():end]
updates={'PlayNumberOfClients':'1','RunUnderOneProcess':'True','PlayNetMode':'PIE_Standalone','bLaunchSeparateServer':'False','AdditionalLaunchParameters':''}
for key,value in updates.items():
 pattern=r'(?m)^'+re.escape(key)+r'=[^\r\n]*'
 if re.search(pattern,body):body=re.sub(pattern,key+'='+value,body)
 else:body=body.rstrip('\r\n')+newline+key+'='+value+newline+newline
body=re.sub(r'(?m)^(NetworkEmulationSettings=[^\r\n]*)',lambda m:m[1].replace('bIsNetworkEmulationEnabled=True','bIsNetworkEmulationEnabled=False'),body)
assert 'bIsNetworkEmulationEnabled=False' in body
changed=text[:match.end()]+body+text[end:]
path.write_bytes((b'\xef\xbb\xbf' if bom else b'')+changed.encode('utf-8'))
verified=path.read_text(encoding='utf-8-sig')
assert all(re.search(r'(?m)^'+re.escape(k)+'='+re.escape(v)+r'\r?$',verified) for k,v in updates.items())
assert 'Saved/Gate9Validation/process_startup.py' not in body.replace('\\','/')
receipt={'closed_editor_config_restoration':True,'native_section':heading,'values':updates,'network_emulation_enabled':False,'backup':str(backup),'file_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'checked_at':datetime.datetime.now().isoformat()}
(root/'Docs/Gate9Results/persisted-editor-preferences.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print('Persisted standalone one-player/one-process PIE; no test launch command; emulation disabled. Other sections preserved.')

