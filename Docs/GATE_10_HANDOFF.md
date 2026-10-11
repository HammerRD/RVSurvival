# Gate 10 handoff — Western NY playable region (gameplay prototype)

Prepared 2026-10-10 for the next development agent. Read this file first, then
`ROADMAP.md`, `WORLD_ARCHITECTURE.md`, `ENCOUNTER_SYSTEM.md` and `GATE_10_VALIDATION.md`.

## Status

- **Gate 10 is complete as a gameplay prototype and ready for the owner's acceptance.**
  It is not accepted until the owner (Bobby) says so after his own visual/interior
  walk-through. Gate 11 has not been started or authorized.
- **Scope decision (owner, 2026-10-10):** Gate 10 closes as a *gameplay* prototype. The
  world currently looks barren/flat and the roads look synthetic; that is expected.
  A dedicated **art/"world look" pass is the next step, run as its own step right after
  Gate 10**, so visual changes do not silently invalidate the terrain and driving checks
  below. Any art change that touches terrain, roads or pads must re-run the terrain/edge
  audit and the route drive (see "Re-validation" below).
- Engine: Unreal Engine **5.8.3** (CL 58210709) at `D:\Epic Games\UE_5.8`.
  Project: `D:\GitHub\RVSurvival\RVSurvival\RVSurvival.uproject`. Branch `main`.
- **Repository state:** all Gate 10 work is committed **locally only**. Local `main` is
  about 180 commits ahead of `origin/main` (GitHub `HammerRD/RVSurvival`, which still only
  has the Gate 1 commit). Nothing has been pushed. If another tool/agent needs the code,
  the owner must push or otherwise share the repository first.
- Intentionally uncommitted, owner's local files — never commit or print them:
  `Config/DefaultEngine.ini` local hunks, `.vsconfig`, `*.slnx`.

## What Gate 10 delivered

Map: **`/Game/Maps/WNY_PrototypeRegion`** (`Content/Maps/WNY_PrototypeRegion.umap` plus
World Partition external actors under `Content/__ExternalActors__/Maps/WNY_PrototypeRegion`).

- **World:** native World Partition, 4032 m square Landscape (16x16 components, 4 m vertex
  spacing, 65 streaming proxies, one edit layer named "Layer"), ~6.01 km of native spline
  roads (72 `ARVRegionRoad` actors), five authored sites — Pine Creek Fuel, Erie Road Service
  (garage), Hawthorne Farm, Maple Run Campground, Rowland Crossroads — with seven enterable
  prototype building shells, parking slabs, abandoned vehicles with finite cargo, editor-baked
  partitioned PCG dressing (14,695 instances / 784 components), native HLOD (132 actors) and
  partitioned navigation.
- **Gameplay systems (all new code under `Source/RVSurvival/*/World/`; accepted Gate 1–9.5
  systems were not modified):**
  - `ARVScavengeContainer` + `URVRegionStateSubsystem`: finite, server-authoritative loot
    with stable GUIDs; searched/taken state survives World Partition unload/revisit.
  - `URVEncounterDirector` (WorldSubsystem) + `ARVRegionEncounterZone`: authority-only
    Quiet / Infected Cluster / Supply Cache outcomes from `URVEncounterProfile` data assets,
    global non-quiet cooldown, reduced repeat weight, stable per-session outcomes, global
    active-infected cap (12, hard max 16), safe hidden spawns on navmesh, value-only
    snapshots (position, vitality, leg injury, death) when a zone suspends.
  - `ARVRegionGameMode`: region-only game mode, validated arrival into the mobile RV,
    regional Loot/Population difficulty, native World Partition streaming source on the RV
    (connection prewarm) and orderly source release on shutdown.
  - `ARVRegionRoad`: spline-mesh road with asphalt and centre paint.
  - `URVWorldContentLibrary`: editor/development bridge — landscape creation, partitioning,
    site grading, pavement-edge blend, terrain audits, loot and encounter validators.
- **Networking:** separate-process listen server with 100 ms latency / 2% loss passed shared
  container contention (exactly one owner), loot conservation across unload, quiet travel,
  moving-RV late join/reconnect and orderly shutdown. Native WP client visibility
  acknowledgements are enabled (`Config/DefaultEngine.ini`, committed in 43816a9) to avoid
  `MissingLevelPackage` disconnects.

## Terrain history (important for anyone editing terrain)

1. Original grading (V1/V2, commits ca3c787/3cac7c6) wrote heights with
   `FLandscapeEditDataInterface` **without selecting an edit layer**, so only the final merged
   heightmap changed; the next layer merge restored the original hills. Tags claimed grading
   had happened. Lesson: **always write through the edit layer**
   (`FScopedSetLandscapeEditingLayer` on the "Layer" GUID), then
   `RequestLayersContentUpdateForceAll` + `ForceUpdateLayersContent`, and **audit from disk
   before trusting any tag or receipt**.
2. **V3** (5b1e135): sites graded through the edit layer, each pad widened by one 400 cm
   quad, garage extension included, four rural loops re-seated. Marker `WNYGradedSitesV3`.
3. **Paved edges** (f9bdbaf): terrain blended to every road spline mesh and the five
   parking slabs so there is no curb anywhere; Rural loop 4-5 lowered to meet the divided
   highway. Marker `WNYPavedEdgesV1`. Strict audit after reopening from disk:
   0 failures; road edge steps −4.9..+8.2 cm (mean 3.8), slab edges 2.8..7.1 cm, terrain
   never more than 1.25 cm above pavement (baseline was 18 cm average, 62 cm worst).

Function: `URVWorldContentLibrary::BlendRegionTerrainToPavement` — paved vertices 6 cm
under pavement *simple collision* (what vehicles drive on), first ring at the traced edge
−3 cm, 3-quad smooth falloff, then a 16-iteration correction pass that models the Chaos
heightfield triangle split (diagonal from cell origin to far corner).

## Validation evidence (latest)

| Area | Result | Evidence |
|---|---|---|
| Terrain/pads/roads | Strict audit pass from disk, 0 failures | `Docs/Gate10Results/saved-terrain-full-audit.json` |
| Pavement edges | 3,055 measured inside/outside pairs pass (79 unmeasurable at junction overlaps) | same file, `edge_steps` |
| Full route drive | 4.465 km normal-input drive completed, no stalls; garage stop 0.2 m from target, hold-E exit/re-entry pass; max roll 10.9°, pitch 11.4°, coolant 66 °C, frame median/p95 16.7 ms | `Docs/Gate10Results/regraded-route-drive.json` |
| Derived data | PCG pending 0; HLOD Success 0/0 (42 rebuilt); navigation Success (known CrowdManager warning) | `pcg-paved-full-load.json`, CHANGELOG |
| Loot/encounters/network | Finite loot, contention, unload/revisit conservation, quiet travel, late join, shutdown | `GATE_10_VALIDATION.md` |
| Encounter bookkeeping | 12/12 pass | `Docs/Gate10Results/closure-checks.json` |
| Prior gates integrity | Since Gate 9.5 acceptance (81b65c9): only additions under `Content/`; no prior map or vendor/imported asset modified; all source changes are new `World/` files plus Build.cs | `git diff --name-status 81b65c9 HEAD` |

Each terrain change was saved only after an in-session strict pre-save audit passed;
failed attempts were never saved and their evidence is kept in `Saved/Gate10Validation`.

## Closure items (done)

- Encounter bookkeeping: native validator `ValidateEncounterBookkeeping` 12/12 pass —
  cooldown, quiet fallback, stable outcomes, killed/living/externally-destroyed member
  snapshots, supply cache restored without the taken item, transient records cleaned up.
- Prewarm/performance: player ready 1.28 s after PIE start with the RV area streamed in;
  uncapped development-PIE frames median 8.34 ms, p95 8.71 ms, p99 9.01 ms; peak editor
  working set 4.4 GB. Evidence: `Docs/Gate10Results/closure-checks.json`.
- Final editor build succeeded; every scripted editor and builder run exited cleanly.
- Still the owner's: visual/interior walk-through of all five sites and the acceptance decision.

## Known issues and limits (not blockers for a gameplay prototype)

- Visual quality: barren, flat, synthetic road look — deferred to the art pass.
- Road network is a single-mesh strip (no shoulders/edge lines). 79 edge pairs sit at road
  junction overlaps and are not measured by the edge audit.
- The automated route follower cuts sharp corners; the route has a deliberate
  off-pavement turnaround at the garage. These are harness behaviours, not vehicle rules.
- The driver seat is entered from outside the cab (hold E at the driver door); it is not
  reachable from the interior aisle.
- Not implemented (by design): weather/time simulation, hordes/migration, human AI,
  campaign saving, cross-region travel, final Encounter Director.
- Earlier HLOD/navigation hangs were caused by Incredibuild (XGE) shader distribution with
  an unactivated license. The `XGEController` plugin is now **disabled** in
  `RVSurvival.uproject` (da76ef6); shaders compile locally.

## Working environment notes

- Build: `Engine\Build\BatchFiles\Build.bat RVSurvivalEditor Win64 Development
  -Project=<uproject> -WaitMutex`. Add `-NoHotReloadFromIDE` only when an editor without
  the project loaded (e.g. the Project Browser) has Live Coding running. A build cannot
  replace `UnrealEditor-RVSurvival.dll` while the owner's editor has the project open.
- Scripted editor runs: `UnrealEditor.exe <uproject> -ExecCmds="py <script>" -unattended
  -nosplash -NoLiveCoding -abslog=<log>`; scripts use a Slate post-tick state machine,
  release Python UObject references, and call `quit_editor` (unattended quit does not save).
  Do not use `-ExecutePythonScript` for interactive runs.
- Builders: `UnrealEditor-Cmd.exe <uproject> /Game/Maps/WNY_PrototypeRegion
  -run=WorldPartitionBuilderCommandlet -AllowCommandletRendering
  -builder=WorldPartitionHLODsBuilder -SetupHLODs -BuildHLODs` (or
  `-builder=WorldPartitionNavigationDataBuilder`) `-SCCProvider=None -unattended`.
- Editor automation hazards: release Python UObject refs before map changes; never reload
  a map in a cleanup callback; do not duplicate worlds; guard save callbacks against Slate
  re-entrancy; Unreal struct arrays iterate as copies; never suppress assertions or leak
  detection; on a crash read the logs.
- Process rules used throughout: never roll back to a4d60d6; fix forward; keep failed
  evidence; label harness failures as harness failures; never change accepted gameplay,
  vehicle physics or mechanical rules to make a test pass; never edit vendor assets or
  prior gate maps.

## Key tools (`Tools/Validation/Gate10/`)

| Script | Purpose |
|---|---|
| `audit_saved_terrain.py` + `terrain_audit_common.py` | Read-only full terrain, pad, road and pavement-edge audit (strict pass/fail) |
| `blend_pavement_edges.py` | Gated pavement-edge blend (saves only if the pre-save audit passes; marker already set, so a rerun is a no-op) |
| `grade_sites_v3.py` | Historical V3 site grading (marker set; no-op now) |
| `launch_regraded_route.py` + `regraded_route_drive.py` | One-player PIE, no save, normal-input full route with garage exit/re-entry |
| `regenerate_loaded_biome.py` | Regenerate and save PCG with all cells loaded |

## Re-validation after any art/terrain change

1. `audit_saved_terrain.py` must pass (0 failures) after reopening from disk.
2. Regenerate PCG, rebuild HLOD and navigation; confirm Success and clean exit.
3. Re-run `launch_regraded_route.py`; the route must complete with the garage stop and
   hold-E exit/re-entry passing.

## Gate 11

Not started and not authorized. The owner will brief the next gate after the art pass.

## Appendix — Gate 10 commits (local `main`, newest first)

See `git log --oneline 81b65c9..HEAD`. Milestones: d03ee50 framework review; ae5a573 6 km
road network; a3d336e encounter foundation; 654ab93 navigation and physical RV entry;
43816a9 native WP visibility acknowledgements; ec330ce emulated moving-base rejoin and
orderly shutdown; 3cac7c6 garage approach; 6e177fe garage height diagnosis; 45544a5 full
terrain audit; 5b1e135 V3 edit-layer grading; 194b1c0 HLOD/navigation refresh; da76ef6
XGEController disabled; edeadd6/faec538 route drive diagnosis; f9bdbaf paved-edge blend;
4ebea5d full route drive; later commits record closure items and this handoff.

## Appendix — Gate 10 changelog

The complete chronological Gate 10 changelog is the section of `Docs/CHANGELOG.md` from
"Gate 10 foundation recovery checkpoint" to the end of the file, and the detailed evidence
ledger is `Docs/GATE_10_VALIDATION.md`. A verbatim copy is appended below.

```text
### Gate 10 foundation recovery checkpoint (in progress)

Saved a 6.01 km spline road network, bounded native partitioned PCG dressing,
five authored location shells and ten finite contextual storage points in the
new WNY map. Added native streaming inspection and a ledger safeguard so failed
capacity restoration cannot overwrite a complete loot snapshot. Editor build
passes. PCG scheduling aborts, editor shutdown behavior, actual traversal,
multiplayer streaming, encounters and visual validation remain unresolved or
untested; this is not Gate 10 acceptance. Prior accepted maps/vendor files are
not edited.

## 2026-10-10 — Gate 10 navigation and initial PIE checkpoint

Saved native partitioned navigation and non-spatial WNY mobile RV/start. Native navigation builder exited successfully with no errors; runtime path-following remains pending. Normal E/W/S player input opened the side door and physically entered the RV; visible interior, walking movement and reference-frame registration confirmed. Stopped PIE and closed editor cleanly. Finite-loot lifecycle diagnostics passed targeted identity/transfer/restore/depletion checks, but actual streaming/multiplayer world-loop acceptance remains pending. Landscape/nearby dressing requires further visual refinement. Gate 10 remains in progress; no Gate 11.

## 2026-10-10 — Gate 10 environment refinement checkpoint

Saved project-side woodland terrain material, 129 additional bounded roadside PCG parents, five static abandoned trail vehicles with finite cargo, roadside obstruction/route choice, poles and fences. Selective Epic sample texture import preserves source hashes. Final saved-state PCG run: 231 parents, 8572 instances, zero scheduling errors and clean shutdown. Fixed Slate callback reentrancy in author/save automation; native save now completes before quit phase. Scene/player-path/nav/multiplayer validation remains pending. Gate 10 not accepted; no Gate 11.

### Gate 10 streaming/arrival recovery checkpoint — in progress
- Saved native 64-proxy landscape conversion, road-clearance PCG bounds review, rural groves and parallel highway geometry.
- Saved native PCG regeneration (14,694 instances) with no scheduling errors and clean shutdown.
- Added region-only validated mobile-base arrival with safe ground fallback; preserved inherited survivor settings during Blueprint reparenting. Runtime join and multiplayer validation still pending.
- Gate 10 remains NOT ACCEPTED; no Gate 11 work.

### Gate 10 site grading — saved authoring milestone, validation pending
- Diagnosed low gas canopy from inconsistent terrain references; visibility rays correctly blocked firearm shots.
- Added bounded native Landscape grading for five prototype sites and aligned site geometry/road approaches.
- Recorded actual door/pickup/firearm preparation control paths; corrected harness pivot aim and numeric key naming.
- Recovery a4d60d6 preserves pre-grading world. Gate10 remains in progress, NOT ACCEPTED.

Graded-site refresh: native partition navigation saved regenerated chunks and shut down cleanly (one Recast crowd-manager warning during builder teardown). Native HLOD setup/build exit0 and clean Exiting after terrain/PCG refresh. Diagnostic instance counts now separate PCG-owned source instances from other/HLOD instances, avoiding inflated foliage totals. Final build for this instrumentation succeeded. Saved-world normal-control prepared-player/drive/scavenge sequence is being re-run; no acceptance yet.

Gate10 saved-region normal-control drive/scavenge/return-store retest passed for preserved food GUID/condition. Native canopy/site grading restored unobstructed accepted firearm traces; no combat rules changed. Separate-process join exposed MissingLevelPackage with server streaming; investigating native visibility acknowledgements, no validation bypass. Gate10 remains in progress/not accepted.

Gate10: persist native WP visibility acknowledgements after reproduced two-process MissingLevelPackage; preserve unrelated config edits. Repair region-only Loot/Population future flags by rebuilding modified struct-value lists; save native HLOD material usage flags. No engine validation bypass. Network recheck pending.

## Emulated separate-process validation and mobile-base source follow-up
The repaired saved region passed separate-process listen-server validation with 100 ms outgoing latency and 2% outgoing packet loss: normal E opened the shared container, simultaneous requests had exactly one owner, remaining item GUID/quantity/condition and searched state survived actual partition unload/revisit, quiet travel occurred, and the host Custom Loot 1.5 / Population 0.25 settings converged on the client while the client override was rejected. These are scoped network tests with explicit traversal relocation fixtures, not proof of the complete driven route. Curated server/client receipts are in Docs/Gate10Results.
A native UWorldPartitionStreamingSourceComponent is now registered on the tagged mobile base by the region-only game mode. Its configurable bounded radius keeps terrain around the parked RV available while players explore. The source build succeeded. The first extended PIE reconnect probe failed MissingLevelPackage after ordinary reconnect; its failure cleanup also attempted to reacquire a world during travel and was corrected to release keys/unregister/write the receipt even when no region world exists. Native standalone two-process reconnect validation is underway to distinguish editor PIE package naming from gameplay travel. No missing-package validation suppression. The RV source also retained the gas-site cell, so that extended probe's old gas unload expectation failed; earlier actual-unload evidence remains separate and is not rewritten. Gate10 remains IN PROGRESS / NOT ACCEPTED.

## Pending-connection prewarm and native game shutdown follow-up
Native GC did not resolve reconnect. Added a region-only, tunable native streaming-source component on the game mode, using grid loading ranges around the initial origin view. With that prewarm, the client rejoined the current RV at 3749.54 cm/s, relative (89.13,-10.72,176.66), then walked rearward to (-100.50,-18.82,190.98) in MOVE_Walking. The earlier pending-connection diagnosis is consistent with Epic UE-364613, but our legacy replication path is not claimed as its exact Iris repro. This prewarms a bounded neighborhood rather than suppressing package validation; memory/performance cost still needs measurement.
Two probe expectations were incorrect: the server survivor's PlayerState moves to the vehicle during driving, so party size must use the native GameState PlayerArray; the client has no parked-base server source and should unload the gas cell even when the server retains it. Fixed the probe separation, retaining failed receipts. One host exit did not restore possession; new retest uses ordinary service brake plus handbrake rather than handbrake alone, and records exit speed/pawn type.
Three native standalone listen-server exits asserted in World.cpp:4152: visible server-streaming levels were being removed after net mode became standalone. No World Memory Leak/Python reference diagnosis is asserted for these crashes. The harness now disables native source components and controller streaming sources while the net driver is still alive, waits for levels to become invisible, and only then quits. An initial protected StreamingLevels-property read failed; the check was corrected to scoped native LevelStreaming object iteration. Clean shutdown retest pending. No assertion/detection suppression or engine source edit.

## Native reconnect and orderly shutdown retest passed
The road-guided, scoped late-rejoin test passed in separate native game processes with 100 ms / 2% loss: native RV arrival, current moving-RV late join, independent client rearward walking, authoritative two-player party, host stop/normal E exit, and unchanged finite shared loot. Both processes disabled their native streaming sources after testing, waited for streaming levels to become invisible with the net driver still alive, then quit cleanly. Both logs contain clean Exiting and cleanup receipts report zero visible levels.
Earlier blind-throttle probes drifted off-road; one exit sample still had 997.18 cm/s speed and was correctly rejected. Another off-road stop did not exit; retained ground rays hit sloping Landscape and health was active. Its exact guard/input cause was not established, so no seat-code diagnosis is asserted. Medical-state diagnostics ruled out the provisional downed-driver explanation. Normal W/A/D/S road guidance, measured stop and handbrake restored the expected E exit without changing vehicle physics or accepted seat logic. All failing receipts remain separate. The native prewarm workaround remains region-only/tunable and its loaded-neighborhood performance cost is still to be assessed.
This closes the targeted rejoin/shutdown failure, not Gate10 acceptance. Required broader location visual playthrough, continued driven route, encounter/cache bookkeeping, representative regressions and final performance review remain. No Gate11.

Saved project-side facade refinement: fourteen real window apertures across seven enterable shells, replacing full-height painted window backing with wall bands/stiles and translucent project-side glass. Added 98 wall/frame parts, preserved door clearances, terrain, container IDs and vendor assets. Native HLOD/navigation refresh and visual collision verification remain pending.

## Garage front-approach saved refinement
A layout review found the service garage front parking area outside the original graded core. Extended only that site's saved native Landscape pad, with a 90m blended falloff, and rerouted its spline driveway around the building to the front parking area. Native build succeeded (31.67s). Saved 4,067 changed Landscape vertices; aligned the abandoned garage vehicle, simplified body collision and finite cargo point together by 1,147.71cm to the new ground without changing container identity. Saved PCG regeneration completed with pending zero, 14,694 source instances / 784 components and clean editor Exiting. HLOD/navigation refresh and actual continued-route driving remain pending. This is authoring evidence, not Gate10 acceptance.
Garage derived-data refresh saved: native HLOD and navigation exit0; continued route validation pending.
Gate10 remains in progress. User-only Windows Firewall prompt interrupted final continued-route review; checkpoint 3cac7c6 preserves saved garage terrain/props/PCG/HLOD/navigation. No Gate11.
Gate10 resume: retained cargo-approach assertion failure; prepared return-walk/perpendicular-access test correction (runtime retest pending). Windows control helper remains busy after reset; no acceptance claimed.
Gate10 audit checkpoint d03bef8 preserved completed evidence. Same-session food storage visually/authoritatively passed; longer route timed out after2.42km at garage terrain/driveway mismatch. Retained failure; targeted Landscape diagnosis next, no Gate11.
Gate10 localized saved-height audit confirms garage terrain below road/parking despite grading markers. Grading functional result invalidated; exact height-edit persistence cause pending. Diagnostic build succeeded33.96s; no acceptance or Gate11.

## Site grading V3 through the Landscape edit layer
Root cause of the invalidated grading: the Landscape has one edit layer ("Layer") and no editing layer was selected, so GradeRegionSitePads wrote only the final merged heightmap (FLandscapeEditDataInterface with an invalid layer GUID); the next layer merge regenerated it from the untouched layer while V1/V2 tags were still saved. Full read-only audit (45544a5) showed saved heightmap, edit layer and collision equal to the original ungraded formula at all 6,242 samples.
V3 grades the five sites (each widened by one 400cm Landscape quad so pad edges stay flat) and the garage extension in one pass inside FScopedSetLandscapeEditingLayer on "Layer", then forces the layer merge; target formula unchanged. Rural loops 1-30, 2-0, 2-35 and 3-0 re-seated at graded height +12cm. In-session pre-save audit passed (0 failures) before saving; two earlier unsaved attempts retained (edge-band and road failures).
Reopened from disk: strict audit pass, 0 failures. Pads vs target: Pine Creek, Erie, Rowland, garage 0cm; Hawthorne -0.19cm; Maple Run +0.29cm; heightmap, edit layer and collision agree. All 407 road control points with a road hit are 16.8-26.9cm above terrain (mean 18.15; previously up to +1176cm). PCG regenerated and saved: pending 0, 14,695 instances / 784 components, clean Exiting.
HLOD builder setup completed but stalled at [1/132] for >10 minutes with no CPU/log progress; stopped. HLOD and navigation refresh pending; no driving, PIE or Gate10 acceptance claimed. No Gate11.
Derived-data refresh after V3 grading: native WorldPartitionNavigationDataBuilder succeeded (result 0, 0 errors, the known CrowdManager warning) and replaced 5 navigation data packages; its process then hung in shutdown and was stopped after saving. HLOD builds stalled at [1/132] because shader compilation was routed to the XGE (Incredibuild) controller while its license reports "not activated": read-only stack dumps show the game thread in FShaderCompilingManager::FinishAllCompilation from UHLODBuilderMeshSimplify::Build, and the XGE dispatch thread blocked in ConnectNamedPipe with no worker process; the navigation shutdown hang is the same XGEController wait. Re-ran HLOD with -noxgeshadercompile (local ShaderCompileWorker): 132/132 actors, 16 rebuilt over changed terrain and 116 unchanged, Success 0 errors/0 warnings, clean Exiting. Runtime driving and visual review remain pending; no Gate10 acceptance claimed.
Disabled the XGEController plugin for this project (Incredibuild license never activated; XGE shader dispatch hung HLOD builds and shutdowns). Verified: editor build succeeded on Unreal Build Accelerator; unattended editor run reports "No distributed shader compiler controller found / Using 12 local workers" and exits cleanly.
Regraded-world normal-input route drive (one-player PIE, no map save, no transform/velocity fixtures): physical side-door E exit, walk around the cab, hold-E driver entry, W/A/D/S/SpaceBar. Erie garage now passes: drove the driveway onto the parking slab (RV Z37 over slab Z19, 0.4m from the parking target), stopped, normal hold-E exit and re-entry both succeeded; garage leg max |roll| 5.5deg / |pitch| 5.7deg, coolant 52C. Continued route then stalled after 1.827km at (-72694,9104,-680cm), 7.2m beside the Rural loop 0 centreline on Landscape (Z-699, road surface about -646) at 8cm/s, 73.7C: the route follower entered the (-80000,0) hairpin at up to 17.6m/s and left the road, then could not recover on the side slope. Classified as a route-follower (harness) failure, not a terrain/road height mismatch; no gameplay, vehicle or check changes. Hawthorne/Maple/Rowland not yet reached. Five earlier attempts were harness failures before or at entry (aisle seat not reachable, hold-E, property names, re-entry walk). Not accepted.
Route drive attempt 8 (route-follower corner lookahead only): garage stop, hold-E exit and re-entry passed again (1.1m from parking target). After re-entry, the turnaround south of the garage stalled at (-59936,-13069,18cm) after 1.222km: the RV was on Landscape (Z0) and drove into the south edge of the garage parking slab (top Z19, about x-61600..-58400, y-12700..-9950) at about 6.9m/s at a shallow angle, dropped to 2cm/s and could not climb the 19cm step; coolant rose to 69C while W was held. Attempt 7 crossed the same edge at a steeper angle. Finding: graded pads now sit at Z0 while parking slabs/roads sit 18-19cm above, leaving curb-like edges wherever a vehicle leaves the paved surface. Not accepted; no gameplay, vehicle or check change.
Pavement edge blend (WNYPavedEdgesV1, through the "Layer" edit layer; pad/road targets unchanged): terrain under the 354 road spline meshes and 5 parking slabs sits 6cm under the pavement simple collision, the first ring meets the traced pavement edge 3cm low, then a 3-quad smooth blend; a second smoothing pass (90,866 samples in 9,982 quads, Chaos collision triangulation) corrects the interpolated surface. Rural loop 4-5 now drops to highway height (new spline point (128556,2600,12)) instead of ending 20cm above the divided highway. New strict audit pairs points 50cm inside/outside every road edge every 5m and every slab edge every 2m (3,134 pairs, 3,055 measured; 79 unmatched where the inside point is not on that pavement, e.g. junction overlaps): baseline road steps mean 18cm/max 62cm, terrain up to 19cm above road, slabs 19cm. Six unsaved attempts kept as evidence; attempt 7 passed pre-save and was saved. Reopened from disk: pass, 0 failures; road edge steps -4.9..+8.2cm (mean 3.8), slab 2.8..7.1cm, terrain at most 1.25cm above pavement, heightmap/layer/collision agree within 3cm, pads beyond the 24m blend still on target. PCG regenerated (pending 0, 14,695/784); HLOD 132 actors (42 rebuilt) Success 0/0 and navigation Success 0 errors (known CrowdManager warning), both clean Exiting with local shader workers.
Full regraded route drive after the pavement blend (same normal-input harness and route follower, one-player PIE, no saves): completed 4.465km in 332s and stopped at the route end (169850,36) on the highway. Garage: stopped 0.2m from the parking target on the slab, hold-E exit and re-entry passed. Closest approach: Pine Creek 47m (passes on the highway), Erie service 12m, Hawthorne 10m, Maple Run 11m, Rowland 50m (passes on the junction). No stall; max |roll| 10.9deg, max |pitch| 11.4deg, peak coolant 66C, top speed 19.0m/s, sampled frame median/p95 16.7ms. 32 one-second samples after the start were on Landscape where the follower cut sharp corners or used the deliberate garage turnaround; all were crossed at 5-14m/s without loss of speed. PIE stopped and the editor exited cleanly. Visual review remains; this is driving evidence, not Gate10 acceptance.

## 2026-10-10 — Gate 10 closure: gameplay prototype ready for owner acceptance
- Encounter bookkeeping validator 12/12 pass (cooldown, quiet fallback, stable outcomes, dead/suspended/destroyed members, supply-cache conservation).
- Prewarm: player ready 1.28 s after PIE start with the RV area streamed; uncapped PIE frames median 8.34 ms / p95 8.71 ms; clean exit.
- No prior gate code, map or vendor asset changed since 81b65c9. Art pass is the next step; Gate 11 not started.
- Handoff for the next agent: `Docs/GATE_10_HANDOFF.md`.
```
