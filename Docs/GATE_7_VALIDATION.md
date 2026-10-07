> **Current resumed pass: ACCEPTED, 2026-10-07.** Preserved mechanical foundation integrated with the user-accepted Gate6 physical-entry/seating/roof baseline; fresh results and limitations are recorded in the closure below. Gate8 was not started.

# Gate 7 mechanical failure and repair validation

Status: **ACCEPTED**, 2026-10-07. Gate 8 was not started. Accepted Gate 6 baseline: `2ef5b83`. This verdict covers the prototype behavior and bounded tests below, not final mechanical balancing or a packaged shipping build.

## Implementation and engine framework review

Six native classes establish the opt-in foundation: `URVCoolingComponent`, `URVMechanicalProfile`, `ARVServicePoint`, `ARVMechanicalMotorhome`, `ARVEngineHood`, `URVMechanicalWidget`. Cooling and engine condition are independent records; there is no universal RV health. The motorhome composes these systems and the accepted fuel/electrical/Chaos architecture. Passenger movement, seats, normal character movement and the driving physics configuration were preserved.

Use replicated Actor Components, Gameplay Tags, Primary Data Assets, RepNotifies, owned-controller Reliable RPCs, weak next-tick dispatch, TimerManager, native Chaos torque scaling and read-only UMG. Existing inventory FastArray records remain authoritative. No custom transport, timer framework, parallel fluid inventory, GAS/CommonUI migration or Lyra experience refactor is justified here. Relevant primary references: [component replication](https://dev.epicgames.com/documentation/unreal-engine/replicating-actor-components-in-unreal-engine), [Gameplay Tags](https://dev.epicgames.com/documentation/unreal-engine/using-gameplay-tags-in-unreal-engine), [Data Assets](https://dev.epicgames.com/documentation/unreal-engine/data-assets-in-unreal-engine), plus installed UE5.8 TimerManager, Chaos and NetEmulation headers/source. Engine concerns are reused; the causal mechanical rules are RVSurvival-specific.

The complete C++/content change list is [source-content-manifest.txt](Gate7Results/source-content-manifest.txt): 21 C++ files and 11 project-side assets. Existing inventory/controller/HUD/door/systems files receive bounded integration; no accepted vendor or prior-map edits.

## Cooling, temperature and engine condition

Normal tuning lives in `/Game/Mechanical/DA_NormalMechanical`:

| Quantity | Default |
| --- | --- |
| Coolant capacity / low warning | 12 L / below25% |
| Ambient / maximum temperature | 20 / 200 C |
| Idle plus full-load heat | .25 +1 C per simulation second |
| Passive / radiator cooling coefficient | .0015 / .009 per second |
| Airflow | `1 + clamp(speed /2682.24 cm/s,0,2)` |
| Slow / major leak | .001 / .015 L per second |
| Radiator slow / major thresholds | below.85 / at-or-below.35 |
| Warm / hot / overheating / critical | 95 /105 /115 /130 C |
| Service readiness | speed<10cm/s, engine off, temperature<=60C |
| Engine maximum / warning / reduced-output fraction | 1 / .75 / .5 |
| Base overheating damage | .0004 of maximum condition per second, escalating up to6x |
| Thermal limp output | .35 |
| Shutdown / restart fractions | .1 / .3, with restart temperature<105C |

Cooling effectiveness is radiator condition times coolant fraction. The solver uses the bounded exponential solution of `dT/dt = heat - k(T-ambient)` in at-most1-second simulation steps. Engine load, speed airflow, radiator damage, coolant loss and shutdown change that balance. Slow leaks continue while stopped. Shutdown removes combustion/load heating; residual temperature cools. Engine maximum, thresholds, rates and severity are tunable; condition is clamped relative to its maximum.

A healthy full-load one-hour simulation settles at84.1026C with no coolant loss or engine wear. Minor100-second leak gives11.9L; major gives10.5L. Damaged radiator/low coolant are measurably hotter, and airflow/cooldown behave correctly. Temperature/fuel/condition NaNs and invalid ranges are rejected or bounded as recorded.

`/Game/Development/Mechanical/DA_AcceleratedMechanical` is a separate saved profile: thermal/leak/damage rate coefficients20x, unchanged equilibrium/thresholds, .25s test repairs. Explicit PIE-only debug time scale additionally supports bounded acceleration; production defaults remain normal. Live profile proof: development180s and normal3600s both reach84.1026C; development10s and normal200s slow leak both yield11.8L. Struct `.copy()` preserves the normal asset. Shipping/test builds reject debug mutation; no client debug RPC exists.

## Items, repairs, hood and controls

Seven definitions under `/Game/Mechanical`: mechanic tool kit, radiator patch kit, replacement radiator, engine service parts, full5L coolant, partial1.75L coolant, empty coolant hardware. Tools/parts use registered requirements tags and minimum condition; gameplay does not match display-name strings. Tool/part logistics are2kg/3L; coolant5kg/6L. Patches stack10; other parts/tools/cans are individual. Fixed prototype weight is not a fluid-density simulation.

Coolant uses the accepted Gate6 fluid fields (`Fuel`, `FuelLitres`, `FuelRevision`, legacy names) with exact `Resource.Fluid.Coolant` identity. Owned GUID/revision/capacity validation conserves litres, preserves condition and leaves empty hardware. Gasoline/diesel compatibility remains exact. Exterior tool/fluid/spare-parts storage is reused; pantry/overhead roles remain unchanged.

| Control | Behavior |
| --- | --- |
| Hold E | Inspect front engine/cooling point through accepted .5s interaction |
| P | Open/close stopped hood; open hood interlocks propulsion |
| B |8s roadside patch: usable toolkit retained, one patch consumed; at-least.65 radiator condition, .15 leak multiplier, temporary |
| N |15s radiator replacement: toolkit retained, one radiator consumed, condition1/no patch/no leak |
| M |20s recoverable engine service: toolkit retained, one service part consumed, condition raised to.65; does not heal radiator |
| I, Up/Down, F | Select owned coolant and refill through opened service point |
| Escape | Close/cancel; supplies retained on interruption |

B/N/M/P use a separate EnhancedInput context only while inspecting, removed on close/range exit/teardown. Accepted remapped controls remain available elsewhere. Repair start reserves the subsystem; completion revalidates ownership, requirements, range/LOS, hood, stopped/off/cool state and mechanical revision before atomic consumption. Container/power/seat/rest transitions, leaving range, closing hood or disconnect interrupt safely. Inventory inspection alone need not cancel. No animation lock or crafting system is introduced.

The separate purchased `Art_RV_Chassis_Hood` is used as a project-side hinged visual, pivot(258.325,0,141.455)cm,60-degree pitch. The original owned hood visual is suppressed by asset identity; vendor mesh/material files are unchanged. Fixed fascia/HoodTop/firewall/cab collision remains protective when open. Swing obstruction and stopped guards apply. The engine bay is serviced from outside, never physically entered.

Read-only restrained UMG displays temperature/gauge, low coolant/leak, engine wear/limited output/shutdown and hood interlock. Detailed service information is qualitative; progress uses synchronized server time. Right anchoring plus DPI-aware vertical placement avoids overlap with the fuel monitor. Native-window review confirms readable service and driver views, single hood visual and survival UI retained. The desktop helper could capture but failed viewport activation; gameplay controls were exercised through the existing native development key dispatcher, not hardware-keyboard claims or direct completion shortcuts.

## Multiplayer authority and persistence preparation

Server owns thermal integration, radiator/coolant/engine/fault state, output permission, reservations, timers and inventory mutations. Component state/tuning/revision and public service progress replicate; controller service selection/feedback is owner-only. Clients send intent with owned item IDs and expected revisions, never amounts/outcomes. Foreign GUID, stale/duplicate refill, missing-tool and concurrent repair requests cannot create supplies or clear faults. Explicit controller PawnLeavingGame/EndPlay cancels owned repairs immediately, with weak-reference/.1s endpoint fallback. Timers are cleared on cancellation/EndPlay.

Future save serialization should retain scalar machine records, patch state/multiplier, fault tags and profile/item asset/tag/GUID identities. Active player references/reservations are transient and should cancel on restore. Normal BeginPlay initializes new machines; a future serializer must explicitly restore existing state. No full save/offline system is implemented. Other vehicle types need their own running/load/speed/service-readiness adapter; the solver/records/requirements remain modular.

## Actual test setup and results

Saved `/Game/Maps/Gate7MechanicalTest`,77 actors, purchased54-part RV, accepted road/reference space, all seven exterior compartments/interior stations/rest/seats/ladder, seven new pickups. Blueprint: `/Game/Vehicles/Gate7/BP_ClassCMechanicalMotorhome`. Previous maps retained byte-for-byte. UE5.8.3 Development Editor/Win64; live native gameplay bindings at60FPS. Initial placement/fault/supply fixtures are identified in scripts; actual roadside walking, entry/exit, inventory selections/transfers and timed repair intent use normal paths. No direct repair-completion helper.

Latest named receipts in [Gate7Results](Gate7Results/) are the evidence; raw quarter-second/frame samples and logs remain in `Saved/Gate7Validation`, regression/audit folders and History. Historical failures are clearly retained under FailedUncapped/FailedInvestigations/development-history; they are not acceptance passes.

| Executed group | Passing checks / result |
| --- | --- |
| Final single-player |43/43: normal/minor/major cooling, load/airflow/cooldown, all thresholds, clamping/nonfinite input, nondefault engine maximum, overheating/shutdown, exact refill/full rejection, missing requirements, timed patch/replacement/engine repair, cancellation and used-fluid storage GUID/revision/condition round trip |
| Host-driver baseline, separate processes |31server /24client; complete roadside stock retrieval, repair/refill and resumed travel |
| Host-driver server-outgoing100ms/2% loss |31server /25client; includes client debug-authority rejection |
| Client-driver final100ms/2% both outgoing directions |25server /33client; measured temperature rise from70C fault under actual W/load, coolant loss, host walker, authority/contention/convergence, roadside workflow and resumed travel |
| Two actual native disconnect/reconnect repair cycles |11server /8client; reservation cleared,9s no-late wait, shared GUIDs intact, new pawn/service access and exactlyone patch after each rejoin |
| Serial authority stress |18/18 in140.59s:100 exact fluid transactions,100 timed cancels,100 completions,100 heat/shutdown/cool cycles, final stack safety, full/partial/empty drop+normalE repick, actual shutdown W rejection and repaired W traction |
| Actual throttle-caused severe failure and recovery |10/10; crossed critical and wore engine to.098288/shutdown without setting that condition directly; natural cooldown48.51C, normal20s M/15s N, inventory F5L, actual E/W resumed at937.52cm/s |
| Separate-process V/seat/bed control regressions, reversed role, bidirectional100ms/2% |65server /65client;20V/1 cycles, occupied/moving/recent-stop transitions, repeated E/Z/R/E bed, zero floor-fall/seated-walking samples |
| Rear seats/moving pantry/exterior contention/ladder, emulated |22server /22client |
| All five stations parked/highway and leave/walk, emulated |25server /25client |
| Repeated parked/moving house door and glass, emulated |43server /43client; exactlyone visible mesh each, matching collision/frame |
| Gate1 representative regression |23/23 movement/look/jump/interaction/multiplayer |
| Gate2 representative regression |24/24 shared vehicle/host+client driving/possession/exit; extra inventory identity after possession receipts |
| Gate4 inventory regression |24/24 capacities, pickup/drop/state/container/contention |
| Gate5 survival regression |27/27 consumption/stacks/ownership/thresholds/rest and24-hour equivalent clamping |
| Entry/normal movement regression |22/22 |
| Gate6 fuel/electrical separate-process emulation regression |31server /29client; partial cans/refuel/conservation, batteries/alternator/generator/solar/loads/panel/ownership/disconnect |
| Open-hood complete exterior collision audit |33/33 front/corners/wells/both sides/rear/under-front/firewall/windshield boundary/continuous walk-around, capsule34cm retained |
| Driving camera regression |17/17 low/road/~60mph/turn/reverse/obstacle boom recovery;1400cm arm,340cm anchor,85FOV,16cm probe retained |
| Saved-package audit |44/44; all seven maps loaded twice with scoped/released references; normal profile,54parts,seats/bed/layout/ladder/collision/camera/77-actor map and separate developer repairs verified;SaveAll/clean exit |
| Saved20x developer profile |5 save/content checks +4 live solver/equivalence/default-profile checks |

Network settings are not mislabeled: early runs used editor server-outgoing100ms/2%; final Everyone runs apply native `NetEmulation.PktLagMin 100`, `PktLagMax 100`, `PktLoss 2` in both processes, confirmed in both logs. These are outgoing delays, not a claimed100ms RTT. Separate PIDs are checked. Finite-route post-fixture-reset mechanical correction maxima are0cm; original whole-session maxima around574-575cm include the deliberate initial placement correction and are not usable movement metrics. Existing30cm baseline/75cm emulated regression bounds were retained, not weakened. Raw samples permit inspection of this separation.

Stress heat-cycle42.08C figure is a maximum post-fault-segment endpoint after shutdown/cooling, not a measured peak. The separate actual-drive trace crossed130C and recorded the causal failure. Accelerated simulation/fixtures are distinguished from elapsed real play; no claims of hours of physical driving.

## Failures found and fixes

- Initial same-tick aim/E raced replicated view; aim on a preceding frame and settled approach now match the actual input path. Early missing-tool assertion was scheduled after host reservation and correctly got busy; it now precedes reservation, with a separate valid contention test.
- Continuous reverse/brake after reaching rest restarted reverse; brake-then-handbrake phases corrected. Uncapped child FPS differed from accepted60FPS and inflated corrections; restored both caps and isolated setup fixtures. Earlier681.35/222.90cm failed movement measurements are retained. No solver/collision threshold bypass.
- Collapsed new UMG did not tick back into view. HUD now controls availability; physical DPI positioning separates the fuel/engine panels. Service actions are scoped rather than globally consuming remapped B/N/M/P.
- Disconnect cleanup initially depended on a later.1s service Tick. Explicit owned-controller cleanup was added; rejoin/fault handoff waits for valid replicated endpoints and actual fresh state. Repeated native cycles pass without late completion or supply corruption.
- Python inspection used unavailable WidgetBlueprintLibrary instead of the supported ScriptName WidgetLibrary, and a wrong bool property spelling. The optional editor-only NetworkEmulationTarget enum was not exported; supported native console commands replace it. Driver inspection first looked up the unpossessed survivor by PlayerState, which is cleared by normal possession; it now resolves the authoritative driver-seat occupant. These helper errors ended cleanly and were repeated successfully. They were not Unreal crashes or accepted gameplay passes.
- A serial launcher briefly observed the just-exited process during teardown; process handles are disposed and a one-second settle prevents a concurrent launch. No forced kill, leak-detection suppression or destructive map duplication.

No fatal Unreal crash or World Memory Leak occurred in this Gate7 work. Clean completed logs contain no Python errors; failed helper logs remain preserved. The existing unactivated Incredibuild/standalone fallback is nonblocking; no license/payment or OS security changes were made. Final dashboard and profile logs contain no CreateSavedMove warning.

## Known prototype limits

- Simplified first-order thermal/airflow/condition model, no thermostat/fan/pump/hose/oil/transmission/brake/tire simulation, skills, maintenance schedule, final animations/VFX/audio or random breakdowns. Ambient is currently configured, not weather-driven.
- Repairs require parked/off/cool and an open hood. Engine service is recoverable.65 condition, not guaranteed perfect restoration. Fixed simplified front protection remains even when hood opens; the mechanical underside is intentionally not a sealed hull. No crouch/prone/under-RV traversal is claimed.
- Native visual/window review and real binding dispatcher testing are documented; failed desktop viewport activation is not represented as successful hardware playtesting. Separate-process emulation is a finite PIE matrix, not proof against every network/streaming/packaged configuration.
- Live thermal ticks cap a single hitch to2real seconds; explicit debug advances support up to86400 simulation seconds. No offline catch-up/persistence implemented. Fluid weights remain fixed prototype metadata; legacy field names remain for compatibility.
- Stopped beds/rest and seat-to-seat limits remain. The resumed map now uses the accepted parked ladder/roof access with propulsion interlock; earlier mechanical-baseline tests used the controlled endpoint. Exterior storage doors remain static preparatory parts; no full compartment-opening animations added.

## Recovery, saved state and closure

Meaningful local checkpoints:65a2d08 baseline/framework plan;15622e7 compiled foundation;63fca04 saved map/content;8ccd3ec service/hood safety;90729db live UI/scoped controls;6c38c2f network/stress/disconnect; a4dac2d both-direction networking and prior-gate regressions. Final closure is a separate local commit; its hash is in the final report/Git history rather than a self-referential commit hash in this file.

Save before/after content/configuration, normal StopPIE, runner release before world changes and SaveAll/clean shutdown are verified. Latest native dashboard session saved/stopped/closed cleanly; final DevelopmentEditor Win64 build succeeded (target up-to-date,.68s; preceding UI compile17.15s).108/108 vendor SHA256 hashes match; all prior map/fallback assets remain unchanged. Pre-existing unrelated `Config/DefaultEngine.ini`, `.vsconfig`, `Automation_RVSurvival.slnx`, `RVSurvival.slnx` remain excluded from Gate7 commits. Gate7 changes are committed locally; no push. No Gate8 work.

Next recommended task: manually review the saved Gate7MechanicalTest/service controls and balancing, then explicitly authorize the next gate when desired.
## Resumed integration after user Gate6 manual acceptance

The user explicitly accepted the physical-entry/seating/roof refinement on 2026-10-07. Its diagnostic limitations and raw correction history remain preserved. The preserved mechanical map initially had physical entry disabled, Dinette rest and the old ladder endpoint. Copied only scalar project-side collision configuration from the accepted saved Gate6 map, removed the obsolete Dinette rest actor, enabled physical entry and matching roof/ladder configuration on Gate7MechanicalTest and BP_ClassCMechanicalMotorhome. Normal mechanical profile and supplies were retained. Actor count is now76 because the obsolete rest actor was removed; this is not a lowered behavior criterion. Gates1–6 maps and vendor assets are unchanged by this integration.

Framework review reconfirmed native component replication, owned-controller RPCs, RepNotifies, TimerManager, Gameplay Tags, Primary Data Assets, Chaos output scaling, native CharacterMovement and UMG in the existing foundation. No duplicated transport/timer/effect framework or broad GAS/Lyra migration is warranted. Machine-specific cooling equations and repair policies remain game rules.

Fresh single-player suite passes43/43 on the integrated saved map. A first separate-process route attempt stalled before readiness because the launcher inherited standalone PIE mode restored during prior cleanup. Stopped PIE and closed the saved editor normally; no forced kill or leak suppression. The corrected launcher explicitly configures the closed editor native listen-server enum (not exported to Python), with an INI backup. Failed setup is retained and is not a gameplay pass. Both-role route, mechanical-network, stress, saved-package and final-build results remain pending for this resumed pass.

Recovery checkpoints: d9dc8b0 records user acceptance and scoped saved audit; dfa4dad saves integrated map/BP and scoped route tooling. Refrigerator is part of the combined vendor interior mesh rather than a separate named part. No guessed or oversized refrigerator collision has been added; the optional nonblocking correction remains deferred pending measured visual geometry.

Fresh impaired physical routes: host-driver34server/34client and client-driver34server/34client, all passing, distinct process IDs. Each includes physical entry/exit, stopped driver rejection, moving passenger3, cab/Dinette/bed, roof walk/return and open/closed doorway behavior. Native binding diagnostics are not mislabeled as new hardware manual tests; the user separately accepted the Gate6 manual playtest. Host-driver mechanical route passes32server/26client with both-direction100ms outgoing/2%loss, including roadside recovery and supply conservation. Vendor integrity currently108/108unchanged. Reverse mechanical/stress/final regressions remain in progress.

Client mechanical repeat: first timed sequence missed initial normal-E driver entry and cascaded; exact first missed-request cause remains unestablished. Added read-only local prompt/seat-feedback/active-movement diagnostics, without changing gameplay. The next run entered/drove correctly but its fixed-duration front approach stopped at local(386.43,-135.72,72.38), behind the front corner; service diagnosis failed through valid solid collision. Replaced only the test walking pulses with native-W waypoint steering outside the shell and around the bumper to(550,0), with no teleport or direct completion. Corrected client-driver100ms/2% run passes25server/33client including supply retrieval/diagnosis/timed patch/exact refill/resumed driving. Failed attempts are retained under FailedAttempts and raw Saved History. This does not retroactively establish the exact first missed-input cause or certify every impaired interaction timing.

Fresh stress passes18/18 in140.65s, including100 fluid transfers/100 cancels/100 timed commits/100 heat-cool cycles and actual W traction restored at950.55cm/s. Impaired moving-storage route passes8server/8client. First disconnect run passed11/8 assertions but failed the clean-log criterion: generic appended emulation referenced absent module-global pc. The disconnect runner intentionally uses function-local controller/world references. Skip that footer for disconnect and apply native emulation on initial join and each rejoin using reacquired controller; a clean repeat is required. No Unreal fatal/world-memory-leak or forced kill occurred.

Corrected disconnect clean repeat passes11server/8client for two native disconnect/reconnect cycles with bidirectional emulation reapplied in joined worlds. Both current logs scan clean for Python errors/fatal/world leaks, so the earlier19 passing assertions with a setup error are not counted as acceptance. Entry/front-shell22 and Gate1 interaction23 fresh regressions pass; remaining regressions/build/save closure continue.

## Resumed Gate7 closure - ACCEPTED, 2026-10-07

This closure supersedes the resumed-pass pending notes. Existing mechanical gameplay C++ was preserved; the saved Gate7 map/Blueprint now include the accepted physical side door, sole bed rest point, fitted kitchen/roof collision and parked roof-access ladder. All earlier maps/fallbacks and108vendor files match the prior accepted state.

| Fresh executed group | Result |
| --- | --- |
| Mechanical single player |43/43 |
| Host-driver separate-process mechanical100ms/2% |32server/26client |
| Client-driver separate-process mechanical100ms/2% |25server/33client |
| Physical entry/cab/Dinette/bed/roof/exit, both impaired roles |34/34 per role combination |
| Moving pantry/exterior storage, impaired host driving |8server/8client |
| Two real repair disconnect/reconnect cycles, clean impaired repeat |11server/8client |
| Conservation/timer/thermal stress |18/18 in140.65s;100 transactions/cancels/commits/heat-cool cycles each |
| Entry/front collision regression |22/22 |
| Gate1 movement/interaction/multiplayer |23/23 |
| Gate2 driving/possession/blocked-exit prerequisite and restoration |30/30, plus inventory-after-possession receipt |
| Gate4 inventory |24/24 |
| Gate5 survival |27/27 |
| Gate6 resources, separate processes/emulation |31server/29client |
| Saved packages, seven maps reloaded twice |50/50, SaveAll/clean quit |
| Final actual UMG visibility/capture |3/3, normal E service path; panel and survival readable |

The legacy Gate2 Console Input.+key repeat failed re-entry before blocking exits. Its empty prompt/unoccupied prerequisite and failed assertions remain in FailedAttempts. A scoped wrapper uses the already accepted native InputKey dispatcher; all30unchanged prerequisite/exit/restoration checks then pass. No production exit/seat/collision code was changed. This comparison establishes that the retained failure did not demonstrate unsafe release of an occupied seat; it does not retroactively prove every earlier missed-input root cause.

Screenshot review found SHOWUI was placed after filename without a flag; installed UGameViewportClient parsing accepts it first or as-showui. Corrected test capture and ran a real UMG probe: service and survival visible, native E opens service, final image in Gate7AcceptedInterior/ui-final.png. This was a capture omission, not a hidden UI gameplay fix.

Final DevelopmentEditor/Win64 build succeeded, target up-to-date,1.54s. Module SHA256 remains A7E3B18FBACA5B51CCBF41372F624DD02799FF4373110841698AD389AF864DC9, matching fresh physical/storage provenance. Editor and PIE shut down normally; no active test/build automation remains. Final native preferences restored and verified with editor closed: standalone1player,one process,emulation off,empty child launch parameters; backup retained. Vendor108/108hashes match and only Gate7MechanicalTest/BP_ClassCMechanicalMotorhome content differ from37b12e5. No purchased source or Gate1–6 map changes.

Remaining limitations: first-order thermal model and provisional rates; service requires parked/off/cool/open hood; temporary patch retains leak/condition limitations and engine service restores only.65; no other mechanical failure subsystems or full persistence. Beds/seat-to-seat stopped-only; passenger3 moving supported, driver3 stopped; roof parked/interlocked with ordinary edge fall risk, no moving/rolled roof certification. Refrigerator collision remains explicitly DEFERRED/nonblocking per the user brief: combined interior mesh requires measured geometry rather than a guessed aisle-blocking box. One initial scripted outer-driver E miss remains of unestablished exact cause; failed evidence retained and later diagnostic/native routes pass. No new full hardware-manual, packaged or dedicated-server certification is claimed.

Local recovery checkpoints: d9dc8b0 user acceptance/read-only audit; dfa4dad saved integration; bf17b5f both physical roles/network setup;523c6a6 corrected roadside and retained failures;8ff142d stress/reconnect. Final closure is a separate commit, recorded in Git/final report rather than a self-referential hash here. Working tree preserves only the pre-existing engine config and three IDE files outside task commits. No push.

Next recommended task: manual Gate7MechanicalTest roadside/service playtest and measured refrigerator-collision follow-up; await explicit Gate8 authorization. Stop after Gate7.

## 2026-10-07 rollover refinement — validation in progress
Added a compiled prototype recovery component and remappable F8 / development RVRecover command. Earlier Gate7 acceptance does not yet cover this new refinement. Three near-ground single-player orientations passed 18 checks on the initial clearance policy. Separate-process validation remains pending: first paired run stopped on a test-only unpossessed-pawn PlayerState lookup; needs snapshot now reacquires PlayerState actors. Initial high-drop fixture self-righted and a Python distance API error was corrected. Failed receipts/logs remain under Saved/Gate7Validation/History. No Gate8 work.


Recovery progress checkpoint: host/client requests and all three orientations passed; uneven surface, damaged mechanical state, partial resources, cargo GUIDs, safe passenger placement and continued walking/driving passed. Host-driver post-recovery E/3 re-entry and moving-interior walking/turning passed. Corrected native prediction cleanup to retain CurrentTimeStamp; prior reset produced expired ServerMove warnings. Current code adds a 400 cm vertical-search bound, conservative full-body clearance, ladder/roof rejection and a Shipping/Test permission guard. Final held-input, UI and regression closure remains pending.

