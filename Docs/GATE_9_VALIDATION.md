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

## Focused multiplayer, inventory and stress evidence

`combat_baseline_server.json` and `combat_baseline_client.json` pass 24/24 and
14/14 respectively in distinct processes. `combat-baseline-comparison.json` checks
exact GUID/definition/quantity/condition/round/revision/loaded relationship agreement.
Fixture admissions account for ten server checks; they are not ten gameplay tests.
Native fire/reload, concurrent independent shots, stale/foreign intent rejection,
subsequent valid fire, infected head/torso deaths, player head/torso wounds/downing,
downed fire rejection, three sequential dressings and revive retaining injuries pass.

`combat-stress.json`: 100 actual normal semiautomatic input presses, seven completed
reloads over 60.1 seconds. Exactly 100 shots, 120 initial rounds reduced to 20,
all nine item GUIDs retained, conditions/quantities/bounds valid, one loaded magazine,
and final unload without loss. Six meaningful invariant checks, not one artificial
assertion for every shot.

`combat-pickup-storage.json` passes 8/8 using normal held E for world pickup and
storage opening, followed by accepted inventory UI request methods for drop/transfer.
A six-round magazine preserves identity, condition and rounds through drop, repick,
container transfer and return. Container aiming required settling the capsule-relative
eye origin after changing yaw. Failed fixture receipts remain. The inaccessible Python
deferred-spawn helper was replaced by reacquiring existing map actors; no source
or saved-map reconstruction was needed.

`infected-hearing-cancel.json` passes 5/5: initial player outside sight cone, actual
gunshot in native Hearing, investigate/chase, attack windup and victim range escape
with no late wound. This test complements, rather than substitutes for, sight/bite tests.

Manual OS 4/R/LMB actions equip, complete reload and decrement one round. Rendered
pose is NOT yet approved: inspection found Epic AO_Pistol axes authored -1..1,
but degree-valued pitch fed Y and saturated upward at a small angle. A presentation
conversion to NormalizedAimPitch is being compiled; no CharacterMovement or physics
change. Failure screenshots are retained. Network emulation, remaining body-region
and visual validation, moving-RV and final representative regressions remain pending.

## Verified presentation and full body-region multiplayer follow-up

The normalized Epic aim input now uses degrees/90, matching its authored -1..1
axis. The Gate9-only character profile uses OwnerCameraOffset (0,0,4) cm rather
than the earlier profile's 20 cm forward offset, giving the full-body pistol pose
clearance from the camera. Prior profiles/maps are unchanged. Grip translation
(-8,0,8) cm with yaw 180 aligns the authored mesh's grip pivot to the configurable
Tool hand anchor. OS 4/R/LMB equip/reload/fire and a rendered infected death were
inspected. First-person aim/ready, reload and observation-camera body/grip are
usable at prototype quality. Remote screenshots on both separate processes show
a complete humanoid head/body and visible forward-facing handgun. Owner head
hiding in an owner observation view is intentional, not remote head loss.

`combat_regions_server.json` and `combat_regions_client.json` pass 50/50 and
28/28 checks. Twelve server-only debug patient resets and ten inventory admissions
are setup validation, not additional combat accomplishments. Actual normal input
shots hit Head/Torso/LeftArm/RightArm/LeftLeg/RightLeg from host and client, and
replicate the matching medical regions. Concurrent normal held-E claims admit the
six-round world magazine exactly once. Cross-process inventories agree exactly.
Default gameplay trace overlays are now development-only and disabled unless
rv.Combat.DebugTrace is explicitly enabled; native muzzle/impact effects remain.
Network-emulation and final RV regression closure are still pending.

## Stable combat and RV multiplayer milestone — 2026-10-08

Separate-process `combat_emulated` passed all recorded checks (50 server, 28
client), including actual shots to all six medical regions from both roles,
concurrent held-E pickup, exact magazine inventory convergence, and downed /
treatment / revive. Outgoing emulation was 100 ms with 2% loss per endpoint.
Reload contention and disconnect receipts pass 8 server / 7 client checks:
a spare transferred during a pending reload aborts completion without ammo loss;
shared-magazine contention admits one owner; disconnect leaves shared state intact.

`moving_armed_host_emulated` and reciprocal `moving_armed_client` have no failed
checks. Native 4/R/LMB equipped, loaded and fired on the standing passenger;
walking/standing at low, road and approximately 60 mph fixture speeds, turning,
braking and twenty stopped V round trips remained functional. Speed phases use
server physics velocity fixtures, not a claim of human throttle acceleration.
The recorded passenger correction count/max were zero in these runs.

Camera recoil now uses native EngineCameras UDefaultCameraShakeBase with
UWaveOscillatorCameraShakePattern: 0.7 degree pitch, randomized 0.12 degree yaw,
0.18 second recovery, tunable item metadata. Native rotation multiplier must be
explicitly enabled (its constructor defaults it to zero). The retained failed
receipt records that discovery. The rerun measured excursion and return while
ControlRotation remained unchanged. Gameplay ray direction is not camera-shake
state. Pickup/drop/repick/storage, condition/GUID continuity and empty firing
checks pass in the 17-check single-player receipt.

Remaining before acceptance: targeted infected limb / obstacle / loss behavior,
representative storage-survival-resource regressions, final saved-state/build /
vendor audit, editor preference restoration, and documentation closure.

## Final runtime validation closure (supersedes earlier pending notes)

All runtime acceptance areas now pass. Final saved-content/build/checkpoint closure
is being completed. Receipts contain individual setup, diagnostic and gameplay
checks; their counts must not be advertised as a single large gameplay assertion count.

| Area | Actual evidence |
|---|---|
| Complete firearm loop | Normal OS 4/R/LMB/RMB visual session; native input foundation; 17 pickup/storage/recoil checks; real gun and magazine drop/repick, condition/GUID/revision continuity, partial/empty magazines, holster/re-equip/unload. |
| Magazine guards and controls | `magazine-contract.json`: wrong-caliber owned reload, duplicate GUID, non-stackable combat records, negative/over-capacity rounds, conserved inventory; native F10 opens real UMG Controls rows for all five combat actions and close handler restores look/movement. |
| Host/client medical damage | `combat_regions` and `combat_emulated`: both roles hit all six logical regions with actual server traces; contaminated/bleeding wounds, downing, downed-fire rejection, sequential dressings and revive retaining injuries. Exact magazine snapshot convergence in distinct processes. |
| Infected end-to-end | Native sight/chase/bite/death and gunshot-hearing/windup cancellation receipts. `infected-navigation.json`: cover blocks sight, hearing investigation takes a native detour, actual calf hit changes vitality 65→45.5 and speed 320→160 cm/s, sight reacquisition/loss and investigation expiry, pursuit along parked RV exterior and usable firing nearby. |
| Infected multiplayer | `infected_attacks_emulated`: both players receive replicated contaminated bleeding bites; repeated cooldown cycles remain bounded by one injury per completion; both deaths replicate once. Equipped client disconnect removes its survivor; native rejoin gives one fresh empty inventory and retains exactly the host's gun/magazine/12 rounds. |
| Contention/disconnect | Concurrent held-E world magazine claims have one winner. Moving a spare during native R reload aborts without loss. Shared magazine contention has one owner. Pending-reload disconnect preserves shared GUID/round state. |
| Stress | 100 real semiautomatic input presses, seven reloads, 120→20 total rounds, all nine GUIDs/conditions preserved, one reserved magazine and clean final unload. No impossible quantities or replayed shots. |
| Moving RV | Both host-driver/client-armed-passenger and client-driver/host-armed-passenger pass. Standing passenger uses 4/R/LMB, walks front/rear/sideways at low/road/~60mph fixture speeds, turns and brakes; twenty stopped V round trips per role pass. Recorded correction count/max are zero. |
| Accepted RV paths | `rv_controls_host`: native physical side door entry/exit, cab↔living, both dinette seats, bed lying/Z/R/E, ladder/roof/return and replicated door. Rendered moving passenger inspected. |
| Inventory/survival | `storage_survival_client`: native E/T/Tab/I/G moving pantry transfers during turns, shared exterior contention, drop/repick identity/condition, weight/volume rejection, hour drain and one-time consumption. 20 server/12 client checks pass. |
| Fuel/electrical/medical authority | Resource smoke preserves fuel quantity/condition/drop/repick/shared storage/source bounds. Corrected `resource_guard_host/client` each tests the normal E panel approach, healthy owned change and matched downed rejection under native 100ms/2% emulation; both roles pass. |

Network profiles use outgoing 100 ms latency and 2% packet loss per endpoint
(approximately 200 ms added round trip), rather than claiming a measured real
internet latency. Unreliable cosmetic loss does not mutate gameplay. Representative
combat/medical/AI/reconnect and moving passenger tests use this profile. Pure grip/
pose adjustments did not trigger repeated full expensive matrices.

### Failures investigated during final validation

- The old two-player resource fixture lined players up toward the cab panel. With
  skeletal Visibility hit queries enabled, the farther player's approach can be
  occluded by the nearer humanoid. One E attempt instead completed the inherited
  test counter. The nearer client healthy control succeeded. Testing each role
  from the foremost clear approach restores real E and control validation. No
  resource access, medical rejection, or collision rule was relaxed. Failed full
  resource receipts and obstructed guard receipts remain for audit.
- A synchronous reflective NavigationSystem Python diagnostic raised a handled
  ensure on a class-default-object GetWorld check. CrashContext reports **Ensure**,
  not a fatal world-leak crash. The editor continued and shut down cleanly. Remove
  that diagnostic; prove the cover detour through native AI path following instead.
  Start the test clock after fixture setup: expensive setup previously compressed
  equip/reload events into one frame and invalidated later shot evidence. The
  corrected sequence passes; repeat teardown verification follows below.
- New fixture attempts hit EditDefaultsOnly restrictions on transient objects and
  fresh struct wrappers. Use a separately saved development Data Asset and its
  owned metadata proxy. Python's boolean/out-parameter rejection returns None;
  verify CanAccept error plus None plus unchanged inventory, rather than bool(error).
  Non-reflected control row fields are not Python properties; inspect actual live
  TextBlock labels. These were harness errors, not repaired gameplay by weakened checks.
- Reconnect cleanup initially accessed module globals after runner release. Cache
  only engine functions/scalars for the short rejoin callback and reacquire the
  new controller. Return immediately after release so the old tick cannot access
  cleared globals. Corrected native disconnect/rejoin passes with no retained world.

### Risk-based regression and limitations

One representative final regression pass covers native movement/interaction,
seats/possession, moving reference frame, bed/rest, ladder/roof/physical entry,
workstations/storage, capacity/consumption, fuel/power and medical/downed/revive.
Historical complete Gate1–8.5 suites, long resource simulation, every repair recipe,
rollover orientation matrix and every old visual pose were intentionally not
repeated: no vehicle physics, CharacterMovement, reference-frame, recovery, repair
or persistence code was changed. Their accepted maps/content remain byte-preserved.

Prototype limitations: one hitscan semi-auto 9mm, no separate chamber or loose-round
repacking, no final weapon/medical/attack animation polish, no lag compensation,
nominal magazine mass does not decrease per cartridge, no full persistence/offline
state. Reload chooses a compatible spare automatically; U unload is required before
moving a loaded gun/magazine. Firing while seated/resting/climbing/treating/downed is
rejected. The parked-RV navigation test covers reachable exterior paths; infected do
not board moving RVs, predict vehicle paths, or dynamically rebuild regional navigation.
No horde/director/world loot/human AI/Gate10 work. Refrigerator collision stays in
its accepted deferred backlog. The previous Gate8 resource qualification was already
resolved in Gate8.5; these clear-approach guards are additional regression evidence.
