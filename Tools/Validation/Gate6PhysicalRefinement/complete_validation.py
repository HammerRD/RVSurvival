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
 rows.append({'suite':name,'server_checks':counts[0],'client_checks':counts[1],'failed':failed,'pids':[p['pid'] for p in pair]})
 for role in ['server','client']:
  raw=saved/(name+'_'+role+'.json')
  if raw.exists():
   data=json.loads(raw.read_text(encoding='utf-8-sig'));samples=data.get('samples',[])
   # Raw metrics include fixture and intentional seat/bed/ladder transitions.
   metrics.append({'suite':name,'role':role,'samples':len(samples),'raw_max_correction_cm':max((s.get('max_correction',0) for s in samples),default=0),'peak_speed_cm_s':max((s.get('speed',0) for s in samples),default=0)})
summary={'status':'NOT ACCEPTED - full manual hold routes pending','evidence_kind':'diagnostics, not full manual acceptance','suites':rows,'metrics':metrics}
(docs/'final-test-summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
table='\n'.join('| '+r['suite']+' | '+str(r['server_checks'])+' / '+str(r['client_checks'])+' | '+str(r['failed'])+' |' for r in rows)
section='''
## Gate 6 physical-entry, seating and roof refinement - 2026-10-07

**Status: NOT ACCEPTED for this additional refinement; complete manual held-key validation is pending.** Historical accepted Gate6/Gate7 records above are preserved. Existing Gate7 checkpoint c8e28ff is paused; no Gate7 resumed or later gate started. Engine association recovery fce8422 uses canonical5.8 and opened UE5.8.3 without the Convert Project dialog.

### Root causes and saved changes

- Dinette sleep contamination was an explicitly saved ARVRestPoint named Dinette rest at (45,-28,155), configured by an old layout script. Removed that actor from Gate6FuelElectricalTest. Both real dinette cushions use the authoritative reusable seats, never BeginRestAuthority. The actual rear bed is the sole rest actor in the saved map. Bed pose/wake mechanics remain accepted; sitting remains Awake and does not invoke sleep recovery.
- Physical doorway blockage was the KitchenCabinet proxy extending to x85 into the stepwell. New centre(5,80,130), extent(50,35,43), ends at x55 beside the well. Closed door, sampled swing safety, shell/front/firewall, floor and furniture collision remain. EntryStepLow is visible; middle/high collision follows the purchased step geometry. Native tagged moving bases naturally reduce capsule radius34->30 and walking speed on the steps/interior, restoring world values on exit. bPhysicalDoorEntry suppresses normal aisle-teleport markers in the Gate6 derivative. Normal open-door entry/exit is physical; no character placement shortcut is used after the diagnostic's initial approach fixture.
- Cab RearInterior defaults to3 and is remappable. Passenger release supports the accepted moving frame; driver release requires effectively stopped speed (new tunable MaxDriverCabDepartureSpeed10cm/s). Existing full-capsule/supported aisle validation precedes releasing occupancy. Native release restores possession, movement, collision, base, camera and input. Invalid placement retains the seat. Available cab/rear seats remain normal E interactions; occupied seats reject.
- Ladder originally deliberately rejected the upper exit and stopped climbing at180cm. New parked roof access uses replicated ladder/roof state, native CMC flying/plane constraints and validated rail/ground/roof capsule sweeps. ClimbHeight335.6 accounts for the actual88cm half-capsule. Roof dismount lands near(-315,75), on support measured at319.6cm (vendor triangle319.5916). RoofWalkMain is fitted to actual roof height; separate AC, rear/middle/back-left vents and pipe collision match measured fixtures. Their walkable tops retain the native RV frame. E at top restores walking; hold E at the upper ladder query reserves return, S descends, E at bottom restores world movement. Per-character weak propulsion locks remain while on the roof and release on descent/disconnect. No floating platform, vendor edit, custom prediction or transform-forcing movement solution.
- Original input had transient Enhanced Input contexts but no implemented remapping menu;1/2/V used fixed-key polling. RVInputMappings, URVControlsWidget and URVControlRowWidget now use native player-mappable metadata, UEnhancedInputUserSettings profiles and UMG InputKeySelector. F10 opens, Escape/Return closes, native settings save remaps. A passive controller-owned driving catalog exposes defaults before first possession without applying input. Cab/door/bed/survival hints follow local bindings. Initialization registration retries idempotently; teardown unregisters contexts and removes widgets. No separate key-save framework.

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

Raw measured correction/speed summaries are in final-test-summary.json. Raw maxima include setup and intentional validated transitions; they must not be interpreted as continuous walking jitter. The host impaired physical route resets diagnostics after initial seating only, with native debug logging retained. Complete human usability is not inferred from counters.

### Failures, recovery and limits

Failed diagnostic attempts are retained under Saved/Gate6PhysicalRefinement/History. They exposed insufficient braking before parked bed tests, a player blocking a cab sightline, a navigation helper continuing to override aim at an obstructed approach, and reopening from inside the door swing. Corrected the harness to brake to a real stop, stop navigation before aiming, approach from a supported aisle, clear the sightline and physically back away before reopening. Gameplay guards were not bypassed. The observer also needed to read driver needs from the possessed vehicle's PlayerState rather than the unpossessed character. Disconnect callback release initially resumed a loop after clearing its globals; it now returns immediately, and clean repeats are required. Early helper finish ordering and two C++ API/shadowing/Slate dependency build errors were fixed; subsequent builds pass. No world-leak detection suppression or forced process kill.

Build-remap-hints.log records Development Editor/Win64 Succeeded. Final network tests require clean Python/fatal/world-leak scans and normal editor shutdown. Original108SHA256 verification is in vendor-integrity.json. Working tree excludes pre-existing DefaultEngine.ini/.vsconfig/Automation_RVSurvival.slnx/RVSurvival.slnx; the engine file is not printed or committed. Saved/committed recovery checkpoints:a6d64ba,da75110(WIP),329bfce,4a94608,d3d93de,f40a691; subsequent closure checkpoints are in Git/final report.

Remaining intended limits: parked bed; stopped seat-to-seat switching; effectively stopped driver-to-rear; parked ladder/roof with propulsion interlock; prototype sit/lie/climb presentation; roof edges have normal falling risk; no moving/rolled/steeply tilted/externally pushed roof, packaged or dedicated-server certification. Complete new manual-player acceptance remains unfinished.

### Required Bobby follow-up before acceptance / any Gate7 work

1. Open Gate6FuelElectricalTest, F10 check bindings, open the house door with a normal E hold from clear of its swing. Hold W up the visible step and through the doorway; walk front/rear/back and physically out, then close. Repeat on host and remote client.
2. Sit/stand each Dinette cushion using normal E holds: status must stay Awake. Hold E at the rear mattress, visibly lie down, use Z, R/E stand, walk away and exit; repeat in both roles.
3. Passenger3 while another player drives: stand safely, walk, then E into available cab/rear seats. Driver3 while moving must reject; after stopping it must restore aisle walking. Verify occupied rejection and ordinary V/1/2 seat controls.
4. Park, hold E at ladder, hold W to top, E onto the real roof, walk around fixtures, hold E at upper ladder, hold S down, E off; walk away. Repeat both roles with representative100ms/2% settings. No floor fall, stuck input/camera/collision or sleep contamination is acceptable.

The remaining flows require a human sustained-key pass or a supported tool capable of real key holds. They are pending, not failed human tests and not presumed passes. Stop after this refinement; do not resume Gate7.
'''
p=root/'Docs/GATE_6_VALIDATION.md';old=p.read_bytes();marker=b'\n## Gate 6 physical-entry, seating and roof refinement - 2026-10-07'
if marker in old:old=old.split(marker,1)[0]
p.write_bytes(old.rstrip()+section.encode('utf-8')+b'\n')
print('Recorded '+str(len(rows))+' diagnostic suites; manual acceptance remains pending.')
