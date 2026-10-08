"""Read-only receipt and accepted-content preservation audit outside Unreal."""
from pathlib import Path
import subprocess,json,hashlib,datetime
root=Path(__file__).resolve().parents[3];out=root/'Docs/Gate9Results'
def git(*args):return subprocess.check_output(['git','-c','core.fsmonitor=false',*args],cwd=root)
names=['foundation-input','ai-medical-loop','infected-hearing-cancel','combat-stress','combat-pickup-storage','magazine-contract','infected-navigation','saved-audit']
names += [case+'_'+role for case in ['combat_regions','combat_emulated','reload_contention_disconnect','infected_attacks_emulated','rv_controls_host','moving_armed_host_emulated','moving_armed_client','storage_survival_client','resource_guard_host','resource_guard_client'] for role in ['server','client']]
receipts=[]
for name in names:
 data=json.loads((out/(name+'.json')).read_text());rows=data['results']
 receipts.append({'file':name+'.json','recorded_checks':len(rows),'failed':[r['case'] for r in rows if not r['pass']]})
maps=git('ls-tree','-r','--name-only','3256c27','--','Content/Maps').decode().splitlines();changed=[]
for name in maps:
 if hashlib.sha256(git('show','3256c27:'+name)).digest()!=hashlib.sha256((root/name).read_bytes()).digest():changed.append(name)
old_changes=git('diff','3256c27','--name-status','--','Content').decode().splitlines()
modified_old_content=[line for line in old_changes if not line.startswith('A\t')]
vendor=json.loads((out/'vendor-final.json').read_text());preferences=json.loads((out/'persisted-editor-preferences.json').read_text())
summary={'checked_at':datetime.datetime.now().isoformat(),'receipts':receipts,'all_selected_current_receipts_pass':all(not r['failed'] for r in receipts),'accepted_map_baseline':'3256c27','accepted_map_files':len(maps),'changed_accepted_maps':changed,'modified_or_deleted_accepted_content':modified_old_content,'vendor_files':vendor['count'],'vendor_changed':vendor['changed'],'editor_preferences_restored':preferences['closed_editor_config_restoration']}
(out/'final-evidence.json').write_text(json.dumps(summary,indent=2))
assert summary['all_selected_current_receipts_pass'] and not changed and not modified_old_content and vendor['count']==108 and not vendor['changed']
print('Selected current receipts pass; all accepted content/maps preserved; 108 vendor hashes match.')
