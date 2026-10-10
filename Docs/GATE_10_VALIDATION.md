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
