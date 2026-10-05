# Gate 2 validation

Status: **ACCEPTED** on 2026-10-05. Gate 1 remains accepted; Gate 3 is not started.

## Build and fixture

Unreal Engine 5.8.3, CL 58210709; Development Editor / Win64. ChaosVehiclesPlugin enabled; RVSurvival depends on ChaosVehicles and PhysicsCore. The installed UE vehicle template supplies the skeletal rig, physics asset, wheel bones and animation. `/Game/Vehicles/BP_PrototypeMotorhome` configures that replaceable rig and a primitive shell labeled PROTOTYPE RV. `/Game/Maps/Gate2VehicleTest` has RVGameMode, two Player Starts, a 300 m square flat driving area, roadside reference blocks and movable exit blockers. Gate1Test and startup/default map selection are preserved.

C++ foundation: ARVVehicleBase, ARVMotorhome, URVVehicleMovementComponent, URVVehicleSeatComponent, ARVVehicleEntryPoint, URVVehicleWheelFront and URVVehicleWheelRear. Existing survivor/controller/HUD handle seat attachment, possession, input mapping lifetime, exit and disconnect. Entry reuses the accepted Gate 1 0.5 s hold interaction.

## Configuration

3500 kg; center of mass override (0, 0, 10) cm; rear-wheel drive; automatic transmission/reverse; 850 Nm maximum torque; 4500 maximum / 800 idle RPM. Four 50 cm radius, 30 cm width wheels on PhysWheel_FL/FR/BL/BR; front steering 32 degrees; suspension spring 1000, damping ratio 0.7, maximum raise 10 cm/drop 20 cm. Prototype handling is provisional. Recorded transmission settings: final ratio 3.08, gear-change time 0.4 s; forward ratios [2.85, 2.02, 1.35, 1, 2.85, 2.02, 1.35, 1], reverse ratios [2.86, 2.86]. Exact loaded values, physics asset and wheel settings are in fixture.json. Physics prediction and async physics ticking are disabled; gravity is -980 cm/s². Native physics replication uses autonomous-proxy updates, with 60 Hz maximum / 30 Hz minimum actor updates.

Driver/passenger seat positions (90, -55/+55, 110) cm; entry offsets (90, -170/+170, 90); exit offsets (90, -300/+300, 0). Additional seat components reuse the same assignment/entry/exit implementation. Entry and exit require speed <=150 cm/s. Exit rejects steep ground, obstacle roofs/drops and capsule overlap; blocked exits retain occupancy.

Server alone integrates Chaos vehicle forces. Owned controller sends bounded input intent at 20 Hz, with 0.5 s server timeout. Native replicated rigid-body movement updates simulated and autonomous proxies. Client Chaos manager force updates and proxy gravity are disabled; clients receive server vertical motion. Chaos network physics prediction is disabled. No client transform RPC or moving-interior solution.

## Test method and evidence

Tests execute in live Unreal PIE using synthetic Enhanced Input `Input.+key` / `Input.-key` commands. Server teleports characters only to arrange repeatable fixtures, and resets the vehicle between driving phases. Driving assertions measure actual Chaos movement from input, possession and replicated seat references; they do not inject vehicle travel. This is technical input-path validation, not physical keyboard device certification. JSON assertion results and successful build logs are stored in `Docs/Gate2Results/2026-10-05`.

The final C++ build succeeded (27.26 seconds, VS 14.44.35229 / Windows SDK 10.0.22621.0). All gameplay failures were fixed and rerun on the final build. The final evidence contains **133 passing assertions, zero failed**: 90 live Gate 2 assertions, 20 comparisons of paired live replication samples, and 23 Gate 1 regression assertions. Repeated development runs are not added to this total.

| Executed suite | Passed / total | Results |
|---|---:|---|
| Two-player listen server, one process | 24 / 24 | Host/client driver possession; both driver/passenger combinations; occupied-driver rejection; acceleration, steering, reverse and handbrake; movement/attachment replication; moving-exit rejection; normal exit/possession restore; all exit candidates blocked then cleared |
| Concurrent driver claims, continued entry hold | 2 / 2 | Exactly one winner; no exit caused by the prolonged entry hold; fresh E press releases seat |
| Two-player listen server, separate processes | 27 / 27 | 15 host + 12 client assertions; both driving/seating combinations, occupancy agreement, exit, remote-driver disconnect, RV preservation and driver-seat reuse |
| Separate processes, outgoing server latency 100 ms and packet loss 2% | 27 / 27 | Same host/client seat, driving, exit, disconnect and reuse assertions; no permanent seat lock |
| Separate-process passenger disconnect | 10 / 10 | 7 host + 3 client assertions; passenger seat freed while driver remains; driver exits; walking and jump restored |
| Gate 1 single-player regression | 15 / 15 | WASD, mouse axes, jump, prompt, hold completion/no-repeat, early release, aim/range/line-of-sight cancellation, initial count reset |
| Gate 1 listen-server regression | 8 / 8 | Independent movement, host/client increments, simultaneous two increments, continued holds/no duplicates, remote early release, initial count reset |
| Paired separate-process replication samples | 20 / 20 | Ten baseline + ten emulated-network position/occupancy comparisons |

Baseline moving position differences were 9.33 and 9.42 cm; stopped differences were 2.47 cm. With network emulation, moving differences were 80.54 and 78.46 cm; stopped differences were 3.53 and 3.32 cm. Acceptance limits were 100 cm baseline/stopped and 250 cm emulated moving samples. All paired seat occupancy states agreed. Measured server gravity was enabled and client proxy gravity disabled. These samples establish basic synchronization, not a general latency/prediction guarantee.

Gate1Test's file was not resaved by Gate 2, and Editor Startup Map/Game Default Map remain Gate1Test. The final editor is open on Gate2VehicleTest, PIE stopped, with two-player listen-server/Run Under One Process enabled, additional launch arguments cleared, network emulation disabled, background throttling restored and FPS cap removed.

## Failures found and fixes

- Chaos world vehicle manager still updated client vehicles with component ticking disabled. Authority guards now cover PreTickGT and Update; the inherited Chaos input RPC ignores client values and uses server-processed values.
- A blocked exit could select the roof of an obstacle. Ground-height checks now reject obstacle roofs and excessive drops before capsule clearance.
- Separate-process parked client physics sank because no local suspension counterbalanced gravity, moving the client entry target below the server target. Client proxy gravity is disabled, leaving vertical motion to replicated server physics. Both multiplayer seating combinations passed after this fix.
- A prolonged E hold crossing driver possession could be interpreted as exit by the new input context. Driver exit now arms only after the entering key/action is released. The prolonged-hold race and fresh exit press passed on the final build.
- Passenger entry label orientation corrected for the opposite side of the prototype.

## Known limits

Prototype rig/body collision and handling require replacement/tuning for production art. Native server physics replication has visible correction and latency limits; no prediction or Gate 3 passenger reference frame is implemented. Seated survivors are fixed to seats and cannot walk or jump inside the moving RV. Fuel, damage, inventory and all other later-gate gameplay are absent.



## Editor automation issue and recovery

After every gameplay suite and regression passed, reloading the editor map from the final Slate Python cleanup callback caused an access violation in python311.dll/PythonScriptPlugin during map cleanup. No RV gameplay frame appears in the recorded crash stack. This is an observed editor automation limitation, not proof of its underlying engine root cause. The crash evidence is retained in cleanup_crash.log. The harness now unregisters its callback before cleanup and leaves map switching outside that callback. The saved project reopened successfully; the corrected cleanup function was rerun and logged GATE2_CORRECTED_CLEANUP_PASS. No gameplay assets were lost, and no crash occurred during the acceptance PIE suites. Avoid callback-driven map reloads in this harness; the engine-level crash itself has not been repaired.

## Files changed

- New Vehicles public/private pairs: RVVehicleBase, RVMotorhome, RVVehicleSeatComponent, RVVehicleEntryPoint, RVVehicleMovementComponent and RVVehicleWheel (front/rear classes).
- New RVPlayerController.cpp and updated controller header; updated survivor header/source and prototype HUD for seat/input/possession lifecycle.
- RVSurvival.Build.cs and RVSurvival.uproject enable the supported Chaos dependency/plugin; existing engine association is preserved.
- New Gate2VehicleTest.umap, BP_PrototypeMotorhome.uasset and required installed vehicle-template content dependencies. Gate 1 content/configuration is preserved.
- Updated RV_SYSTEM, TECHNICAL_ARCHITECTURE, NETWORKING, ROADMAP, current GAME_DESIGN scope, CHANGELOG and this validation document. Permanent JSON/log/configuration evidence and rerun scripts are in Docs/Gate2Results/2026-10-05.

Gate 2 is accepted for this two-player listen-server vehicle foundation. Five-player, packaged and dedicated-server validation have not been performed. Stop here: no Gate 3 moving-interior work or later gameplay systems were added.
