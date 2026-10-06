# Gate 4 validation

Status: **ACCEPTED on 2026-10-05 (America/New_York).** Gate 5 has not begun.

## Implemented architecture

- `URVItemDefinition`: Primary Data Asset catalog, display/description/category, optional mesh/icon, kg/L per unit, stack maximum, condition/equipment/physical-carry flags, gameplay and future crafting tags.
- `FRVItemInstance`: GUID, definition asset, quantity, normalized condition, location identifier and key/value custom state. Stored items are lightweight FastArray records, not Actors. Full-record transfers retain GUID; splits receive a new GUID and preserve condition/custom state. Transport bookkeeping is reset on each destination array.
- `URVInventoryComponent` and `URVContainerComponent`: shared tunable weight/volume/filter rules and server-only serial transactions. Player storage defaults to 25 kg/35 L. A physical-carry item cannot enter ordinary player storage. Capacity failure leaves the source unchanged.
- `ARVInventoryInteractable`, `ARVWorldItem`, `ARVStoragePoint`: reuse accepted 0.5-second Gate 1 interaction. One server winner claims a pickup. Owned inventory requests identify existing records and quantities; server revalidates authority, availability, selected container, 300 cm reach and Visibility line of sight. Clients cannot submit definitions or fabricate authoritative instances.
- FastArray contents and capacities replicate to relevant viewers; selected container/feedback are owner-only. Weak native next-tick intent dispatch avoids editor Python script guards forcing local RPC callspace. Each server mutation still checks authority explicitly.
- Drop searches clearance and safe floor support with Visibility collision, rejects excessive height changes, and preserves item state. Cargo on tagged passenger floors uses native replicated attachment and inherits platform relevancy. Unattached pickups retain native distance culling. Standing passengers remain native CharacterMovement pawns; no passenger tick teleport/attachment was added.
- `ARVPrototypeHUD`: minimal Canvas UI, separated from gameplay state. I toggles, Tab selects panel, Up/Down selects row, T transfers one, G drops one. Shows quantity, condition, weight, volume and rejection feedback; scales to 640×480. Normal movement/input remains enabled.

Foundational files are under `Source/RVSurvival/Public/Inventory` and `Private/Inventory`. Integration changes: survivor inventory default component, prototype HUD and GameplayTags/NetCore build dependencies. Vehicle/seat/possession/passenger movement implementations and purchased source art remain independent.

## Saved content and setup

`/Game/Maps/Gate4InventoryTest` preserves the purchased Class C derivative, two player starts, 10 km driving space and six Gate 3 workstation placeholders. Saved editor fixture: 61 actors, exactly 11 pickups and six storage points. Gate 1–3 maps and fallback vehicles are preserved; default/startup map remains Gate1Test.

Five RV points use the reusable component: pantry, general cabinet, medical, tools and exterior compartment; each has 100 kg/60 L capacity. External storage has 100 kg/120 L capacity. Pantry accepts food/water tags, medical accepts medical, and tools accept tool/material/automotive; general/exterior storage are unrestricted within capacity. Interior markers sit on exposed aisle-facing furniture surfaces. No furniture collision or reach/LOS checks were disabled.

Inert Data Assets in `/Game/Items`:

| Item | kg | litres | max stack | Special metadata |
|---|---:|---:|---:|---|
| Bottled water | 1.1 | 1.2 | 6 | Water |
| Canned food | 0.45 | 0.5 | 10 | Food |
| Bandage | 0.05 | 0.1 | 10 | Medical |
| Pain medication | 0.05 | 0.1 | 5 | Medical |
| Fuel can | 12 | 22 | 1 | Automotive |
| Engine part | 18 | 8 | 1 | Automotive |
| Scrap metal | 2 | 1 | 10 | Metal crafting metadata |
| Hand tool | 1.5 | 2 | 1 | Equipment eligible; tool metadata |
| Inert ammunition box | 1 | 1 | 5 | No weapon behavior |
| Bulky supply crate | 2 | 40 | 1 | Exceeds normal player volume |
| Large battery | 30 | 25 | 1 | Requires physical carrying; excluded from backpack |

Fixture condition is 73%, with Batch custom state. Moving-storage fixtures use 62% and MovingStorageTest Batch. These values make preservation measurable. No hunger, thirst, fuel consumption, medicine, crafting, combat or later-gate effects exist.

## Build and actual validation

UE **5.8.3 CL 58210709**, Development Editor/Win64, VS 14.44.35229, Windows SDK 10.0.22621.0. Final gameplay/UI build succeeded in 34.82 seconds (`Gate4Results/build-cargo-relevance-ui.log`). No engine source changes.

Tests use real PIE, accepted Enhanced Input key actions, actual hold interactions and owned native inventory intent. Initial fixture positioning/item seeding is labeled setup; walking/driving/transfers/completions are not simulated by rewriting results or transforms. Independent processes record their own world state; paired comparisons verify GUID, quantity, condition, custom state and passenger position. Native HUD controls were additionally exercised with OS keyboard input on a focused client viewport.

| Run | Result | Receipt |
|---|---|---|
| Shared inventory baseline | 13/13 | `baseline.json` |
| Expanded two-player inventory | 24/24 | `full.json` |
| Single-player PIE | 10/10 | `single.json` |
| Shared host-driver/client-walker storage + Gate 3 route | 63/63 | `moving_host.json` |
| Separate-process inventory | 12 server + 13 client, 33 exact paired checks | `process_inventory*` |
| Separate-process inventory, 100 ms/2% loss | 12 server + 13 client, 33 exact paired checks | `process_inventory_emulated*` |
| Separate-process host driver/client walker | 61 server + 62 client, 81 paired checks | `process_moving_host*` |
| Separate-process client driver/host walker | 63 server + 56 client, 81 paired checks | `process_moving_client*` |
| Separate-process host driver/client walker, 100 ms/2% loss | 61 server + 62 client, 81 paired checks | `process_moving_host_emulated*` |
| Native remote-client HUD at 640×480 | Seven state checks + visual/key review passed | `native-ui.json`, `ui-samples.json` |
| Final Gate 1 regression | 23/23; clean shutdown | `Gate1Regression` |
| Final Gate 2 regression + inventory possession | 24/24 + 4/4; clean shutdown | `Gate2Regression` |
| World recovery map-cycle checks | 24/24; clean shutdown | `CrashRecovery` |

Required inventory cases passed: weight and volume rejection independently; stack/non-stack behavior; full drop/repick retaining GUID and condition; both transfer directions; full container with no partial loss; two users/concurrent deposits; contested withdrawal; same-pickup one winner; immediate contended repick; foreign-ID/client-authority rejection; replicated client changes and dropped items; disconnect preserving shared contents. Stable IDs and Batch state survive transfers. Quantity conservation and unique IDs are checked.

Moving cabinets passed stationary, approximately 480 cm/s low speed and 1780 cm/s road speed, including actual gentle steering during medical transfer. The embedded Gate 3 route additionally tests approximately 2670 cm/s highway speed, front/rear/sideways walking, acceleration, braking, gentle/strong turns, stop/resume, six workstations, outside movement and re-entry. Neither driving role lost the passenger floor or accumulated unstable positional error. Transfers did not stop walking or alter movement mode.

Network emulation is **outgoing server** Min/MaxLatency 100 ms, PacketLoss 2%, with Run Under One Process disabled. Engine logs explicitly confirm PktLagMin=100/PktLagMax=100/PktLoss=2. It is not a claim of bidirectional 100 ms. Maximum paired passenger local-position discrepancy: host-driver baseline 14.50 cm, client-driver baseline 8.73 cm, emulated host-driver 12.03 cm. Emulated strong-turn standing drift peaked at 3.44 cm; two corrections, max 1.76 cm. Braking had one 1.91 cm correction. Storage stages had no measured correction/floor loss. Small corrections were usable; no severe persistent jitter, sliding, floor penetration or launches occurred in these runs.

Native client UI review confirmed readable capacities/73% condition and quantity, actual T deposit/withdrawal, Tab panel selection, Up/Down row selection, G tool drop, clear Volume capacity exceeded feedback with source preserved, and I close/reopen without stale container access. Replicated state matched the server. A normal PIE click is needed to give its viewport keyboard focus.

## Failures investigated and fixed

- Unsupported generic World duplication caused the editor world-leak fatal; full recovery/root cause/repeat results follow below. Leak detection remains enabled.
- Setup retries duplicated pickup/storage actors. Removed only duplicate Gate 4 fixtures and saved the known map, preserving accepted content.
- Direct Python RPC execution was local under the editor script guard. Native weak next-tick dispatch and explicit server guards fixed authority; unchanged assertions then passed on server role 3.
- Cabinet markers behind furniture blocked interaction. Moved project-side markers to exposed surfaces while preserving collision and LOS validation.
- Drop WorldStatic rays hit the coarse vehicle chassis 152 cm above passenger feet. Changed support queries to the existing cabin Visibility collision, retaining clearance/normal/height checks. Before/after receipts and full moving reruns pass.
- A floor-attached drop did not reach the remote client driver. Native attachment relevancy only delegates for certain parent types; floor boxes did not qualify. Attached pickups now delegate to the platform. The unchanged failed assertion and independent GUID/state comparisons pass after the fix; world pickups retain distance culling.
- Runner assembly had a missing newline, producing a startup SyntaxError. Corrected and syntax-checked archived/current scripts, then cleanly restarted. No gameplay success was claimed for that run.
- Emulated initialization cached workstations before replicated names arrived. Restored Gate 3's six-name readiness check and made early errors produce failed receipts. Kept all gameplay thresholds unchanged.

Failed receipts/logs are retained separately from passing evidence. No unrelated vehicle or passenger redesign was made.

## Known limits and scope

No full persistence/reconnect/death inventory, active hand/two-person carrying, equipment use, recipes, survival effects or cargo-mass adjustment to Chaos handling. Large battery exclusion provides the carried-object boundary, not the final hands mechanic. Compatible stacks do not auto-merge; partial records remain identified stacks. UI is prototype Canvas, without final icons/art, rebinding, large-list pagination or seated-driver inventory presentation. Pickups are query-only cube placeholders; generalized mesh-size-aware drop bounds and dynamic loose-cargo physics are future work. Rough terrain/airborne passengers/larger sessions remain Gate 3 limitations, not newly validated cases. Existing CreateSavedMove warnings are retained as non-blocking prototype warnings.

Definitions, lightweight records, location identifiers and reusable container queries preserve future equipment, workstation/linked-storage, serialization and mobile-base systems. None of those later gameplay systems was implemented.

## Saves and local recovery checkpoints

Saved item assets/map after fixture, metadata and exposed-marker milestones, before risky reloads and after recovery. Saved editor state was restored on resume, not recreated. World/actor wrappers are scoped; callbacks are unregistered and module-owned runner references released while Python/Unreal are alive. Completed runs stop PIE and shut down normally.

Milestones: `2e9abe3` pre-Gate 4 evidence; `55a1522`, `436eb58`, `6132ceb` explicitly labeled WIP recovery; `aa8f8c7` crash recovery; `7a96ac3`, `b426f1c`, `4ea32a0` recovery/regressions; `8d8cbb3` tested inventory baseline; `e2d0c15` compiled recovery; `6d0257c` expanded checks/markers; `54a95bf` documentation checkpoint; `d370a05` drop collision fix; `7ac446d` shared moving storage; `8f8c86a` separate/emulated inventory; `0d33d3b` corrected runner; `f71bf8b` user pause recovery; `ab9af07` remote-driver cargo fix; `525f9ad` replicated readiness; `ca3c86b` emulated moving storage; `0580113` native UI. Final regression/documentation checkpoint completes this gate.

Vendor integrity: all 108 files match the accepted Gate 3 SHA-256 manifest. Gate 1–3 maps and fallback assets have no changes. Existing user DefaultEngine.ini/IDE changes are excluded from these commits and preserved. No Git push or later gate work.

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

Post-recovery live Gate 1 regression passed 23/23 checks; Gate 2 shared listen-server driving/seating passed 24/24. Both editors shut down normally after callback/module release. Gate 3 host-driver/client-walker passed 42/42 and client-driver/host-walker passed 42/42, including highway speed, acceleration/braking, turns, six workstation interactions, exit and re-entry. Both editor shutdowns were clean. Gate 4 work resumed after these regressions. All 108 purchased vendor source files match the accepted Gate 3 SHA-256 manifest; accepted Gate 1–3 maps have no Git diff. At that recovery checkpoint, inventory/moving-storage/network validation remained pending; final results above now satisfy it.
