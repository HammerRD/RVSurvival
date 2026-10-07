"""Evidence-driven validation closure; never infer manual acceptance from diagnostics."""
from pathlib import Path
import json
root=Path('D:/GitHub/RVSurvival/RVSurvival');docs=root/'Docs/Gate6PhysicalRefinement';saved=root/'Saved/Gate6PhysicalRefinement'
rows=[];metrics=[]
for path in sorted(docs.glob('*_server.json')):
 name=path.name[:-12];client=docs/(name+'_client.json')
 if not client.exists():continue
 pair=[json.loads(p.read_text(encoding='utf-8-sig')) for p in [path,client]]
 counts=[len(p['results']) for p in pair];failed=[sum(not c['pass'] for c in p['results']) for p in pair]
 rows.append({'suite':name,'server_checks':counts[0],'client_checks':counts[1],'failed':failed,'pids':[p['pid'] for p in pair],'source_checkpoints':[p.get('source_checkpoint') for p in pair],'module_sha256':[p.get('module_sha256') for p in pair],'evidence_kind':[p.get('evidence_kind') for p in pair]})
 for role in ['server','client']:
  raw=saved/(name+'_'+role+'.json')
  if raw.exists():
   data=json.loads(raw.read_text(encoding='utf-8-sig'));samples=data.get('samples',[])
   # Raw metrics include fixture and intentional seat/bed/ladder transitions.
   seen={};timeline=[]
   for s in samples:
    who=s.get('who');count=s.get('corrections',0)
    if count!=seen.get(who,0):timeline.append({'t':s.get('t'),'who':who,'count':count,'max_cm':s.get('max_correction'),'position':s.get('pos')});seen[who]=count
   measured=[s['max_correction'] for s in samples if 'max_correction' in s]
   metrics.append({'suite':name,'role':role,'samples':len(samples),'raw_max_correction_cm':max(measured) if measured else None,'peak_speed_cm_s':max((s.get('speed',0) for s in samples),default=0),'correction_timeline':timeline})
summary={'status':'NOT ACCEPTED - manual hold routes and transition smoothness unresolved','evidence_kind':'diagnostics, not full manual acceptance','suites':rows,'metrics':metrics}
(docs/'final-test-summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
table='\n'.join('| '+r['suite']+' | '+str(r['server_checks'])+' / '+str(r['client_checks'])+' | '+str(r['failed'])+' |' for r in rows)
assessment=json.loads((docs/'transition-correction-assessment.json').read_text())
transition_table='\n'.join('| '+run['suite']+' | '+p['phase']+' | '+str(p['first_event_s'])+'–'+str(p['last_event_s'])+' | '+str(p['native_correction_events'])+' | '+str(p['max_native_report_cm'])+' |' for run in assessment['runs'] for p in run['phases'] if p['begin_s']>=13.6 and p['max_native_report_cm']>75)
raw_physical=[]
for name in ('physical_host_100ms_2loss','physical_client_100ms_2loss'):
 data=json.loads((saved/(name+'_client.json')).read_text(encoding='utf-8-sig'))
 samples=[s for s in data['samples'] if s['t']>14]
 raw_physical.append(name+': '+str(max(s['corrections'] for s in samples))+' cumulative events / '+str(round(max(s['max_correction'] for s in samples),2))+'cm native maximum')
raw_physical_summary='; '.join(raw_physical)
regression_rows=[]
for label,file in [('Earlier Gate5 entry/front shell','regression-refined-entry.json'),('Gate1 interaction','Gate1Regression/summary.json'),('Gate2 strengthened vehicle','Gate2Regression/shared.json'),('Gate2 inventory/possession','Gate2Regression/inventory-possession.json'),('Gate4 inventory','regression-inventory.json'),('Gate5 needs','regression-needs.json')]:
 data=json.loads((docs/'Regressions'/file).read_text(encoding='utf-8-sig'))
 records=data if isinstance(data,list) else data.get('results',data.get('checks'))
 count=records if isinstance(records,int) else len(records)
 failed=0 if isinstance(records,int) and data.get('pass') else sum(not r['pass'] for r in records) if isinstance(records,list) else 1
 regression_rows.append({'suite':label,'checks':count,'failed':failed,'receipt':file})
(docs/'regression-summary.json').write_text(json.dumps(regression_rows,indent=2)+'\n',encoding='utf-8')
regression_table='\n'.join('| '+r['suite']+' | '+str(r['checks'])+' | '+str(r['failed'])+' |' for r in regression_rows)
section='''
## Gate 6 physical-entry, seating and roof refinement - 2026-10-07

**Status: NOT ACCEPTED for this additional refinement; complete manual held-key validation and transition-smoothness assessment remain unresolved.** Historical accepted Gate6/Gate7 records above are preserved. Existing Gate7 checkpoint c8e28ff is paused; no Gate7 resumed or later gate started. Engine association recovery fce8422 uses canonical5.8 and opened UE5.8.3 without the Convert Project dialog. Epic Launcher metadata confirms UE_5.8 at D:/Epic Games/UE_5.8, version5.8.3-58210709. Native DesktopPlatform enumeration resolves that entry as5.8; it does not require the absent legacy HKLM engine key. See engine-association-verification.json.

### Root causes and saved changes

- Dinette sleep contamination was an explicitly saved ARVRestPoint named Dinette rest at (45,-28,155), configured by an old layout script. Removed that actor from Gate6FuelElectricalTest. Both real dinette cushions use the authoritative reusable seats, never BeginRestAuthority. The actual rear bed is the sole rest actor in the saved map. Bed pose/wake mechanics remain accepted; sitting remains Awake and does not invoke sleep recovery.
- Physical doorway blockage was the KitchenCabinet proxy extending to x85 into the stepwell. New centre(5,80,130), extent(50,35,43), ends at x55 beside the well. Closed door, sampled swing safety, shell/front/firewall, floor and furniture collision remain. EntryStepLow is visible; middle/high collision follows the purchased step geometry. Native tagged moving bases naturally reduce capsule radius34->30 and walking speed on the steps/interior, restoring world values on exit. bPhysicalDoorEntry suppresses normal aisle-teleport markers in the Gate6 derivative. Normal open-door entry/exit is physical; no character placement shortcut is used after the diagnostic's initial approach fixture.
- Cab RearInterior defaults to3 and is remappable. Passenger release supports the accepted moving frame; driver release requires effectively stopped speed (new tunable MaxDriverCabDepartureSpeed10cm/s). Existing full-capsule/supported aisle validation precedes releasing occupancy. Native release restores possession, movement, collision, base, camera and input. Invalid placement retains the seat. Available cab/rear seats remain normal E interactions; occupied seats reject.
- Ladder originally deliberately rejected the upper exit and stopped climbing at180cm. New parked roof access uses replicated ladder/roof state, native CMC flying/plane constraints and validated rail/ground/roof capsule sweeps. ClimbHeight335.6 accounts for the actual88cm half-capsule. Roof dismount lands near(-315,75), on support measured at319.6cm (vendor triangle319.5916). RoofWalkMain is fitted to actual roof height; separate AC, rear/middle/back-left vents and pipe collision match measured fixtures. Their walkable tops retain the native RV frame. E at top restores walking; hold E at the upper ladder query reserves return, S descends, E at bottom restores world movement. Per-character weak propulsion locks remain while on the roof and release on descent/disconnect. No floating platform, vendor edit, custom prediction or transform-forcing movement solution.
- Original input had transient Enhanced Input contexts but no implemented remapping menu;1/2/V used fixed-key polling. RVInputMappings, URVControlsWidget and URVControlRowWidget now use native player-mappable metadata, UEnhancedInputUserSettings profiles and UMG InputKeySelector. F10 opens, Escape/Return closes, native settings save remaps. A passive controller-owned driving catalog exposes defaults before first possession without applying input. Cab/door/bed/survival hints follow local bindings. Initialization registration retries idempotently; teardown unregisters contexts and removes widgets. No separate key-save framework.
- Telemetry additionally found repeated autonomous CharacterMovement corrections while a passenger was seat-attached in MOVE_None. Native CMC deactivation now protects the authoritative seated transform, rejects stale character-move/adjustment RPCs through engine IsActive guards, then Activate(true) restores simulation before standing. A tick-only attempt left stale RPC corrections; restoring a cached remote-proxy tick flag left outside floor/reference-frame state stale. Both failed attempts are retained. Seated walking input is cleared/ignored. Server authority and world/interior correction rules remain enabled. Subsequent native20-cycle/highway/bed regression results are distinguished from earlier physical-route receipts and are followed by final-source physical reruns.

Saved content is limited to Gate6FuelElectricalTest and BP_ClassCSystemsMotorhome. Current configuration69actors; the removed Dinette rest was the70th. All prior maps/fallbacks, seven exterior compartments, vendor108files, Chaos tuning and existing Gate7 content are preserved. See configured.json and source-content-manifest.txt.

### Actual native-window evidence versus diagnostics

Actual supported Windows input opened F10 Controls and closed it with Escape; default3 restored the stopped driver to a validated aisle. Actual UI rebound RearInterior to Num3, native Num3 executed the transition, and the test binding was restored to3. Rear-bed use was entered with held-input diagnostics, then visibly inspected in the horizontal prototype/head view; actual Z selected Sleeping and R restored safe Awake walking. After diagnostic climbing, actual E performed roof dismount and actual E performed bottom dismount. Roof/furniture/steps were viewed in the purchased geometry.

The supported sky API provides key taps/chords, not a key-down/key-up hold. It cannot perform an uninterrupted hardware E hold or a sustained W/S walk/climb. Native-held-input diagnostics do exercise the real Enhanced Input bindings, accepted interaction trace/duration/RPC path and CMC physical routes; they are not claimed as full manual-player acceptance. Initial approach fixtures are labeled, as are isolated inventory/exterior regression fixtures. No direct completion/seat/rest RPC is used as a control shortcut in the new physical route.

### Separate-process diagnostic results

Both endpoint PIDs differ. Emulated cases use explicit native NetEmulation.PktLagMin100/PktLagMax100/PktLoss2 on both endpoints, as well as PIE settings. Counts are targeted checks, not manufactured stress totals. Receipts list each result and raw Saved samples/logs remain available.

| Suite | Server / client checks | Failures [server,client] |
|---|---|---|
'''+table+'''

The physical routes cover open-door steps/entry, cab E, occupied1 rejection, passenger3 while moving, moving driver3 rejection, both Dinette seats Awake, bed/Z/R and player independence, stopped driver3, rear-to-cab E, physical exit, roof walking/return/down, propulsion lock, closed-door block, backing clear of swing, re-entry and front/rear/back-out walking. Roof/ladder disconnect cases verify reservation release, remaining Awake player and resumed propulsion. Native20-cycle, stations/door/storage/resource/prior-gate regression receipts are recorded separately when executed.

Raw measured correction/speed summaries are in final-test-summary.json. Final raw post-reset client metrics: '''+raw_physical_summary+'''. These include seat release, rest/ladder placements and doorway/base changes, not only initial fixture setup. The host impaired physical route resets diagnostics after initial seating only. Sampled steady-window correction changes and seat offsets are recorded in correction-comparison.json; relative seat offsets are explicitly checked below1cm. Brief transition correction bursts remain a measured limitation requiring visual held-key review; they are not dismissed as setup or certified invisible. Complete human usability is not inferred from counters.

The unchanged legacy checks use75cm with network emulation and30cm without it, after resetting diagnostics for steady highway/turn walking or moving workstation use. Original Gate3 explicitly excluded initial fixtures and transitions from steady-driving claims. Native20-cycle and station steady phases still pass those original checks. They do **not** certify transition smoothness. The following final-code transition reports exceed75cm; no broader transition threshold was invented:

| Run | Phase | Approximate event seconds | Events | Maximum native report cm |
|---|---|---|---|---|
'''+transition_table+'''

Full per-phase events and adjacent vehicle-local position changes are in transition-correction-assessment.json. This native metric compares an acknowledged saved move with a correction target; matching-base relative coordinates are used only when bases agree. Intentional authoritative seat/bed/ladder placements are distinct from ordinary walking, but cached acknowledgements or unsolicited displacement cannot be separated reliably by aggregate counters. Occupancy, supported destinations and sampled seated offsets pass; **transition visual smoothness remains unresolved**, not accepted as an expected cosmetic effect. A sustained-key visual run must verify it, and further engineering is required if that run shows unusable snaps/jitter.

### Failures, recovery and limits

Fresh representative prior-gate results:

| Regression | Checks | Failures |
|---|---|---|
'''+regression_table+'''

Gate3 moving-interior, natural frame entry/exit and station regression are covered by the physical/native/station suites above. Fuel/electrical31server/29client checks also passed with separate processes and emulation. Both driver-role storage runs preserve quantity, condition and GUID identity through moving pantry transfer and shared exterior contention. Door43/43 checks preserve single door/glass visuals and matching collision.

One original Gate2 blocked_exits_retain_seat check failed (23of24passed). That legacy helper did not assert successful driver re-entry before testing blocked exits, so the result cannot distinguish failed approach/re-entry from an unsafe release. No production exit code was changed. The retained failed receipt is Regressions/FailedAttempts/Gate2-legacy-blocked-exit.json; exact first-failure root cause remains unestablished. An unchanged-expectation diagnostic repeat passed26/26; two added coverage/restoration repeats passed29/29 each; the final strengthened repeat passed30/30, checking possession, vehicle-controller/PC linkage, occupied seat, six candidate rays covered, actual Pawn/Visibility blocking responses, rejection retaining the seat and clear exit restoring active/ticking walking and capsule collision. These do not retroactively prove the first failure was fixture-only.

Failed diagnostic attempts are retained under Saved/Gate6PhysicalRefinement/History. They exposed insufficient braking before parked bed tests, a player blocking a cab sightline, a navigation helper continuing to override aim at an obstructed approach, and reopening from inside the door swing. Corrected the harness to brake to a real stop, stop navigation before aiming, approach from a supported aisle, clear the sightline and physically back away before reopening. Gameplay guards were not bypassed. The observer also needed to read driver needs from the possessed vehicle's PlayerState rather than the unpossessed character. Disconnect callback release initially resumed a loop after clearing its globals; it now returns immediately, and clean repeats are required. Early helper finish ordering and two C++ API/shadowing/Slate dependency build errors were fixed; subsequent builds pass. No world-leak detection suppression or forced process kill.

build-native-seat-reactivation.log records the meaningful lifecycle compile. build-final.log records Development Editor/Win64 Succeeded after Git working-set changes rebuilt the unity module without gameplay source changes. The two final physical impaired role combinations were refreshed against that final DLL; other complete suites tested the same source checkpoint6760ed3 before the final relink. Receipts preserve module hashes and source provenance rather than implying identical binaries. Final network tests require clean Python/fatal/world-leak scans and normal editor shutdown. All launched editors/PIE sessions exited normally; no force kill or world-leak detection suppression. Original108SHA256 verification and saved map/BP hashes are in vendor-integrity.json and saved-state-verification.json. Only Gate6FuelElectricalTest and BP_ClassCSystemsMotorhome differ from baselinefce8422. Working tree excludes pre-existing DefaultEngine.ini/.vsconfig/Automation_RVSurvival.slnx/RVSurvival.slnx; the engine file is not printed or committed. Recovery checkpoints:a6d64ba,da75110(WIP),329bfce,4a94608,d3d93de,f40a691,f547152,05294c1(superseded tick-only attempt),6760ed3(native lifecycle); final closure hash is in Git/final report.

Final saved-state/editor-preference inspection reconfirmed69actors, sole Rear bed, physical entry,319.6cm roof, fitted cabinet and roof-enabled ladder without starting PIE. Cleanup exposed Python limitations for the private PlayNetMode enum: exported-name, integer and getter conversions failed, leaving the editor open but no PIE running; all errors remain in final-editor-preferences.log. Supported settings, Save All and normal quit then completed. Python property edits did not persist PIE preferences, so with Unreal confirmed closed the native Saved/Config/WindowsEditor/EditorPerProjectUserSettings.ini section was restored canonically to PIE_Standalone,1client,one-process,no separate server,empty AdditionalLaunchParameters and disabled emulation. Other sections were preserved and the prior file backed up under Saved. Persisted-editor-preferences.json records the actual file verification; final-editor-preferences.json alone is only in-memory evidence. No test script will be automatically launched by the remaining child-launch setting. Editor/PIE are stopped; no resource-intensive test automation remains.

Remaining intended limits: parked bed; stopped seat-to-seat switching; effectively stopped driver-to-rear; parked ladder/roof with propulsion interlock; prototype sit/lie/climb presentation; roof edges have normal falling risk; no moving/rolled/steeply tilted/externally pushed roof, packaged or dedicated-server certification. Complete new manual-player acceptance remains unfinished.

### Required Bobby follow-up before acceptance / any Gate7 work

Open the project through its5.8 association, then explicitly open /Game/Maps/Gate6FuelElectricalTest (do not use the pre-existing paused Gate7 map). Default PIE is now ordinary standalone1player/one-process/no emulation. F10 shows remappable bindings; current defaults:Einteraction/stand/dismount,1driver,2passenger,Vnext seat,3rear interior,Zrest/sleep,Rstand from bed,W/Swalk/climb,held right mouseorbit. For multiplayer choose2players,Play As Listen Server,Run Under One Process disabled; configure representative100ms/2% for the role checks below. No diagnostic launch command is present.

1. Open Gate6FuelElectricalTest, F10 check bindings, open the house door with a normal E hold from clear of its swing. Hold W up the visible step and through the doorway; walk front/rear/back and physically out, then close. Repeat on host and remote client.
2. Sit/stand each Dinette cushion using normal E holds: status must stay Awake. Hold E at the rear mattress, visibly lie down, use Z, R/E stand, walk away and exit; repeat in both roles.
3. Passenger3 while another player drives: stand safely, walk, then E into available cab/rear seats. Driver3 while moving must reject; after stopping it must restore aisle walking. Verify occupied rejection and ordinary V/1/2 seat controls.
4. Park, hold E at ladder, hold W to top, E onto the real roof, walk around fixtures, hold E at upper ladder, hold S down, E off; walk away. Repeat both roles with representative100ms/2% settings. No floor fall, stuck input/camera/collision or sleep contamination is acceptable.
5. In both host/client role combinations with100ms/2% settings, explicitly watch/record unwanted snaps or jitter during moving cab/Dinette release, rear-seat release, bed wake, ladder entry, roof dismount, upper-ladder return and ground dismount. Distinguish intended validated destination placement from any subsequent unsolicited movement. Use passenger and remote-observer views; correlate phase times with transition-correction-assessment.json. If transitions are unusable, return to this refinement for engineering rather than accepting them as cosmetic.
6. Retain the ambiguous initial Gate2 negative-exit result for investigation if it recurs. The stronger test must confirm driver possession/controller/seat ownership and all six genuinely blocked exit candidates before E, retain the occupied seat on rejection, then restore ordinary walking after blockers are removed. The original missing-prerequisite result is not a proven production defect or a proven fixture-only cause.

The remaining flows require a human sustained-key pass or a supported tool capable of real key holds. The current UI API only taps keys; aggregate native diagnostics cannot certify sustained-route visual transition smoothness. Manual coverage and technical transition-smoothness uncertainty are separate unresolved items. They are pending, not failed human tests and not presumed passes. Any observed defect returns to this refinement for engineering. Stop here; do not resume Gate7.
'''
p=root/'Docs/GATE_6_VALIDATION.md';old=p.read_bytes();marker=b'\n## Gate 6 physical-entry, seating and roof refinement - 2026-10-07'
if marker in old:old=old.split(marker,1)[0]
notice='''> **Current additional Gate6 refinement: NOT ACCEPTED yet - held-key manual-player routes and transition smoothness remain unresolved.** Earlier acceptance below is historical baseline evidence. Existing completed Gate7 checkpoint c8e28ff is preserved and paused; no Gate7 work was resumed by this refinement. See the final physical-entry/seating/roof section and Bobby checklist below.

'''.encode('utf-8')
if old.startswith(b'> **Current additional Gate6 refinement:'):old=old.split(b'\n\n',1)[1]
p.write_bytes(notice+old.rstrip()+section.encode('utf-8')+b'\n')
print('Recorded '+str(len(rows))+' diagnostic suites; manual acceptance remains pending.')
