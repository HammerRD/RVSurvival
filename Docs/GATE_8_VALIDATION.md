# Gate 8 medical validation

Status: **IN PROGRESS — NOT ACCEPTED**. Authorized 2026-10-08. Gate 9 is not started.

## Baseline and recovery

Accepted Gate 7 baseline: `0b6eff6`. Pre-existing unrelated working-tree changes are `Config/DefaultEngine.ini`, `.vsconfig`, `Automation_RVSurvival.slnx`, and `RVSurvival.slnx`; these are excluded from Gate 8 checkpoints. Preserve all 108 vendor packages and prior maps. Refrigerator collision remains deferred unless directly relevant to medical placement.

## Framework review

Gate 8 uses Epic GameplayAbilities for replicated medical attributes and timed medication effects. An additive PlayerState-owned AbilitySystemComponent and AttributeSet leave accepted needs, inventory, seats, and native CharacterMovement prediction intact. Persistent PlayerState ownership is appropriate when the player possesses the RV; passive medical effects target PlayerState rather than assigning injuries to the vehicle pawn.

Injury identity, body region, wound treatment rules, resource requirements, and patient eligibility are RVSurvival gameplay. Reflected GUID-backed injury records and Primary Data Assets represent these rules. GAS owns attribute replication and medication duration/aggregation. Native component replication/RepNotifies, owned RPCs, TimerManager, Enhanced Input and UMG remain the engine mechanisms for interaction and presentation. CommonUI and Lyra experience/game-feature infrastructure are unnecessary for this focused gate. No parallel inventory or custom networking framework is planned.

Primary sources reviewed:

- [Epic GAS overview](https://dev.epicgames.com/documentation/en-us/unreal-engine/understanding-the-unreal-engine-gameplay-ability-system)
- [Epic Lyra PlayerState ability ownership](https://dev.epicgames.com/documentation/unreal-engine/abilities-in-lyra-in-unreal-engine?lang=en-US)
- [Epic attribute/ASC integration](https://dev.epicgames.com/documentation/unreal-engine/gameplay-ability-system-component-and-gameplay-attributes-in-unreal-engine?lang=en-US)

## Implementation progress

Initial foundation: GameplayAbilities plugin/module dependencies, persistent ASC, replicated Blood/Vitality/Analgesia attributes, serializable injury/body-region types, configurable medical profile and existing-item medical capability metadata. This is a foundation only; treatment, injury simulation, medical station, UI, downed/revive and runtime validation remain unfinished.

## Validation policy

Compile and exercise changed medical features first. PlayerState additions require targeted possession/state replication checks; speed/downed policy will require targeted native moving-interior checks. Inventory consumption must reuse accepted serial transactions and validate GUID/revision/ownership at completion. One representative Gates 1–7 pass, vendor/saved-content audit, separate-process medical matrix with 100 ms/2% loss, final build and clean shutdown are required for acceptance. Do not count compile success as gameplay validation.

At the initial architecture review, runtime validation and map creation were pending. Subsequent progress is recorded below.

## Foundation checkpoint — 2026-10-08
Development Editor/Win64 builds passed (21.29 s foundation, 19.56 s medication). Initial C++ replication macro parameter naming failed, then was corrected. Focused live PIE component diagnostic passes 21 checks: authoritative moderate blood loss, GUID-backed wound, existing inventory admission, one-item bandaging, stopped bleeding with retained injury, stale revision rejection, fracture scale query, pain/burn/concussion state, clamping/downed/reset. This is NOT normal-player or multiplayer acceptance. Three Python fixture failures (reflected attribute accessor, default-only temporary Data Asset editing, out-parameter return assumption) were corrected; failed receipts/logs remain under Saved/Gate8Validation. PIE stopped and editor shutdown completed cleanly without fatal/world-leak/Python errors in the final run. All 108 vendor hashes match. No prior maps changed. Treatment UI, station support, movement/action restrictions, multiplayer/revive/medication duration tests and final regressions remain pending.


## Station/UI implementation checkpoint (pending validation)
Gate8MedicalTest saved with nine medical pickups, a functional station at the accepted runtime station-definition position, linked existing Medical storage, normal medical profile and Gate8-only PlayerState/GameMode derivatives. Prior layouts/vendor meshes are unchanged. F9 uses the existing remappable Enhanced Input catalog. UMG offers self/nearby teammate, injury/supply selection, treatment/cancel/close, with qualitative symptoms and HUD urgency warnings.
Downed guard changes touch speed-query policy, input eligibility, interaction, inventory request authority and seat/controller requests. No native solver, prediction, base or transport is replaced. Targeted Gate3 moving and Gate4/7 resource regressions are now required by the risk policy. Treatment interruption uses passenger-frame-local anchors so vehicle translation itself is not cancellation; moving away over50cm or changing frame cancels before consumption.
Setup failures retained: workstation editor-actor assumption, unavailable Python get_root_component (use exposed Mesh), reflected boolean sampler accessor. Saved map setup recovered in place; references released and editor exited cleanly. First-header ordering diagnostics were corrected although UBT still reported build success. Current build success20.16s plus medical warning build18.37s. UI/multiplayer/advanced medical behavior is not accepted yet.


## Normal-player medical panel observation
An initial injury/supply fixture was seeded, then the native window received F9 and visible UMG button clicks. The player completed a normal four-second bandage: active bleeding cleared, injury remained stabilized rather than erased, Bandage quantity changed from three to two, and the HUD changed to the leg-mobility warning. Next-injury selection visibly displayed the left-leg fracture. Fracture treatment, medication, cancellation, teammate treatment and network acceptance remain pending. The first sampler encoded GUIDs as Python struct display strings; these are not GUID-conservation evidence. Future sampling uses GuidLibrary string conversion. Preserved samples: Gate8Results/manual-ui-bandage-samples.json. Managed PIE stop and editor shutdown completed cleanly. Treatment guards reject invalid GUIDs/non-finite supply tuning and require bleeding control before revive. Development Editor build passed in 5.85 seconds.

Focused treatment transaction diagnostic passed all 16 targeted cases: cancel retains supply and leaves fracture untreated; completed splint consumes once, preserves fracture and uses configured 0.65 mobility; GAS analgesia applies without erasing injury; burn dressing and antiseptic consume once and update treatment/risk; condition and GUID survive; invalid GUID consumes nothing. The initial Python GUID wrapper comparison failed and is retained separately. Final PIE/editor shutdown clean. This diagnostic does not replace normal UI or multiplayer acceptance. Medication expiry and concurrent/teammate cases remain pending.

## Separate-process teammate diagnostics
Client healer / host downed patient passed 13 targeted cases on each distinct process (server31720/client15528) at100ms min/max packet lag and2percent packet loss, confirmed in Net log. Bleeding prevents premature revive; dressing consumes once; repeated concurrent revive request consumes one kit; blood restores only to about30; injuries retained; other player's blood unchanged; condition retained; active-patient revive rejected. This is owned-RPC diagnostic evidence, not manual UMG acceptance. Corrected launcher stopped PIE and both processes cleanly without Python/fatal/world-leak errors.
Earlier host-healer baseline gameplay assertions passed, but launcher shutdown failed with UnboundLocalError: a function-local import shadowed release_runners. Removed local import; recovery explicitly unregistered the launcher callback, released runner modules, stopped PIE and quit cleanly. Initial recovery attempt also lacked explicit unreal import and was corrected. Failed log preserved as Saved/Gate8Validation/teammate_host_failed_cleanup.log. No leak detection suppressed. Opposite-role repeat under emulation is running; full Gate8 remains pending.

Host healer / client patient emulated repeat also passed13cases per process (server26284/client21188), with clean PIE/editor shutdown and no Python/fatal/world-leak errors. Both role combinations are now proven for these owned-RPC teammate cases; manual panel controls, moving treatment, disconnect/stress and final regressions remain pending.

Normal OS F9/visible UMG follow-up: selected fracture and Splint; Begin displayed10-second progress; Cancel visibly retained3supplies/untreated fracture; retry completed and showed Splint2/stabilized/recovery-needed. Selected PainMedication and completed2-second action; quantity3to2, painnoticeabletolow, fracture remained. Close removedpanel/restoredGameOnly; normal W tap produced small forward displacement in telemetry (not a sustained-walk test). Stable GUID string telemetry retained. An earlier Escape before viewport focus stoppedPIE; sampler then referenced invalidHealth. Added validity guard to unregister sampler when PIE objects disappear; preserved failed log. Managed follow-up shutdown requested; not an acceptance substitute for moving or teammateUI.

Moving host-driver/client-passenger diagnostic passed normalEseat entry, normal3rear transition, basic bandaging at about2962cm/s, one-item consumption, stable frame/localfloor and subsequent normalW walking towardrear duringturn. Reported9corrections/max215.48cm includes startup fixture placement; cannot classify moving correction behavior from that aggregate. Follow-up resets diagnostics after validatedstanding/before driving to isolate the relevant interval. Earlier setup failed on an unused historical InteriorAccessPoint assumption; removed it and preserved logs. Added immediate managed cleanup if runner loading fails.

Isolated remote-client passenger run reset native correction diagnostics after normal3standing and before movement. Following bandaging at road/highwayprototype speed, turn and nativeWwalk, client reported0corrections/max0cm; local position moved roughly130to12cm alongaisle, height177.17cm. This contextualizes prior215.48cm startup-inclusive metric rather than discarding it. Client-driver/host-passenger case also passed all7checks perprocess. All final role runs ended cleanly; prior failed log entries retain earlier timestamps.

Medical boundary diagnostic passed18cases: minor/moderate/severe rates .5/3/10blood units per minute; combined accelerated bloodloss to86.50; basic bandage rejects severe injury withoutconsumption; development-only short GAS medication effect applies then expires, painreturns/underlyingfracture remains and finalitem removed; concussion healing reaches0.4167 under acceleratedclock; tagpresent; downed drop rejection/speed0; clampedblood/vitality; terminalfoundation/reset. Normal medication remains300seconds; shortfixture lives underDevelopment. Editor clean shutdown.

Focused repeated-timer stress completed20successful cycles with duplicate requests eachcycle and4cancellation/retries. Initial20supplies endedat0exactly; no failures, invalid quantities, changed remaining GUIDs/condition, late cancellations or Python/fatal/world-leak errors. Clean editor shutdown. This targets transaction/timer failure modes, not an inflated assertion count or literal endurance simulation.
## Additional focused validation
Normal medical-panel controls passed self-treatment, cancellation, retry, splint selection, temporary analgesia and closing the panel. Separate-process moving treatment passed both driver/passenger roles under 100 ms latency and 2% packet loss. In the isolated remote-passenger interval, native movement diagnostics reported zero corrections and a maximum correction of 0 cm while bandaging, turning and walking. Earlier startup-inclusive correction values are retained above.

Both disconnect directions passed: patient disconnect releases the healer's hold without consuming a supply; healer disconnect causes no late completion and leaves the patient downed. Both servers remained operational and completed managed shutdown.

Boundary and repeated-transaction tests passed as recorded above. These remain targeted diagnostics, not a substitute for remaining station and representative regression validation. Gate 8 remains IN PROGRESS / NOT ACCEPTED.

## Station, interruption and integration follow-up

The separate-process client opened the medical station with normal E input. Linked medical storage accepted and returned supplies; condition remained 0.81 and quantities were conserved across separate runtime IDs. The first return assertion incorrectly assumed split stacks would merge. Its failed receipt is retained; the corrected aggregate-quantity repeat passed on server and client. Parked advanced treatment consumed exactly one kit and controlled severe bleeding. RequiredPowerLoad is currently None: the station does not require electrical power in this test map.

Corrected interruption diagnostics passed on both processes at 100 ms / 2% loss: out-of-range rejection, genuine obstructed visibility with inactive hold and `Patient obstructed` feedback, patient movement cancellation, subsequent stabilization and cancelled revive without restoration or supply consumption. The earlier obstacle-creation failure invalidated its later nominal results; those receipts are preserved without acceptance credit.

Normal E/3/Z/R controls preserved injury identities through passenger seat, rear standing, bed entry, sleep and wake. Downed native walking was restricted, dropping retained the item and sleep entry was rejected. The bed approach uses an explicitly labeled initial placement fixture; this is not a new complete physical entry-path audit.

Moving medication consumed one dose and applied native GAS relief. A diagnostic display probe failed because MedicalWidget is protected; another filtered UObject probe did not observe the panel. Those failed display checks are retained and are not UI acceptance evidence. A later native Windows inspection of the separate client window visibly confirmed the medical panel, severe left-arm wound, active bleeding/contamination warnings, AdvancedKit ×2 and linked Medical storage after normal E station interaction. The subsequent widget-library probe is unavailable in this build and was removed rather than changing production UI solely for introspection.

Vendor audit against accepted checkpoint 0b6eff6: all 108 files unchanged. See vendor-final.json. Final representative regressions, saved-content reload audit, final build and documentation closure are still pending.

## Actual client medical controls under emulation

Using the separate client's native Windows viewport under 100 ms latency / 2% loss, actual F9 opened the medical panel. Visible `Inspect nearby teammate` selected the downed host and showed its moderate torso wound/active bleeding. Visible Begin started the eight-second pressure treatment; completion showed no active bleeding, retained stabilized wound and dressing quantity 2 → 1. Next medical supply selected FirstAidKit; visible Begin started the twelve-second revive. Completion showed Conscious and kit quantity 2 → 1. Next injury visibly displayed the retained, untreated moderate left-leg fracture. Close removed the panel and returned to the normal view. Only initial injury/item/approach fixtures were automated; gameplay used OS keyboard and mouse controls. Read-only server/client samples corroborate the transactions.

The earlier synthetic F9 display checks were inconclusive harness observations; this actual control path resolves the player-facing F9 concern. The normal E station visual observation remains separate evidence.

A targeted read of every power/electricity reference in the Gate 8 request found no mandatory station-power requirement. Electrical gameplay is required to remain intact as a regression. This map intentionally configures basic medical assessment/linked storage with no power load; future powered equipment can use the inherited station requirement. Advanced kits require a reachable station and parked RV. Moving storage succeeded at approximately 1471 cm/s; advanced treatment was rejected with `Park the RV for this treatment`, with its supply retained.

## Seated-driver medical edge case

UI review found that native APawn::UnPossessed clears the survivor's PlayerState during driving. Nearby patient selection now obtains the vehicle's replicated PlayerState only when the character is the replicated driver-seat occupant. This does not change possession or seat authority.

Actual client UI selected the downed, stopped host driver. Its first treatment was legitimately rejected by the old center-to-center ray: development diagnostics subsequently identified `DriverChair` as the obstruction, while the eye-to-eye ray hit no component. Treatment now uses each survivor's server-derived GetActorEyesViewPoint for visibility and keeps range, collision, reservation, state and completion checks intact. No vehicle/furniture/wall collision is ignored beyond the two patient/healer actors.

On the corrected 100 ms / 2% separate-process repeat, actual F9 and visible buttons completed pressure treatment and twelve-second revive. The panel showed Conscious, dressing 2 → 1, kit 2 → 1, stabilized wound and retained untreated leg fracture. Closing restored normal view. Server/client telemetry records driver seat occupancy, medical PlayerState ownership and host controller possession; prior failed case is retained. Real obstruction/range diagnostics must be repeated for the changed medical visibility origin before acceptance.

## Recovery and measured movement validation

The final medical review corrected inevitable post-revive deterioration: a stabilized Active patient no longer loses Vitality simply because Blood is still below the critical threshold. Active bleeding or a critically low Blood downed state still deteriorates. Critical Vitality loss and slow nourished Vitality recovery are now configurable in the medical profile. This is a focused medical rule change; movement, inventory, transport and prediction are unchanged.

Focused runtime pass: medical drop removed the inventory record, preserved 0.47 condition in the world and normal E repick restored the same GUID/condition. Native W walking with a leg fracture measured 210 cm/s; after completed splint it measured 390 cm/s and retained the fracture. After controlling a wound and setting partial post-revive vitals, a two-hour-equivalent medical-clock simulation ended Active at Blood 48.03 / Vitality 24.01, with two injuries retained at about 0.10 healing. Needs used its normal clock during this diagnostic; this is not a two-hour whole-game endurance claim. Editor stopped PIE and shut down cleanly. Recovery build succeeded in 22.18 seconds.

Final representative results completed once: physical entry/collision 22 checks, Gate 1 movement/hold/replication 23, Gate 2 seats/driving/replication 30, inventory 24, needs 27. Passed unrelated suites are not repeated for the localized medical UI/visibility/recovery changes. Affected medical visibility rejection was explicitly repeated on both processes and passed. Remaining final resource/mechanical and saved-content audits are recorded below when complete.

## Final regression observation window

The separate-process mechanical regression passed all 32 server checks and 25 of 26 client checks. Its missing-tool feedback assertion sampled 0.4 seconds after native B input and still saw the prior inspection message. No later repair/resource assertion failed. A focused repeat used the same E inspection, hood-open and B input path with 100 ms latency / 2% packet loss, allowing two seconds for owned feedback replication. It passed: `Missing usable mechanic tool kit x1`, with no client tool available. This establishes eventual rejection feedback; it does not claim a sub-400 ms feedback guarantee. Original failed evidence is retained alongside the repeat.

Fuel/electrical representative regression: 31 server / 29 client checks passed in separate processes under the same emulation. All editors exited cleanly. Rollover, final physical roof/door coverage and saved-package reload closure remain pending at this checkpoint.

Final rollover regression on the medical build: 47 server / 45 client checks passed in separate processes with 100 ms latency / 2% loss. Covered left/right/upside-down, uneven terrain, owner client recovery, repeat rejection, held-throttle release, resources/item identity/mechanical/needs preservation, seat possession, resumed driving, standing/interior walking and turn stability, and sleeping-passenger release. Clean shutdown; no fatal/world-leak/Python errors detected in the run logs.

## Known scope and limits at final review

- No full save game, offline progression, seamless-travel medical copy, permanent death, combat damage pipeline, advanced disease/infection, surgery or final treatment animations. Contamination is a configurable prototype risk, not a complete disease simulation.
- Medical metadata is SaveGame-compatible, but transient treatment reservations must be canceled and timed GAS effects restored explicitly by future persistence code.
- First aid/revive restores partial Blood/Vitality and retains injuries; stabilized recovery is slow. The accelerated two-hour diagnostic advances medical time only, not the entire survival simulation.
- Basic treatment and linked storage work in a moving RV; advanced station treatment requires it parked. Gate 6 parked bed and seat-switch restrictions remain.
- Medical F9 is remappable. Prototype UMG is functional, not final UI art. Native normal input and actual OS mouse/keyboard evidence are distinguished from fixture setup and direct diagnostic transactions.
- Isolated remote moving passenger measured zero corrections in the sampled treatment/walking window. Earlier fixture/seat-transition aggregate measured nine corrections / maximum 215.48 cm; this is retained and is not characterized as steady-state jitter.
- GAS logs an optional missing GameplayCueNotifyPaths warning; no cue assets are required by this gate. No reproducible world-leak crash occurred in final runs. Original failed/inconclusive harness receipts remain as history, with resolving repeats identified.
- Pre-existing unrelated config/solution changes are preserved and excluded from all medical commits. No Gate 9 work is authorized or started.

## Final saved state and coverage boundary

The final saved reload audit passed 42 checks across Gate1Test through Gate8MedicalTest, including normal tuning, purchased 54-part configuration, seven independent exterior compartments, physical entry/roof configuration, bed/seats, front collision, camera, interior storage roles and the new medical station/game mode/supplies. Final physical multiplayer route passed 34 checks on each process. Final source build: `final-recovery-build.log`, Succeeded, 22.18 seconds. Saved audit ended cleanly at 06:05:05 UTC with no fatal, Python or world-leak error. All 108 vendor hashes were verified again afterward. Normal persisted one-player standalone PIE settings restored; editor is closed.

Orbit/remapping regression coverage is a source/configuration audit of the preserved accepted Enhanced Input bindings and camera setup; a new OS orbit/remap exercise was not performed. Actual OS F9/button medical controls were performed. New downed movement/drop/rest restrictions have runtime evidence; resource/service/recovery downed request guards additionally received source review, not a full dedicated downed test matrix. These scope limits are explicit and are not represented as executed cases.

All substantial medical code/content was saved and checkpointed at stable milestones. Final closure excludes the known pre-existing Config/DefaultEngine.ini and solution files. Exact file/asset manifest is Gate8Results/changed-files.json. Current acceptance does not authorize Gate 9.
