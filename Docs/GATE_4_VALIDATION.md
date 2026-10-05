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

Automation fix: use the map-specific `EditorLoadingAndSavingUtils.save_map`, keep World/Actor wrappers within short function scopes, release those scopes and Python garbage before the next load, and load the saved target through LevelEditorSubsystem. Fixture configuration is performed on the explicitly loaded Gate 4 map. Save Map writes a copy without changing the current editor world; this distinction is now accounted for. No engine leak checks, object flags, or engine source were altered.

Repeat tests use unique scratch map paths to avoid attempting to overwrite already loaded test copies. An attempted reuse of an existing scratch path produced an asset duplication warning, rather than the world-leak fatal; the runner now uses unique names.

Recovery found setup retries had produced 22 pickups/12 storage actors. Only duplicate Gate 4 actors at identical positions were removed. The saved recovered map contains 61 editor actors, including exactly 11 pickups and 6 storage points. Existing saved content was recovered rather than rebuilt from memory.

`Tools/Validation/gate4_recovery_repeat.py` repeated the corrected save-copy/reopen sequence three times, each followed by loads of Gate1Test, Gate2VehicleTest, Gate3MovingInteriorTest and Gate4InventoryTest. **24/24 checks passed**, followed by normal editor shutdown. `recovery-repeat.json` and `recovery-clean.log` record these results. The earlier three cycles also completed map changes and clean shutdown, but failed fixture-count assertions because of the duplicate setup actors; those results are retained separately. Scratch maps are recovery-test artifacts, not gameplay additions.

Live Gate 1–3 regression checks are pending following this recovery. Gate 4 acceptance remains blocked until those and the inventory/moving-storage/network matrix pass.

## Implemented foundation, not yet accepted

URVItemDefinition is a Primary Data Asset with catalog ID, presentation references, mass, volume, stack configuration, condition/equipment/physical-carry flags and gameplay/crafting tags. FRVItemInstance holds GUID, definition, quantity, condition, location and serializable key/value custom state. Stored items are FastArray records rather than Actors. URVInventoryComponent and reusable URVContainerComponent share capacity and authoritative transfer rules. ARVWorldItem reuses the accepted hold interaction; ARVStoragePoint opens shared cabinets. Owned inventory RPCs revalidate proximity and line of sight before transfers. A temporary Canvas inventory view shows player/container contents and capacity feedback.

The initial compiled foundation and subsequent UI build succeeded. Initial compiler issues were corrected: DOREPLIFETIME requires OutLifetimeProps, TObjectPtr requires explicit Get for pointer deduction, and replicated custom state uses an array rather than unsupported TMap replication. Latest build has a cosmetic float-literal warning pending cleanup.

Eleven inert logistics definitions include water, food, bandage, pain medication, fuel can, engine part, scrap, hand tool, inert ammunition, bulky supply crate and large battery. The battery is excluded from ordinary player storage; active hand carrying is not implemented yet. RV storage points: pantry, general cabinet, medical, tools and exterior compartment, plus external storage. Six Gate 3 workstation placeholders remain.

Early PIE attempts passed host pickup, non-stackable pickup, and weight/volume blocking, but failed drop identity and selected-container checks with the duplicated fixture. They are development failures, not accepted results. Full reruns after recovery remain required.
