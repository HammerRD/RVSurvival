# Gate 4 validation

Status: **NOT ACCEPTED — development and regression validation in progress.** Gate 5 has not begun.

## Recovery checkpoints

- `2e9abe3`: preserved latest passing Gate 1 regression evidence before Gate 4.
- `55a1522`: explicitly marked WIP recovery, compiled inventory/item authority foundation.
- `436eb58`: explicitly marked WIP recovery, item definitions/UI and initial saved map.
- `6132ceb`: preserved the populated saved map before further crash investigation.
- `aa8f8c7`: recovered duplicate fixture actors and saved crash investigation tools/evidence.

Vendor `/Game/RV` and accepted Gate 1–3 map files are preserved. Existing user changes to DefaultEngine.ini and IDE files remain outside these commits.

## Editor automation crash, 2026-10-05 21:41 UTC

UE 5.8.3 CL 58210709 raised EditorServer.cpp line 2544, `World Memory Leaks: 2 leaks objects and packages`. Evidence: `Gate4Results/CrashRecovery/world-leak.log`; original crash directory `Saved/Crashes/UECC-Windows-AED99C0042A8FC0AFA855E96D9AF728F_0000`.

Immediately before the fatal error, Unreal identified:

- `(standalone) World /Game/Maps/Gate4InventoryTest.Gate4InventoryTest`, retained by garbage-collection keep flags. Reference search explicitly reported no reachable target objects.
- `Package /Game/Maps/Gate4InventoryTest`, retained through that World’s package link.

The failing startup `Saved/Gate4Validation/fixture.py` called generic `EditorAssetLibrary.duplicate_asset` on the loaded Gate 3 map, then `LevelEditorSubsystem.load_level` on the duplicated world. The duplicate was initialized in memory before the loader tried to unload/reuse it. The installed EditorServer source only allows uninitialized worlds to be reused and fails if an initialized target world/package survives unloading. The observed retention is the duplicated world’s standalone/keep state; the log does **not** identify an actor cache, Python delegate, timer, PIE world, or reachable Python variable as its retaining root. No PIE or Slate test callback had begun at this point. PythonScriptPlugin appears because Python invoked LoadLevel.

The installed EditorAssetLibrary.h explicitly documents that its operations do not work on assets of type level. This was an unsupported automation API choice, rather than a gameplay change or an identified test delegate leak.

Automation fix: use the map-specific `EditorLoadingAndSavingUtils.save_map`, keep World/Actor wrappers within short function scopes, release those scopes and Python garbage before the next load, and load the saved target through LevelEditorSubsystem. Fixture configuration is performed on the explicitly loaded Gate 4 map. Save Map writes a copy without changing the current editor world; this distinction is now accounted for. No engine leak checks, object flags, or engine source were altered.

Repeat tests use unique scratch map paths to avoid attempting to overwrite already loaded test copies. An attempted reuse of an existing scratch path produced an asset duplication warning, rather than the world-leak fatal; the runner now uses unique names.

Recovery found setup retries had produced 22 pickups/12 storage actors. Only duplicate Gate 4 actors at identical positions were removed. The saved recovered map contains 61 editor actors, including exactly 11 pickups and 6 storage points. Existing saved content was recovered rather than rebuilt from memory.

`Tools/Validation/gate4_recovery_repeat.py` repeated the corrected save-copy/reopen sequence three times, each followed by loads of Gate1Test, Gate2VehicleTest, Gate3MovingInteriorTest and Gate4InventoryTest. **24/24 checks passed**, followed by normal editor shutdown. `recovery-repeat.json` and `recovery-clean.log` record these results. The earlier three cycles also completed map changes and clean shutdown, but failed fixture-count assertions because of the duplicate setup actors; those results are retained separately. Scratch maps are recovery-test artifacts, not gameplay additions.

Post-recovery live Gate 1 regression passed 23/23 checks; Gate 2 shared listen-server driving/seating passed 24/24. Both editors shut down normally after callback/module release. Gate 3 host-driver/client-walker passed 42/42 and client-driver/host-walker passed 42/42, including highway speed, acceleration/braking, turns, six workstation interactions, exit and re-entry. Both editor shutdowns were clean. Gate 4 work resumed after these regressions. All 108 purchased vendor source files match the accepted Gate 3 SHA-256 manifest; accepted Gate 1–3 maps have no Git diff. Gate 4 acceptance remains blocked until those and the inventory/moving-storage/network matrix pass.

## Implemented foundation, not yet accepted

URVItemDefinition is a Primary Data Asset with catalog ID, presentation references, mass, volume, stack configuration, condition/equipment/physical-carry flags and gameplay/crafting tags. FRVItemInstance holds GUID, definition, quantity, condition, location and serializable key/value custom state. Stored items are FastArray records rather than Actors. URVInventoryComponent and reusable URVContainerComponent share capacity and authoritative transfer rules. ARVWorldItem reuses the accepted hold interaction; ARVStoragePoint opens shared cabinets. Owned inventory RPCs revalidate proximity and line of sight before transfers. A temporary Canvas inventory view shows player/container contents and capacity feedback.

The initial compiled foundation and subsequent UI build succeeded. Initial compiler issues were corrected: DOREPLIFETIME requires OutLifetimeProps, TObjectPtr requires explicit Get for pointer deduction, and replicated custom state uses an array rather than unsupported TMap replication. Latest build has a cosmetic float-literal warning pending cleanup.

Eleven inert logistics definitions include water, food, bandage, pain medication, fuel can, engine part, scrap, hand tool, inert ammunition, bulky supply crate and large battery. The battery is excluded from ordinary player storage; active hand carrying is not implemented yet. RV storage points: pantry, general cabinet, medical, tools and exterior compartment, plus external storage. Six Gate 3 workstation placeholders remain.

Early PIE attempts passed host pickup, non-stackable pickup, and weight/volume blocking, but failed drop identity and selected-container checks with the duplicated fixture. They are development failures, not accepted results. Full reruns after recovery remain required.



## First passing inventory milestone

After fixture recovery, 13/13 live two-player listen-server inventory checks pass: host pickup; complete drop/re-pick with GUID and condition preserved; non-stackable item; independent weight and volume rejection; container opening; both transfer directions; client pickup replication; client transfer replicated to host and client; simultaneous world-pickup contention yielding one winner; condition preservation.

Client transfer diagnostics initially executed on role 2 because Unreal Python editor execution sets GAllowActorScriptExecutionInEditor, which AActor::GetFunctionCallspace handles as local execution. Local request methods now dispatch through next native-world tick using weak timer delegates, and every server mutation explicitly checks authority. The same unchanged transfer assertion then passed with role 3 server execution. Weak delegates do not retain pawns/worlds and recheck local control after possession changes. Inventory view can now close a container through authoritative intent. Latest build succeeded without the earlier cosmetic float warning.

This is a stable partial milestone, not Gate 4 acceptance. Separate-process, emulated network, expanded contention/disconnect, true standalone and moving-RV storage tests remain required.

## Resumed checkpoint and expanded checks

`8d8cbb3` records the passing 13-check inventory baseline; `e2d0c15` records the compiled actor/metadata/drop-safety recovery checkpoint; `6d0257c` records saved exposed cabinet markers and passing expanded results. The expanded shared listen-server suite passed **24/24**, including concurrent container use, contested withdrawal/pickup, immediate repick, foreign-ID rejection, condition/custom-state preservation and disconnect integrity. Single-player PIE passed **10/10**. Results are `Gate4Results/full.json` and `single.json`.

The first moving-storage run exposed cabinet markers behind furniture collision. Project-side markers were moved onto exposed aisle-facing surfaces without disabling furniture collision, reach or line-of-sight checks. The subsequent host-driver/client-walker run passed stationary, low-speed (478 cm/s), road-speed (1788 cm/s), turning medical and moving tool storage transfers and returns, with GUID, condition and custom state preserved and zero measured passenger corrections during storage. All embedded Gate 3 movement/workstation checks passed. Its additional moving-drop lookup failed at 172 seconds because no matching pickup was found; diagnosis and rerun remain required. The editor shut down normally. This partial run is preserved as `Gate4Results/moving-drop-failure.json` and is not acceptance evidence for its failed cases.

Separate-process inventory/storage, representative emulation, native HUD checks and final cleanup remain pending. Gate 4 remains NOT ACCEPTED.

### Moving drop root cause and targeted fix

A short reproduction confirmed authoritative rejection with `No safe drop location`, preserving the original item. Development-gated collision diagnostics found rear-cabinet sweep obstructions and three floor rays hitting the coarse `VehicleMesh` chassis 152 cm above the passenger's feet. The floor ray used WorldStatic, whereas accepted cabin collision and safe vehicle exits use Visibility. The minimal fix changes only that support-ray channel to Visibility. Height, surface-normal, path clearance and landing-overlap rejection remain enabled; vehicle/passenger physics were not modified. The targeted reproduction then passed: the tool spawned on the interior floor, feedback cleared, source item removed. Before/after results and exact blocked component lines are retained. Development Editor build passed. Full moving drop/repick and networking reruns follow.

Full rerun after the drop fix: **63/63 host-driver/client-walker assertions passed**, including the embedded Gate 3 suite, stationary/low/road/turning storage, category rejection, moving floor attachment and repick preserving GUID/condition. Maximum measured visual observer discrepancy 10.18 cm; storage stages had zero corrections/floor loss. Normal editor shutdown at 2026-10-06 00:20:45 UTC. Results and log: `Gate4Results/moving_host.json` and `moving_host-clean.log`. Separate-process cases remain pending.

Two-process inventory: host PID 49556/client PID 48992 passed 12 + 13 live checks, with 33 exact GUID/definition/quantity/condition state comparisons matching across player inventories and shared container. Covered concurrent deposits, contended withdrawal, full container rejection, replicated client drop, contested immediate repick, forged source ID, contended pickup, custom state, client authority rejection and disconnect integrity. Repeated with host PID 5980/client PID 25972 and outgoing server 100 ms/2% loss: 12 + 13 checks passed. Engine log explicitly reports PktLagMin=100, PktLagMax=100, PktLoss=2. Both host editors shut down normally; clients disconnected without retained-world fatal errors.

The first separate-process moving runner failed before gameplay with a Python SyntaxError caused by a missing newline in generated script assembly. Corrected it, syntax-checked all 29 current Gate 4 runners using the engine's bundled Python, and closed the failed test editor from its saved state. No gameplay or content changes were lost. The failed startup log is retained; it is not a passing test result.

## Resume after user pause

Recovered checkpoint `f71bf8b` without content/source drift. The saved Gate 4 map is intact. The interrupted separate-process client-driver run was restarted. Server-side storage/drop/repick passed, but the remote driver received no matching dropped pickup; its receipt failed at 172 seconds. The failure is retained as `process-moving-client-drop-failure.json/.log`.

Inspection of installed ActorReplication.cpp showed that default attachment relevancy delegates to the parent only for skeletal attachments or matching owner. Cabin cargo attaches to a query floor box. ARVWorldItem now explicitly delegates relevancy to its attached platform; unattached world pickups retain native distance culling. No client authority or passenger movement behavior changed. The prototype inventory HUD also scales both panels to fit small PIE windows. Development Editor build passed (34.82 seconds). Exact failed-case and emulated reruns are in progress; Gate 4 remains NOT ACCEPTED.

The unchanged failed remote-driver pickup assertion now passes after attached-platform relevancy delegation. Full separate-process client-driver/host-walker results, GUID/state comparisons and cleanup logs are saved under `Gate4Results/process_moving_client*`. No assertion was removed or weakened.

The first emulated moving run cached workstation actors before their replicated StationName fields arrived; the client lookup failed with KeyError('Workbench'). Restored the accepted Gate 3 readiness requirement: all six station names must be present before coordinated tests begin. Early runner failures now record missing movement samples as failures instead of raising a second exception during result collection. Thresholds/gameplay assertions remain unchanged. Failed emulation startup log is retained; the session was stopped with callbacks/references released and no map reload or crash.

Separate-process host-driver/client-walker under outgoing-server 100 ms/2% loss passed 61 server + 62 client live assertions and 81 paired state/position checks. Maximum paired local-position discrepancy was 12.03 cm. Fixed workstations and moving cabinets passed at stationary, low/road/highway speed, acceleration/braking, gentle/strong turns, exit/re-entry and moving drop/repick. Host editor shutdown was clean. Results: `Gate4Results/process_moving_host_emulated*`. Final native HUD and regression checks remain pending.
