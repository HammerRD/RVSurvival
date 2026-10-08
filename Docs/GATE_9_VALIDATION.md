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

## Presentation and authority refinement (2026-10-08)

Development Editor/Win64 rebuild succeeded using the native Unreal Build Accelerator
local executor (`owned-debug-build.log`). The optional development invalid-intent
probes use owned, weak next-tick RPC requests; they are disabled in Shipping/Test.
The initial conditional-compilation unreachable-return error was corrected.

`foundation-input.json` now records 18/18 checks. Holstering preserves the real
loaded magazine; re-equipping retains rounds. Remappable U explicitly unloads it
before transfer/drop. R remains available to the accepted bed stand-up action;
reload does not produce a spurious wake request for an awake character. Weapon
readiness is suppressed during seating, rest, ladder and medical treatment.

Player and infected attacks use Unreal PointDamage events. Survivor damage feeds
existing injury records and GAS vitality. The new presentation profile can supply
an absolute-scale head query independently of owner head hiding; multiplayer
head/body hit validation remains pending. Existing map pickup visual-scale overrides
remain intact: the new WorldVisualScale application is limited to combat items.

The isolated updated `ai-medical-loop.json` passes 8/8 after native damage routing:
sight, NavMesh chase, contaminated bleeding wound, actual firearm trace kill,
single death and no further attacks. A combined fixture failed after preceding
combat activity changed AI goals; its receipt is retained. The isolated fixture
pauses native brain/path following only during placement, then resumes native
perception and behavior. These are targeted functional results, not final stress
or multiplayer acceptance.

Visual inspection found the original handgun grip facing backward. A project-side
180-degree grip correction and Epic pistol aim-offset asset have been saved.
Reinspection of the corrected rendered pose is pending; earlier screenshots are
failure evidence, not signoff. Separate-process baseline validation is underway.

Separate-process baseline first run: native firing/reload/ownership rejection,
infected head and client torso deaths, logical player wounds/downing and downed
fire rejection pass on both peers. Treatment stabilization/revive failed because
fixture dressings were requested every five seconds, shorter than the accepted
8-second action duration. The test now waits ten seconds between dressings and
14 seconds for the 12-second revive. Original server/client receipts are retained
as `process-baseline-treatment-timing-*.json`. No medical rules were weakened.
