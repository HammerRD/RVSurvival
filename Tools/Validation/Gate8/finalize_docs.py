"""Close documentation only after the remaining runtime and saved-state receipts pass."""
from pathlib import Path
import json, subprocess
root=Path(__file__).resolve().parents[3]
results=root/'Docs/Gate8Results'
if (results/'bounded-closure-coverage.json').exists():
    raise RuntimeError('Historical initial-closure writer: preserve the subsequent qualified bounded-closure record')
required=[results/'saved-audit.json',results/'resources_server.json',results/'resources_client.json']
for case in ['recovery_host_100ms_2loss','final_physical_host_100ms_2loss','mechanical_missing_tool_100ms_2loss']:
    required.extend(results/'MechanicalRegression'/f'{case}_{role}.json' for role in ['server','client'])
coverage=[]
for path in required:
    data=json.loads(path.read_text(encoding='utf-8-sig'))
    rows=data['results'];assert rows and all(r['pass'] for r in rows),str(path)
    coverage.append({'receipt':str(path.relative_to(root)).replace('\\','/'),'passed_checks':len(rows)})
vendor=json.loads((results/'vendor-final.json').read_text());assert vendor['count']==108 and not vendor['changed']
preferences=json.loads((results/'persisted-editor-preferences.json').read_text());assert preferences['closed_editor_config_restoration'] and not preferences['network_emulation_enabled']
def git(*args):return subprocess.check_output(['git','-c','core.fsmonitor=false',*args],cwd=root).decode().splitlines()
files=sorted(set(git('diff','--name-only','0b6eff6','--','Source','Content','Docs','Tools')+git('ls-files','--others','--exclude-standard','--','Source','Content','Docs','Tools')))
(results/'changed-files.json').write_text(json.dumps({'baseline':'0b6eff6','files':files},indent=2)+'\n')
(results/'final-coverage.json').write_text(json.dumps({'status':'ACCEPTED','final_closure_receipts':coverage,'vendor_files_unchanged':108,'scope':'Gate 8 only; failed and inconclusive historical receipts remain identified in validation notes'},indent=2)+'\n')
path=root/'Docs/GATE_8_VALIDATION.md';text=path.read_text()
text=text.replace('Status: **IN PROGRESS — NOT ACCEPTED**. Authorized 2026-10-08. Gate 9 is not started.','Status: **ACCEPTED — 2026-10-08**. Gate 9 is not started.\n\n## Final closure\n\nMedical foundation passed single-player, actual Windows client UI, both healer roles, both moving driver/passenger roles, and separate-process 100 ms / 2% tests. Native controls exercised E, F9, movement, seats, rest, storage and recovery. Final roof/door physical route and saved reload of all eight maps passed. All 108 vendor files match accepted checkpoint 0b6eff6. Final source build succeeded; final editors stopped PIE and exited cleanly. Persisted PIE settings are restored to standalone one player, no child automation and no emulation.\n\nEvidence and exact scope follow below. Earlier progress/pending statements are historical milestones, superseded by this closure. Failed original/inconclusive receipts are retained rather than silently converted to passes. See Gate8Results/final-coverage.json and changed-files.json.\n\nCheckpoint history: 602ceb1 foundation; 803e970 station/content; 5f1d6ba teammate stabilization; 4f1e4a6 moving/interruption/stress; 734eb6a actual client controls; 52766f7 seated-driver UI/visibility; 6a9cc0c stabilized recovery and regressions; final closure commit recorded by Git.')
path.write_text(text)
path=root/'Docs/MEDICAL.md';text=path.read_text().replace('# Medical foundation (Gate 8, validation in progress)','# Medical foundation (Gate 8 accepted)')
text=text.replace('See `GATE_8_VALIDATION.md` for actual results, failed harness attempts and remaining\nacceptance work. This architecture document does not claim the gate is accepted.','See `GATE_8_VALIDATION.md` for accepted results, exact test scope, retained failed\nharness attempts and prototype limitations. Gate 9 is not started.')
path.write_text(text)
for name in ['GAME_DESIGN','TECHNICAL_ARCHITECTURE','NETWORKING','RV_SYSTEM','INVENTORY','ROADMAP']:
    path=root/'Docs'/f'{name}.md'
    text=path.read_text()+'\n\n## Gate 8 closure — 2026-10-08\n\nGate 8 medical/injury foundation is ACCEPTED. PlayerState-owned GAS attributes and reusable health/treatment components preserve accepted inventory, needs, seats, moving interior, resources, mechanical systems and prototype recovery. Both healer/driver roles, actual client UMG controls, impaired separate-process networking, transaction stress, recovery simulation, prior-gate representatives and saved-content/vendor audits passed within the documented scope. See GATE_8_VALIDATION.md and MEDICAL.md for architecture, failed history and limitations. Gate 9 is not started. Earlier pending/unauthorized statements describe historical checkpoints.\n'
    path.write_text(text)
path=root/'Docs/CHANGELOG.md'
with path.open('a') as f:
    f.write('\n\n### Gate 8 accepted — final closure, 2026-10-08\n\nCompleted medical GAS/component/data-asset foundation, injury state, authoritative timed self/teammate treatments, medication, downed/stabilization/revive, station/storage integration and remappable F9 UMG. Fixed unpossessed-driver patient lookup, DriverChair-obstructed medical ray and post-revive deterioration. Final impaired separate-process recovery and roof/door routes passed; saved map reloads and 108 vendor hashes passed; final build and clean shutdown recorded. Original failed timing/display fixtures retained with resolving evidence. Local milestone commits are listed in GATE_8_VALIDATION.md; no Gate 9. Known pre-existing config/solution changes excluded.\n')
print('Gate 8 closure documentation written after required passing receipts')
