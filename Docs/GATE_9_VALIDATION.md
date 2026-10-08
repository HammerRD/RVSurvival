# Gate 9 — basic combat and infected foundation

Status: IN PROGRESS. Gate 8.5 baseline: 3256c27. Gate 10 is excluded.

## Framework review

Use existing Actor Components, Primary Data Assets, Gameplay Tags, Enhanced Input,
CharacterMovement, native RPC/property replication and the accepted GAS medical
attributes. No replacement movement, inventory, networking or animation engine.
Magazine rounds are per-instance inventory data, not an abstract reserve pool.
Player damage extends the medical injury transaction and GAS vital attributes;
it must not introduce parallel player health.

Infected use AIController, AI Perception sight/hearing and NavigationSystem native
path following. Behavior Tree/Blackboard are preferred for inspectable behavior;
StateTree is an alternative supported framework, not a second simultaneous brain.
Native timers handle attack/reload completion with authority revalidation. Animation
Montages/slots support presentation independently of authoritative hit timing.
The existing replaceable humanoid profile remains the body-region boundary.

Official framework references reviewed:
- [AI Perception](https://dev.epicgames.com/documentation/unreal-engine/ai-perception-in-unreal-engine?lang=en-US)
- [Behavior Tree overview](https://dev.epicgames.com/documentation/en-us/unreal-engine/behavior-tree-in-unreal-engine---overview)
- [Animation Montages](https://dev.epicgames.com/documentation/en-us/unreal-engine/animation-montage-in-unreal-engine)

## Recovery and scope

Initial working tree contains unrelated Config/DefaultEngine.ini, .vsconfig,
Automation_RVSurvival.slnx and RVSurvival.slnx changes. Exclude them from Gate 9
commits. Preserve prior maps and all 108 Content/RV vendor files against 0b6eff6.
Editor is closed at the accepted saved baseline. Refrigerator collision remains
deferred. No Gate 9 build, runtime or visual acceptance is claimed yet.

## Validation pending

Firearm/magazine transactions; real remappable input paths and visible presentation;
six-region medical damage; native AI perception/navigation/attack/death; separate
process host/client and representative 100 ms/2% loss; meaningful stress; one final
risk-based prior-gate regression; saved asset/vendor audit; build and clean shutdown.

## Foundation evidence (2026-10-08, still in progress)

- Native Development Editor/Win64 builds succeed. Reflected uint32 UI counter,
  tag identifier, shadowed names and required-header errors were corrected.
- `foundation-input.json`: 16/16 focused checks, including normal Enhanced Input
  4/R/LMB/RMB paths, one shot per press, no held repeat, real loaded magazine,
  partial reload ammunition conservation, holster and GUID value uniqueness.
  Fixture item admission is explicitly not a pickup test.
- The initial Python metadata lookup failed; a subsequent GUID check incorrectly
  compared wrapper strings. Corrected to reflected metadata and native GuidLibrary
  value conversion. Failed receipts are retained separately.
- `ai-medical-loop.json`: native sight acquisition and actual firearm trace damage,
  single infected death and post-death attack rejection pass. Chase movement and
  bite consequences FAIL because native navigation produces no path. Not accepted.
- Native navigation system/volume/Recast actor exist, but even explicit native
  editor Build returns an empty path. Geometry/tile diagnostics are underway.
- `vendor-final.json`: all 108 purchased packages match 0b6eff6. Existing maps
  are preserved; new map is Gate9CombatInfectedTest. Editor/PIE teardown is clean
  in these finite runs; no world-leak detection suppression.
- Free installed Epic pistol animations migrated through AssetTools. Project-side
  prototype handgun mesh/sound, item definitions, optional combat character/profile,
  armed Blend Space/Animation Blueprint and new test map are saved. Montage slot,
  dropped visual sizing and pickup collision are being refined before visual signoff.

Recovery checkpoints: 20ef89d framework baseline; 8ce815a explicitly labeled compiled
WIP before content/runtime validation. No multiplayer/visual/stress/regression
acceptance is claimed by these foundation receipts.

The repaired `ai-medical-loop.json` now passes all eight focused checks. Historical
navigation/reach failure receipts remain. Root causes: the copied driving ground
was Movable, and immediate editor Build was refused under AsyncLoadLock (0x20).
Only the new Gate9 map ground is Static/BlockAll; build waits for the native load
lock to clear, then verifies a real two-point path and saves it. No lock removal.
Next, MoveToActor's StopOnOverlap added capsule radii and stopped at ~154 cm,
outside the 130.5 cm attack-entry bound. StopOnOverlap is now false with a smaller
native acceptance radius; attack completion still independently checks 145 cm
and Visibility obstruction. Actual bites create accepted medical injury records,
not a second player HP system. Single infected death and no post-death attacks pass.
