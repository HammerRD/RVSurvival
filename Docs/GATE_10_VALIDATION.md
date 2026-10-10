# Gate 10 - Western New York playable region

Status: IN PROGRESS. Not accepted. Baseline: 81b65c9. Gate 11 is not started.

## Framework review and planned boundaries - 2026-10-10

Use native World Partition/One File Per Actor for the first region, Landscape for terrain,
native spline mesh roads, editor-generated partitioned PCG for dressing, instanced static
meshes for repeated decoration, and Recast NavMesh/accepted AI Perception for infected.
No custom streaming, foliage, navigation or animation engine. HLOD is evaluated after
the authored layout is stable. Mass is unnecessary for bounded nearby prototype AI.

The installed Electric Dreams sample is a reference and candidate selective asset source,
not a map to copy wholesale. Its default large demonstration disables streaming and
has substantial resource requirements; those defaults are unsuitable for this gate.
Sources: [Epic sample](https://dev.epicgames.com/documentation/en-us/unreal-engine/electric-dreams-environment-in-unreal-engine),
[Epic PCG examples](https://dev.epicgames.com/documentation/en-us/unreal-engine/procedural-content-generation-in-electric-dreams).
Asset dependency and license review must precede importing selected content.

RVSurvival-specific code will own contextual finite loot, stable searched-container
identity, bounded location populations and encounter pacing. Native replication and
accepted inventory transactions remain responsible for ownership and transport.
Session state must outlive streamed actors; unloading/reloading must not reroll loot.
Full campaign persistence and cross-region travel are outside scope.

## Recovery baseline

Accepted map/content checkpoint 81b65c9 verified in local Git. Pre-existing unrelated
changes: Config/DefaultEngine.ini, .vsconfig, Automation_RVSurvival.slnx,
RVSurvival.slnx. These are excluded from Gate 10 work. Prior maps/vendor content are
preserved. No new assets, world, runtime tests or acceptance results are claimed yet.

## Saved foundation checkpoints

- d03ee50: framework review before world changes.
- 34938ed: compiled loot/session ledger and native Landscape bridge; saved new
  World Partition map and external actor packages. Terrain span 4032 m.
- First save automation used an unavailable LevelEditorSubsystem SaveAs method;
  corrected to native EditorLoadingAndSavingUtils.SaveMap. Failed receipt retained
  locally; retry saved successfully and editor exited cleanly. No world-leak crash.
- Selective native AssetTools migration completed: five Epic Electric Dreams
  deciduous vegetation/rock mesh seeds, 95 dependency packages, 950554631 bytes.
  Original installed sample SHA256 values were checked unchanged after migration.
  No paid download or full sample map import. Runtime/material/PCG use is pending.

## Required closure evidence

Pending: saved World Partition/Landscape world, 4-6 km useful road route, five authored
locations and usable interiors, PCG dressing, finite contextual loot, difficulty-linked
population, quiet encounter outcomes, actual drive/scavenge/store playthrough,
stream-out/return conservation, separate-process host/client and representative
100 ms/2% loss, performance observations, targeted regressions, final build,
108 vendor hashes and clean editor shutdown.

## Additional foundation work - 2026-10-10

- ae5a573 saved the native spline road network: 6.0106 km of authored route,
  12 m main road and 9 m secondary road. Actual driving validation is pending.
- Partitioned native PCG generated 6019 aggregate instances, but scheduling
  aborts occurred. Aggregate counts are not acceptance evidence; per-component
  generation and saved-state inspection remain required.
- Five enterable prototype location shells and ten contextual supply containers
  were saved. Interior visual/player-path validation and navigation are pending.
- Location automation first failed on Python GUID construction; corrected to
  GuidLibrary parsing and label-based resumable authoring, with saves per site.
- A failed editor remained alive after destroying its windows and reaching
  "Preparing to exit". A second editor could not replace the map file held by
  that process. After stopping the already-failed shutdown process, the single
  editor retry saved all five sites. Clean shutdown is NOT yet confirmed for
  this sequence; a post-startup/post-tick audit is being used to investigate.
- Development Editor/Win64 build succeeded after adding native streaming audit
  controls and guarding partial loot restoration against snapshot loss.
- Gate 10 remains NOT ACCEPTED/in progress. No Gate 11 work.
- Delaying the audit/load/save work until after startup and requesting quit from
  a later Slate tick completed full editor shutdown ("Object subsystem
  successfully closed" and "Exiting"). No leak detector suppression. Native
  streaming flags saved as enabled/server mode 2/server stream-out mode 2.
  Current editor-loaded subset contains 66 biome parents and 4594 saved instances;
  this is not a whole-region completeness test.
- Full-authoring-bounds PCG retry: 102 parents, 258 total components, 6019
  persisted instances; zero LogPCG scheduling errors or aborts in that run.
  Native editor loader adapter released after save; full clean shutdown confirmed.
  Initial failures are consistent with partition components lacking loaded local
  partition actors. Native bounded editor loading resolves the reproduced sequence.
- WIP recovery checkpoint 7f5b913 preserves locations/PCG/streaming diagnostics.

## Encounter/difficulty foundation

Compiled native server-only encounter director and authored zone actors; saved seven
contextual profiles/zones with Quiet, Infected Cluster and Supply Cache choices.
Native navigation/perception and accepted infected implementation are reused.
Regional difficulty profiles are project-side derivatives of accepted presets;
Loot/Population controls become active only in the new WNY game mode. Old maps and
accepted presets are unchanged. Population outcome/health/death session snapshots,
weak actor registry and global cap are implemented, not yet runtime validated.

The location retry with all editor cells loaded preserved authored actors by label,
removed only the new OpenWorld template PlayerStart, and saved real GUID strings
in the corrected receipt. Full editor shutdown confirmed again. Navigation showed
735 tiles, but the explicit Build call logged build-lock flags 0x20; navigation
correctness and streaming are NOT claimed. Native partition-aware navigation setup
and gameplay projection tests are next.

## Saved navigation and initial player-path inspection

Native WorldPartitionNavigationDataBuilder completed successfully (exit 0, no
errors). Static partitioned navigation uses a 42 cm agent radius and 192 cm height.
One CrowdManager warning occurred during cell cleanup; runtime projection and AI
path-following remain pending. WNY mobile RV and initial PlayerStart are
non-spatial; regional scenery/containers remain spatial. Prior maps unchanged.

Initial one-player PIE used normal Enhanced Input E/W/S input. The fourth approach
opened the door and physically walked onto the RV interior floor (capsule center
Z 196.27 cm, MOVE_WALKING); visible inspection confirmed the interior view.
Earlier probes aimed incorrectly, obstructed the swing, or stopped outside range;
those are harness failures, not passing entry tests. PIE stopped cleanly and
normal editor close reached LogExit: Exiting.

Native loot lifecycle diagnostics passed duplicate identity rejection, single
transfer/stale transfer rejection, restored quantity/condition/GUID, and no
replenishment after recreation. This is NOT actual WP streaming, multiplayer or
normal-player scavenging acceptance evidence. The visible landscape remains too
uniform and nearby dressing sparse. Runtime world loop, environment refinement,
encounters, multiplayer and performance validation remain unfinished.

## Environment and automation refinement checkpoint

Imported four Electric Dreams ground texture packages (157841645 bytes) with source hashes unchanged. WNY material uses project-side non-virtual-texture derivatives and native world-space texture/noise blending; imported originals are unchanged. Added 129 bounded roadside PCG parents. Saved-state generation has 231 parents total, 576 PCG components and 8572 persisted instances. The guarded final run had zero PCG scheduling errors and clean shutdown. Visual review remains pending; counts do not prove world quality.

Initial generation during parent creation again lacked loaded local partition actors; authoring now saves parents first and generation runs in the next clean fully loaded session. Material scripting encountered native UV/Noise/Clamp input-name mismatches; corrected from engine-reported input names. Roadside authoring used an unsupported Transform constructor keyword; corrected to the actor's native transform and resumed saved work.

Save callbacks could be re-entered by Slate ticks while native save pumped UI messages. This caused nested save assertions (native SaveWorld rejects reentrancy) and premature quit requests. Added busy phase before prepare/save, returning to quit phase only after scoped references unwind. Repeated guarded generation/save completed successfully (2026-10-10 04:22:26 local), clean Exiting at 04:22:29. Earlier failed receipts are retained; no world leak detection suppression or fatal world-leak crash.

Authored five static abandoned trail vehicles using existing Epic off-road template art, simplified project-side body collision, stable finite cargo containers, a partial road obstruction/alternate-loop choice, roadside poles and field fences. Player/visual/nav validation remains pending; these are not additional drivable vehicle systems. Prior art packages are unchanged.

## First actual streamed-state probe

Normal E opened Pine Creek packaged supplies. Existing UI transaction request transferred one entire food stack; stale request returned Item no longer available. A development relocation accelerated actual partition unload: the searched container disappeared from the loaded actor set, then reloaded with identical remaining water GUID/quantity/condition and searched flag. This is single-player streamed-state evidence, not a driven loop or multiplayer pass. Native navigation projection at gas succeeded, and a bounded two-infected encounter activated.

Normal E driver interaction/W throttle/S braking produced actual Chaos travel with no velocity fixture: observed 2181, 3551 and 4117 cm/s. The unguided route drifted off-road and final stop sample was still 525 cm/s, so route/parking acceptance is NOT claimed. Visible terrain remains too repetitive/open. Further player-driven route, world quality, encounter and multiplayer validation required.

New saved visual authoring: 92 grass/shrub verge PCG bounds, project terrain tint and farmhouse/camp office pitched roof pieces. Two separate PlayerStarts now target the accepted RV aisle so the intended loop starts inside the mobile base. Safe initial spawn and visual results are pending; no acceptance claimed. Further generation follows saved-partition workflow. Selective Epic sample groundcover import verified original hashes. Checkpoint before road-clearance review.

## Native terrain streaming and arrival checkpoint (2026-10-10)
Converted the existing 256 Landscape components through the native Landscape subsystem grid-size operation into 64 LandscapeStreamingProxies, preserving the heightfield. Removed 24 project-side PCG parents whose bounds encroached on expanded road clearance, added 18 rural groves and eight parallel highway spline segments. Saved PCG regeneration: 317 parents, 784 instance components, 14,694 instances, pending zero, no PCG errors and clean editor exit. Counts remain authoring evidence, not visual or performance acceptance.

Superseding the temporary static aisle PlayerStarts above: restored clear ground fallback starts. New region-only ARVRegionGameMode places arrivals once into the current tagged mobile RV using accepted validated aisle/floor/base logic, retaining the fallback when unsafe. Reparenting initially reset the inherited pawn default; configuration now captures and restores the existing pawn class before saving. Configuration saved and editor closed cleanly; runtime initial/late/moving join validation remains pending. No accepted game-mode or CharacterMovement infrastructure was replaced.

Saved-state arrival retest initially retained the safe ground start: native game mode was active but the new RV actor tag was not persisted because the automation had not marked that actor modified. Corrected explicit actor Modify before setting tags, saved, clean shutdown and reloaded. Actual PIE now used BP_Gate9_5Survivor at (-159900.69,1600.19,195.20), inside the current RV (root Z17.96). Initial one-player arrival passes; moving/late multiplayer arrival remains pending.

A normal-input guided route (E driver interaction and W/A/D/S, no velocity fixture) drove about 300m to Pine Creek and stopped below 30cm/s. Continued with E exit and physical walking through the real building entrance, E opened supplies, Tab/T transferred canned food quantity1/condition0.846189/GUID FACE847540CC73A90E2F83A859A6D950. Initial T on empty player panel correctly moved nothing. The return walk was interrupted by DOWNED: seven LeftArm WOUND severity2 injuries, consistent with accepted infected attacks; three native encounter infected were present. No completed return/store pass claimed. Subsequent prepared-player combat/avoidance loop needed; do not weaken infected damage just to make automation pass.

Native WorldPartitionHLODsBuilder setup/build completed all 133 groups, exit0, 111.95 seconds, peak physical4486MB/virtual6275MB, no Warning/Error lines and clean Exiting. Distant-world visual/runtime review remains pending.

Prepared-player probe physically exited the side door and picked up food/water. Equipment pivot aim missed small meshes; aiming at visible bounds then picked up crowbar, .45 magazine and M1911 normally. No pickup-code change. Corrected test key name Four (4 is invalid for native input injection); visible M1911 subsequently equipped and reloaded seven rounds. Editor StaticMeshEditorSubsystem collision inspection during PIE returned -1 and is not valid collision evidence.

Armed gas attempt consumed all seven rounds without damaging the selected infected. Read-only visibility traces hit project site geometry around Y3850/Z28 before infected head/torso. Accepted native infected BeginPlay correctly configures visibility mesh queries, disproving the provisional Blueprint-default hypothesis. The gas canopy inherited lower building-centre terrain height while positioned closer to the higher highway; site placement/approach grading needs correction. No damage/collision bypass, forced health or successful combat-loop claim.

## Site grading recovery milestone
Recovery checkpoint a4d60d6 precedes bounded grading. Native FLandscapeEditDataInterface updates only the new region's five pads, including native normals/bounds/collision, with a height-sample guard and one-time saved marker. Five pads changed 2052 vertices; 149 site actors and421 road control points aligned, saved and clean Exiting. One pointer-iteration compile error was corrected; final grading build succeeded. Geometry/nav/PCG/HLOD refresh and visual/runtime validation pending. No accepted infected/gameplay collision changes were made.

Graded-site refresh: native partition navigation saved regenerated chunks and shut down cleanly (one Recast crowd-manager warning during builder teardown). Native HLOD setup/build exit0 and clean Exiting after terrain/PCG refresh. Diagnostic instance counts now separate PCG-owned source instances from other/HLOD instances, avoiding inflated foliage totals. Final build for this instrumentation succeeded. Saved-world normal-control prepared-player/drive/scavenge sequence is being re-run; no acceptance yet.

Graded saved-world normal-input retest: prepared via physical RV door exit and E pickups/Four/R; E/W/A/D/S drove about300m and stopped; physical E exit/W walk into Pine Creek; two ordinary firearm primary attacks cleared visible threats using unobstructed head rays; E/Tab/T scavenged food and W returned to RV. Initial T selected empty container pane (no transfer). Later transfer from an angled approach was correctly rejected because EntryTrace blocked the cargo ray. Physically walking perpendicular to the compartment, normal E/Down/T stored food GUID E8385C844BC206B4C5A1E19763E2A8A0 quantity1 condition0.8461890816688538 unchanged, visible in RV cargo. Verification pass true. One receipt matched the wrong item asset string (CannedFood instead of DA_Food); corrected diagnostic and reacquired scoped values, not gameplay. PIE stopped cleanly. Continued-route/multiplayer/world-quality acceptance remains pending.

## Native server-streaming visibility and world-rule repair
The first separate-process client joined then was disconnected with MissingLevelPackage for a /Memory/WNY streaming cell. Native server streaming was enabled but World Partition visible/invisible transaction requests were off. Enabling Unreal's native client/server visibility acknowledgements retained the connection and passed actual two-process container unload/revisit, identical remaining GUID/quantity/condition/searched state, and exactly one winner for simultaneous requests. No net.SkipMissingLevelDisconnect bypass, engine patch or custom streaming transport. Three native acknowledgement CVars are persisted; unrelated existing engine-config changes remain unstaged.
Epic documents a related 5.8 pending-connection issue [UE-364613](https://issues.unrealengine.com/issue/UE-364613). Our log used legacy replication (iris=0), so that Iris-specific issue is context, not proof of the exact same defect. The native acknowledgement configuration solved this reproduced legacy separate-process failure; emulation recheck pending.
The same test found Loot/Population still marked preparation-only. Saved GameMode/GameState/preset references were correct. Python iteration over Unreal's struct array returned copies; modifying loop elements and assigning the original Unreal array discarded changes. Rebuilding a Python list of modified struct values before set_editor_property persisted both flags false in all three region-only profiles. Original accepted presets are unchanged. Read-only direct property assignment in the repair harness was corrected to native editor-property setters. Repaired assets saved and editor exited cleanly.
New WNY materials now have native instanced-static-mesh usage flags for HLOD, resolving map-check material-usage warnings. Network-emulated shared-authority/difficulty/contention/streaming retest underway; Gate10 remains not accepted.

## Emulated separate-process validation and mobile-base source follow-up
The repaired saved region passed separate-process listen-server validation with 100 ms outgoing latency and 2% outgoing packet loss: normal E opened the shared container, simultaneous requests had exactly one owner, remaining item GUID/quantity/condition and searched state survived actual partition unload/revisit, quiet travel occurred, and the host Custom Loot 1.5 / Population 0.25 settings converged on the client while the client override was rejected. These are scoped network tests with explicit traversal relocation fixtures, not proof of the complete driven route. Curated server/client receipts are in Docs/Gate10Results.
A native UWorldPartitionStreamingSourceComponent is now registered on the tagged mobile base by the region-only game mode. Its configurable bounded radius keeps terrain around the parked RV available while players explore. The source build succeeded. The first extended PIE reconnect probe failed MissingLevelPackage after ordinary reconnect; its failure cleanup also attempted to reacquire a world during travel and was corrected to release keys/unregister/write the receipt even when no region world exists. Native standalone two-process reconnect validation is underway to distinguish editor PIE package naming from gameplay travel. No missing-package validation suppression. The RV source also retained the gas-site cell, so that extended probe's old gas unload expectation failed; earlier actual-unload evidence remains separate and is not rewritten. Gate10 remains IN PROGRESS / NOT ACCEPTED.

Native standalone reconnect also reproduced MissingLevelPackage. The client loaded the region and was disconnected on a streaming-cell visibility report for /Game/Maps/WNY_PrototypeRegion/34LXC9PPNVUCG6JRLZ37Z5YUW. Engine source validates the reported package against server streaming levels/linkers/cooked packages; no bypass is introduced. A targeted native garbage-collection experiment between disconnect and reconnect is running, with failed receipts retained separately. This remains a blocking validation item, not accepted behavior.

## Pending-connection prewarm and native game shutdown follow-up
Native GC did not resolve reconnect. Added a region-only, tunable native streaming-source component on the game mode, using grid loading ranges around the initial origin view. With that prewarm, the client rejoined the current RV at 3749.54 cm/s, relative (89.13,-10.72,176.66), then walked rearward to (-100.50,-18.82,190.98) in MOVE_Walking. The earlier pending-connection diagnosis is consistent with Epic UE-364613, but our legacy replication path is not claimed as its exact Iris repro. This prewarms a bounded neighborhood rather than suppressing package validation; memory/performance cost still needs measurement.
Two probe expectations were incorrect: the server survivor's PlayerState moves to the vehicle during driving, so party size must use the native GameState PlayerArray; the client has no parked-base server source and should unload the gas cell even when the server retains it. Fixed the probe separation, retaining failed receipts. One host exit did not restore possession; new retest uses ordinary service brake plus handbrake rather than handbrake alone, and records exit speed/pawn type.
Three native standalone listen-server exits asserted in World.cpp:4152: visible server-streaming levels were being removed after net mode became standalone. No World Memory Leak/Python reference diagnosis is asserted for these crashes. The harness now disables native source components and controller streaming sources while the net driver is still alive, waits for levels to become invisible, and only then quits. An initial protected StreamingLevels-property read failed; the check was corrected to scoped native LevelStreaming object iteration. Clean shutdown retest pending. No assertion/detection suppression or engine source edit.
