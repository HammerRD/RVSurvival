# Gate 3 moving-interior validation

Status: ACCEPTED — live two-player PIE matrix and final regressions passed (2026-10-05).

## Scope and implementation

Gates 1 and 2 remain accepted. Gate 3 integrates the purchased Class C motorhome, proves networked standing/walking inside it, and validates six fixed workstation placeholders. No Gate 4 or full survival/workstation systems were implemented.

`URVPassengerReferenceFrameComponent` wraps native UE 5.8 CharacterMovement moving bases. Movable simple floors carry the `RVPassengerPlatform` tag. The component observes each character's native base and applies reversible interior settings: physics pushing off, physics-base carry ignoring the base actor, 30 cm capsule radius and 200 cm/s walking speed. Ordinary walking sweeps still collide with walls and furniture. It restores the actual prior settings on leaving/teardown and removes its tick prerequisite. The vehicle contains no passenger transform loop or passenger list.

Standing characters remain ordinary possessed survivors. They are not attached or teleported each tick. Native base-relative moves, prediction, server validation, based-movement replication and visual smoothing remain active. `URVCharacterMovementComponent` only instruments the native correction callback; it compares the acknowledged saved move, using relative positions when the bases match. Diagnostics expose local position, floor/base/frame changes, displacement and correction count/distance. `rv.Passenger.Debug` defaults off; 1 logs frames/corrections, 2 also logs bases. LocalPosition is an observed diagnostic snapshot, not a client-authoritative gameplay position channel.

`ARVInteriorMotorhome : ARVMotorhome` supplies content-configured art parts, simplified cabin collision and station locations. Accepted driver/passenger seats, authoritative occupancy, possession, safe exits and input routing remain inherited. The targeted shared `URVVehicleMovementComponent` fix prevents client vehicle physics-state creation and destroys any state created before net-role assignment. Chaos async submission continues independently of GT tick guards; client simulations must not apply forces against server rigid-body replication. Native wheel-body/joint cleanup remains and proxy gravity is off. The mesh rigid body still receives native replication; the server uses supported Chaos Vehicles normally.

`ARVInteriorStation : ARVTestInteractable` reuses Gate 1's authoritative 0.5-second hold, periodic aim/range/LOS checks, no-repeat and replicated completion count. Stations attach at fixed vehicle-local coordinates. Workbench, medical, kitchen/food prep, storage, power and navigation/radio are placeholders only. Future food/water/needs, sleeping/fatigue, injuries/medicine, generator/solar/battery, maintenance/repairs, crafting and long-term storage can compose systems behind these boundaries; none are implemented here. `ARVInteriorTestCharacter` provides collision-free primitive observer presentation on the native smoothed mesh, only through the Gate 3 GameMode.

## Purchased asset and project configuration

Fab UE plugin import: **Class C RV Motorhome – Low Poly**, MSWoodvine, listing `1e7683dc-0f7d-4cac-84d2-e9a1af88523f`. Original `/Game/RV`: 108 files, approximately 433 MB. SHA256 verifies all original packages unchanged. All configuration and collision changes are project derivatives.

- `/Game/Vehicles/Gate3/BP_ClassCMotorhome`: 54 independent vendor mesh parts and exact vendor Blueprint material overrides. Exterior/interior, cab/house doors, compartments, wheels and steering remain separately adaptable. The house door is configured open for the prototype. All art collision is off.
- Six vendor material instances are reused. Sixteen translucent glass components disable Nanite on the project component; original mesh/material settings remain unchanged. D3D12 SM6 is enabled for the imported content. No detailed art dressing.
- `/Game/Vehicles/Gate3/PA_ClassCChassis`: project rigid box centered (-20,0,170), half-extents (360,122,160) cm. Pawn/Visibility ignore on the chassis; query-only simple cabin boxes supply floor, walls, ceiling, furniture and entry steps. No vendor per-poly collision drives characters or chassis physics.
- Front/rear art floor heights measured 87.19/101.49 cm. Front floor center (77,0,82.19), half-extents (153,117,5); rear (-155,-30,96.49), (80,90,5). Usable aisle approximately x=130 to -190 cm; bed/cab chairs are actual obstacles. Lowered first entry step fits native step-height limits.
- Existing off-road skeletal Chaos rig remains invisible and replaceable. Distinct PhysWheel_FL/FR/BL/BR bones receive offsets to measured centers (296,-88,39), (296,88,39), (-115,-93,39), (-115,93,39) cm. Radius 39.25, width 35.8 cm. Project front/rear wheel Blueprints: spring rate 2000, damping ratio .7, raise/drop 10/20 cm; front steering 32 degrees, rear steering disabled.
- Mass 3500 kg; center-of-mass override (-20,0,55) cm; engine torque 1100 Nm, max 6000 RPM, idle 800; automatic transmission/reverse, RWD. Remaining engine/transmission configuration and wheel offsets are in `final_configuration.json` and `final_wheel_configuration.json`. Chaos network physics prediction remains disabled; forces are server-only. Handling is prototype tuning.
- `/Game/Maps/Gate3MovingInteriorTest`: flat 10 km surface, clear driving lane with reference cubes at y=±5000 cm, two distinct Player Starts, purchased RV, native visible-test pawn GameMode. Gate1Test, Gate2VehicleTest, BP_PrototypeMotorhome and the primitive BP_WalkableMotorhome fallback are preserved. Startup/default map remains Gate1Test.

## Build and actual tests

Development Editor / Win64 succeeded: UE 5.8.3 CL58210709, VS14.44.35229, SDK10.0.22621. Final functional build took 27.22 seconds, no compiler errors. `build_receipt.json` records loaded module provenance/hash.

Tests inject actual Enhanced Input keys into live PIE, with real Chaos driving and normal character sweeps. Only initial character fixture placement precedes driving. No standing passenger or driving vehicle is warped to force successful movement. Integrated seat role exchange uses the real stopped RV without an artificial vehicle reset. Native UI inspection confirmed purchased interior materials/prompt and prototype observer presentation. These are finite local PIE tests, not a claim of production polish or exhaustive network reliability.

Shared-process host-driver/client-walker and client-driver/host-walker: **40/40 each**. Separate-process matrix below: 40 common checks per process, plus two actual moving MouseX/MouseY checks on the walking player's process in the later runs. Independent PIDs and paired sample comparison establish actual separate processes; process-local comparisons alone are not used as observer proof.

| Separate-process case | Walking process checks | Max standing drift | Max measured correction | Paired capsule / visual error |
|---|---:|---:|---:|---:|
| Host drives / client walks | 40/40 | 2.35 cm | 0 cm | 13.29 / 16.95 cm |
| Client drives / host walks | 42/42 | 2.29 cm | 0 cm | 9.93 / 10.37 cm |
| Host drives / client walks, emulated | 42/42 | 3.62 cm | 1.85 cm | 9.60 / 13.60 cm |
| Client drives / host walks, emulated | 42/42 | 2.43 cm | 0 cm (authority) | 29.96 / 29.95 cm |

Each full run tests natural door/step entry; low-speed front/rear walking; acceleration through road speeds; approximately 2670 cm/s (60 mph) front/rear and sideways walking; stationary standing relative to the RV; normal look; gentle/strong turns; braking; stop/resume; natural walking exit with original settings restored; re-entry; and replicated observer positions. All six stations completed exactly once at rest and highway speed; medical also completed during a stronger turn. Continued hold did not repeat, early release and look-away canceled. No measured floor/frame loss or launch occurred. No increasing positional error was observed.

Emulation: **100 ms outgoing-server packet latency + 2% outgoing-server loss**, verified in PIE/packet-setting logs. It is not 100 ms independently applied to every direction. The emulated client walker recorded four small corrections in the strong-turn phase, maximum 1.85 cm; movement remained usable. Initial fixture placements and transition corrections are excluded from steady-driving correction claims. Observer timing/interpolation differences are separate from passenger sliding.

Additional final module-owned shared-process host-driver run: **42/42**, followed by successful namespace release, GC and clean editor shutdown. Additional final-material emulated separate-process client-driver run: 40/40 per process, matching station counts; paired capsule/visual maxima 27.03/26.26 cm. Integrated purchased-RV seats/driving: **24/24** including both driver/passenger combinations, occupied-seat rejection, replication, forward/steering/reverse/handbrake, moving-exit rejection, clear/blocked exits and seat release.

Additional frame-sampled long tests, both roles with emulation: **10/10 each**. Each includes 60 seconds straight and 60 seconds of repeated turns at continuous highway speed, plus acceleration/braking. Client standing drift: .14 cm straight, 2.17 cm turning. Host: .11 cm straight, 1.35 cm turning. No corrections or floor loss in either long measured phase. Approximately 3600 samples per one-minute phase. Parked proxy alignment from 5–20 seconds stayed at a constant 4.47 cm world difference, with no growing vertical drift.

Standing passenger disconnect during moving medical hold: **9/9**, rerun on final build. Survivor/frame cleanup occurred; original server count stayed zero with no late completion; RV/driver survived; passenger seat remained free; driver stopped, exited and resumed ordinary movement/jump.

## Regressions and acceptance

Original Gate 2 shared-process, concurrent-seat, separate-process, emulated and driver/passenger disconnect suite passed **90 live assertions + 20 paired replication comparisons** on the final build. Original Gate 1 single/listen movement and interaction regression passed **23/23**, repeatedly including the final clean-shutdown run. Its simultaneous completions and no-repeat behavior still passed. Original maps/fixtures were not altered. Gate 3 acceptance criteria are satisfied; no later gate is authorized or started.

Permanent JSON telemetry, paired comparisons, configuration/material/hash audits, build receipt, logs and rerun scripts: `Docs/Gate3Results/2026-10-05`. `measurement_summary.json` reports actual measured phases; raw records retain individual results. Earlier trial failures are not counted as acceptance passes.

## Investigation history

1. Using the chassis/root bone for every wheel made native wheel-body cleanup disable chassis simulation. Correct distinct wheel bones fixed the cause; a forced physics-asset reinitialization experiment was removed.
2. Excessive spring stiffness flipped the RV and was rejected. A short driving surface caused an off-edge fall and was enlarged. A too-high first step was lowered after measuring real ride height.
3. Client suspension constraints caused approximately 90 cm corrections. Skipping their creation fixed severe jitter. Remaining parked drift exposed async simulation outside GT tick guards; preventing client vehicle physics state removed the accumulating drift.
4. Driving-sequence stops were actual chassis collisions with nearby reference cubes. A runtime collision audit identified them; widening the Gate 3-only lane produced 24 passing checks without a drivetrain change or artificial role-swap reset.
5. Regression automation exposed Python garbage-collection/finalization failures after successful tests. Module-owned runner namespaces made explicit GC safe; releasing completed runner modules while Unreal/Python remained alive then produced a clean normal shutdown. Final Gate 1 results were rerun and retained with a clean GC/exit receipt. Do not run map loads or retain completed temporary runner actor references into interpreter shutdown. No installed engine or vendor files were changed for this workaround.
6. Background-throttled runs and harness API errors were corrected and rerun. An accidentally closed editor interrupted one process test; it was discarded and repeated. Map loads occur from normal startup/console execution, not Slate callbacks, after an earlier callback/GC crash investigation.

## Known limitations

No unresolved Gate 3 acceptance failure or persistent severe movement instability remains in the completed matrix. Small native physics/observer offsets and the measured emulated corrections remain. Prototype passenger animation, static wheel/steering art and handling are not final; visual wheel travel/rotation is not a finished presentation system. Seat entry/exit retains Gate 2's external cab points and safe outside exit behavior; interior seat-transfer UX is not implemented. The aisle deliberately respects actual furniture and uses configurable reversible movement dimensions.

Flat-road tests do not establish rough-terrain, rollover, airborne/jumping passenger or more-than-two-player behavior. Multiple standing passengers can use the per-character/native-base architecture, but those larger sessions have not been validated. These are declared limits, not weakened substitutes for the required two-player walking/interaction matrix. Future survival systems remain unimplemented. Stop after Gate 3; no Gate 4 work.

## File/class manifest

Gate 3 C++ additions (matching Public/Private `.h`/`.cpp` pairs): `Player/RVPassengerReferenceFrameComponent`, `Player/RVCharacterMovementComponent`, `Player/RVInteriorTestCharacter`, `Interaction/RVInteriorStation`, `Vehicles/RVInteriorMotorhome`, `Vehicles/RVWalkableMotorhome`. Updated `Player/RVSurvivorCharacter` installs the movement subclass/reference-frame component. Updated `Vehicles/RVVehicleMovementComponent` supplies the targeted client Chaos physics-state/constraint cleanup. `RVSurvival.Build.cs` adds editor-only MeshDescription/StaticMeshDescription for read-only art measurements and project-side collision configuration. Accepted Gate 2 seat/controller/possession behavior is preserved.

Content additions: original `/Game/RV` import; Class C motorhome/chassis/front-wheel/rear-wheel derivatives; Gate 3 visible-pawn GameMode; primitive walkable fallback; Gate3MovingInteriorTest. Project DefaultEngine adds SM6 while preserving accepted Gate1 startup/default maps. Updated design/architecture/networking/RV/roadmap/changelog/validation documentation and permanent evidence. Previously uncommitted accepted Gate 1/2 dependencies are included when checkpointing the local repository; they are not a new gameplay redesign in this gate.
