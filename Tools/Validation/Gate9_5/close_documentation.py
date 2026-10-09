"""Close validated Gate9.5; preserve existing legacy document bytes."""
from pathlib import Path
import json, subprocess
r=Path('D:/GitHub/RVSurvival/RVSurvival');d=r/'Docs';e=d/'Gate9_5Results';b=r/'Saved/Gate9_5Validation'
for name in ['moving_regression','resource_rates_final']:
 for role in ['server','client']:
  data=json.loads((b/f'{name}_{role}.json').read_text())
  assert all(x['pass'] for x in data['results']), (name,role)
  (e/f'{name}_{role}.json').write_text(json.dumps(data,indent=2))
assert json.loads((e/'final-saved-audit.json').read_text())['saved']
assert 'Result: Succeeded' in (e/'final_build.txt').read_text()
assert json.loads((e/'vendor-resume.json').read_text())['changed']==[]
note='''
## Final closure - 2026-10-09

Gate 9.5 is ACCEPTED at prototype quality. Gate10 has not started. Earlier pending statements above describe historical checkpoints, not the final state.

### Implemented architecture

Native Enhanced Input User Settings is the single binding store: MapPlayerKey, ApplySettings and AsyncSaveSettings. Native UMG controls use the existing restrained theme, grouped remappable actions, conflict warning/intentional confirmation, defaults, sensitivity and invert. Mouse/stick axis rows use UComboBoxString with readable themed entries because UInputKeySelector cannot capture mouse motion. Keyboard remapping was manually exercised; controller-compatible key/axis configuration was exercised, but physical controller hardware was not tested. No development controls appear in the normal menu. HUD/panel help reads the current profile; a read-only PlayerController binding-label wrapper supports future Blueprint prompts.

URVDifficultyProfile Primary Data Assets configure 16 bounded factors. Replicated ARVGameState snapshot/revision and owned PlayerController requests enforce host-only changes; client UI is read-only. Presets Relaxed/Standard/Harsh and Custom feed existing needs, GAS medical, infected, fuel, generator, cooling and engine wear. Loot/population remain clearly marked configuration preparation. Shared rules reset per PIE/session; lobby/dedicated-server administration and world-save persistence remain future work. Personal preferences never alter authoritative rules.

FRVCombatItemSpec contains configurable grip, support hand, sight/eye-relief, muzzle/ejection, holster and FP/TP offsets. M1911 is .45 ACP with seven-round magazines, separate from retained 9mm. Final grip (-14,-1.5,3.5) cm, rear-sight reference (3.1,0,6.35) cm/pitch .16/yaw180, eye relief30cm, muzzle(-15.5,0,4) cm/yaw180. Cosmetic owner ADS blends the mesh through actual rear/front sights and solves hand IK in the project-side Animation Blueprint; reticle hides when settled. Server hit validation remains independent of visual offsets. Reload disables IK and holster restores FOV90. Crowbar grip(-11,-1.5,-8) cm. Holster attachment data is prepared; unequipped weapons currently hide rather than displaying final holstered equipment.

Project-side ABP/profile reuse Epic locomotion, slot/montages and native TwoBoneIK/ModifyBone nodes. Melee-ready uses Epic raised armed locomotion; prototype shove/crowbar montages show the attack. No CharacterMovement, movement-base or character replication rewrite. Per-weapon visual data remains replaceable. Capsule remains movement collision.

Ordinary pickups default to tap; carried battery remains a .5-second hold. Accepted treatment/revive/repair/bed actions retain their durations. One inventory/equipment GUID system supports firearm and crowbar. Melee owned RPC validates state, revision/request, range, cooldown and geometry; sphere sweep plus occlusion ray yields one hit per attack. Shove is short-range/low damage with infected stagger; crowbar has one light attack. Effort uses existing fatigue and exhaustion scaling. No new stamina system, heavy combos, final durability or tool utility.

### Actual validation and evidence

* Single-player native inputs: foundation-input.json and feature-input.json passed handgun equip/reload/fire/conservation, tap pickup, retained timed hold/cancel/no-repeat, shove, crowbar, cooldown, range, wall obstruction, fatigue, difficulty contract and invalid request.
* Real Settings UI: remapped Fire Q then M, Interact P, Melee N and RV accelerate Y; actual firing/melee inputs worked. Conflict warning persisted correctly. Clean restart loaded bindings; Restore Defaults restored LMB/B/E/W. Native controller-axis dropdown selection saved, then defaults restored MouseX. Personal bindings are now defaults after this test. binding-label-probe.json verified immediate Q, settled Q, and reset Left Mouse Button.
* Real UI difficulty: fuel slider moved mode to Custom; Relaxed displayed .70x needs. Saved audit loaded all three profiles with16 valid bounded rules and ordered hunger factors. Server preset/Custom convergence and rejected client override passed in separate processes.
* Manual/rendered views: actual M1911 sights, ready/fire/reload/holster and crowbar ready/swing were inspected. Remote handgun/crowbar renders show full character/equipment. Prototype finger/hand contact and static slide/magazine presentation remain imperfect but usable. No paid asset or custom animation engine was introduced.
* network_emulated_server/client.json: separate-process listen server, configured outgoing100ms latency/2%loss, host/client reload/fire, independent ammo, client-local runtime FireQ without changing hostLMB, host Custom1.7 convergence, denied client difficulty, crowbar hit/cooldown. Passed. Runtime client remap was deliberately not saved because both local PIE processes share one Windows save directory.
* storage_regression_server/client.json: native E/3/T/Tab/G paths; moving pantry transfers during turns, both dinette seats/stand, exterior shared-container contention, drop/repick stableGUID/condition .62, capacity rejection, needs drain and owned consumption. Passed.
* moving_regression_server/client.json: client driver/host standing passenger under100ms/2%loss; low500cm/s, road1800cm/s, highway2700cm/s (about60mph), front/rear/sideways walking, standing, acceleration, turning, braking/resume, firing while riding,20 V-to-passenger/1-to-driver cycles. Passed without floor fall. Server/client reference-frame diagnostics reported0 corrections/max0cm. Speed phases use an explicitly recorded server physics fixture to bound coverage, not a claim of final handling tuning. Animation speed reached200cm/s while walking. Storage run also covered host driving/client interactions.
* resource_rates_final_server/client.json: healthy client normal-E panel plus owned request changed InteriorLights; downed repeat left circuit/revision unchanged and cleared access. This supplies the formerly missing Gate8 healthy positive control. Native difficulty-effect fixture doubled hunger/thirst/fatigue rates: [80,80,20] -> Standard[79,78,20.6667], 2x[78,76,21.3333] over600 simulated seconds. This fixture checks effects, not UI authority (tested separately).
* final-saved-audit.json freshly loaded all new assets, saved dirty content/map and verified .45/7round/sightADS and profile data. final_build.txt succeeded Development Editor/Win64 (target up to date after prior successful changed-source builds). final_saved_editor.log and bounded regression logs ended with clean editor exit. Persisted PIE restored standalone/one-player/one-process/emulation-off/no child automation command.
* vendor-resume.json: all108RV source files SHA256 match0b6eff6. Prior accepted test maps preserved. Refrigerator collision remains deferred and unchanged.

### Failures, fixes and testing scope

Recovered pause checkpoint rather than recreating content. Fixed native key-selector restore recursion (warning was cleared by OnKeySelected re-entry), axis remapping capture limitation, stale hardcoded help, gun orientation/grip, ADS reticle/hand alignment, holster FOV restoration and low melee-ready hands. Earlier fixture misses/blocked rays and a killed melee target were diagnosed, not counted as passes. The added needs probe initially modified copies returned by an Unreal struct-array iterator; writing modified entries back into the array fixed the fixture. Initial final-regression launch used ExecutePythonScript, which exited before callbacks; using the established interactive py command path completed the bounded run. No world-leak suppression or gameplay authority relaxation. No resumed editor crash.

Risk-based regressions targeted interaction, inventory, survival tuning, seats/possession, moving interior, electrical controls, medical downed guard and combat/infected. Did not rerun every Gate1-9 map after pose/offset/style changes or repeat unrelated full stress matrices. No new claim of comprehensive long-duration coverage. Separate-process emulation was concentrated on affected authority/presentation states.

### Recovery/checkpoints and final scope

566ae69 acceptedGate9; 1c68a38 freeM1911; 27ed4d3 freecrowbar; 26762ed pauseWIP; fc94fa3 focused input; 002c5da and4020083 animation recoveryWIP; 9c66b41 settings/presentation recoveryWIP; 00788f2 emulated authority/binding checkpoint. Final closure checkpoint follows this document. Exact changed paths are recorded in Gate9_5Results/changed-files.txt.

Saved map: /Game/Maps/Gate9_5CombatRefinementTest. New project character ABP/profile/montages, combat game framework/presets/itemdefinitions/materials and imported free meshes/textures are confined to their Gate9_5/ThirdParty folders; accepted battery definition explicitly retains timed physical pickup. Original source archives remain preserved locally. Free-source/license/credit record: THIRD_PARTY_ASSETS.md (Xeradev FabStandard, RED2000 CC BY4.0).

Known limitations: prototype hand/finger/reload artwork, controlled montage rather than final melee animation, one light attack, physical controller hardware untested, session-only world difficulty, no dedicated-server/lobby UI, no final holstered equipment, refrigerator collision deferred. No world scavenging, procedural loot/population, hordes, extra weapon catalog, paid art or Gate10 implementation.

Pre-existing unrelated Config/DefaultEngine.ini, .vsconfig, Automation_RVSurvival.slnx and RVSurvival.slnx remain excluded. Raw editor logs/intermediate captures are preserved locally under Saved/Gate9_5Validation; curated receipts/render evidence are committed. Unreal and child PIE/build processes are closed before stopping. Recommended next task: manual Gate9.5 review using the saved map/settings; start Gate10 only after explicit authorization.
'''
p=d/'GATE_9_5_VALIDATION.md';s=p.read_text(encoding='utf-8');s=s.replace('Status: IN PROGRESS.','Status: ACCEPTED.',1);s=s.replace('## Required validation still pending','## Initial validation plan (historical)',1)
if '## Final closure - 2026-10-09' not in s:s+=note
p.write_text(s,encoding='utf-8')
ch='''\r\n\r\n## 2026-10-09 - Gate9.5 refinement accepted\r\n\r\nIntegrated free licensed .45ACP M1911 and CC-BY crowbar, per-weapon grip/sights/muzzle/FP-TP alignment, sight ADS/native hand IK, tap pickups with retained timed actions, themed native Enhanced Input remapping/persistence/conflicts/defaults, host-authoritative difficulty profiles/custom sliders and existing-system multipliers, short defensive shove and authoritative light crowbar melee with fatigue. Fixed key-selector recursion, grip direction/hand presentation and ADS-to-holster FOV restoration.\r\n\r\nNormal menu controls, restart persistence, remote renders, separate-process100ms/2%loss combat/difficulty/local bindings, moving storage/condition/identity/capacity/consume, about60mph moving character and20seat cycles passed. Passenger diagnostics0corrections in final run. Targeted healthy/downed resource guard now has a successful healthy control; doubled needs rates verified. Final saved-content audit/build/clean shutdown passed;108RV vendor hashes unchanged. Raw fixture failures retained, not counted as passes. Refrigerator collision and prototype animation/holstered visual limitations remain documented. Gate10 not started. See GATE_9_5_VALIDATION.md for evidence, source licenses, checkpoint history and known limitations.\r\n'''
p=d/'CHANGELOG.md';raw=p.read_bytes()
if b'Gate9.5 refinement accepted' not in raw:p.write_bytes(raw+ch.encode('ascii'))
p=d/'ROADMAP.md';raw=p.read_bytes();marker=b'Gate9.5 closure: ACCEPTED'
if marker not in raw:p.write_bytes(raw+b'\r\nGate9.5 closure: ACCEPTED at prototype quality; see GATE_9_5_VALIDATION.md. Gate10 has not started.\r\n')
paths=subprocess.check_output(['git','-c','core.fsmonitor=false','diff','--name-only','566ae69','--','Source','Content','Docs','Tools'],cwd=r).decode().splitlines()
(e/'changed-files.txt').write_text('\n'.join(paths)+'\n')
print('Gate9.5 validated closure documentation saved.')
