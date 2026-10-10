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

## Required closure evidence

Pending: saved World Partition/Landscape world, 4-6 km useful road route, five authored
locations and usable interiors, PCG dressing, finite contextual loot, difficulty-linked
population, quiet encounter outcomes, actual drive/scavenge/store playthrough,
stream-out/return conservation, separate-process host/client and representative
100 ms/2% loss, performance observations, targeted regressions, final build,
108 vendor hashes and clean editor shutdown.
