# Gate 8.5 character presentation validation

Status: **IN PROGRESS — NOT ACCEPTED**. Authorized 2026-10-08. Gate 9 is not started.

## Recovery baseline and scope

Baseline `ab601cf` retains Gate 8's documented downed resource-control validation qualification. The stale in-progress heading in the historical Gate 8 record is superseded by its closure sections and the user's explicit functional acceptance. This pass does not claim to resolve that qualification.

Pre-existing unrelated changes: Config/DefaultEngine.ini, .vsconfig, Automation_RVSurvival.slnx and RVSurvival.slnx. Exclude them from checkpoints. Preserve all prior maps and 108 purchased RV packages. Refrigerator collision remains backlog unless directly worsened by presentation.

## Framework and asset review

Installed UE 5.8.3 includes Epic's high-quality Characters shared template pack. Manny Simple, Quinn Simple and SK_Mannequin are available locally; the project currently has no humanoid skeletal mesh. Select Manny Simple and unarmed idle/eight-direction walk/jog/jump/fall/land clips. Import selected packages and dependencies using Unreal AssetTools migration from a disposable project under Saved. Do not import combat gameplay, weapon assets or a template character's replacement movement/controls.

Source: D:/Epic Games/UE_5.8/Templates/TemplateResources/High/Characters. These are installed Epic template assets covered by the Unreal Engine license, not a purchased character. Retain source provenance and a migrated-package manifest. [Epic Third Person template](https://dev.epicgames.com/documentation/unreal-engine/third-person-template-in-unreal-engine?lang=en-US), [Unreal Engine EULA](https://www.unrealengine.com/eula/unreal).

Use the existing ACharacter skeletal mesh, Animation Blueprint, native animation nodes/Blend Spaces, Animation Sequence data controller, capsule collision, CharacterMovement smoothing/prediction and replicated gameplay states. A reusable visual profile maps logical medical regions and equipment anchors to configurable bones. Animation only reads accepted seats/rest/ladder/health/interaction states. It must not introduce a new movement solver, transform RPC, per-tick character attachment or gameplay dependence on a mesh name.

IK Rig/Retargeter remain available for replacement meshes; no retargeting is needed for compatible initial mannequin clips. Control Rig/advanced steering or ladder IK are optional polish, not acceptance requirements. Controlled poses are preferred over networked ragdoll.

## Planned risk-based validation

Inspect actual in-game skeletal poses and first-person views. Test affected locomotion, seats/possession, bed, ladder/roof, medical/downed/revive and moving interior first. Use a representative separate-process impaired-network pass near closure, plus one broad critical-system smoke pass. Do not rerun all historical gates after visual tuning. No acceptance claim until visible behavior, final build, saves, vendor audit and clean shutdown pass.

## Skeletal integration checkpoint — 2026-10-08

Epic AssetTools migration completed: 43 packages, including Manny Simple, SK_Mannequin, materials/textures and selected unarmed locomotion clips. No rifle/pistol/attack assets were migrated. Saved project-side visual profile, humanoid Blueprint, GameMode derivative, 27-sample directional locomotion Blend Space, normal Animation Blueprint and seven prototype pose sequences. Saved Gate8_5CharacterTest with 86 actors, preserving Gate8MedicalTest and its medical/storage setup.

NativeUpdateAnimation derives presentation inputs from CharacterMovement's own velocity rather than vehicle world translation. The Animation Blueprint contains native BlendSpace/SequencePlayer/Blend Poses by Int nodes, not a custom animation evaluator. Pose priority reads existing bed, health, seat, ladder and treatment state. The component changes only discrete skeletal visual offsets and owner-head visibility. Primary capsule movement, seats/rest authority, camera controls, CharacterMovement solver and networking remain their existing systems. Seat/rest primitive substitutes remain fallback for unconfigured characters.

Configured six medical region mappings and seven bone-attached future equipment anchors. Gameplay does not depend on Manny bone names; they belong to the replaceable Data Asset. Controlled prototype poses, not ragdoll. Full seated/bed/ladder/downed visual inspection and runtime/network acceptance remain pending.

Build initially reported CacheInitialMeshOffset requiring FRotator and editor graph arrays containing TObjectPtr; corrected those API/type mismatches. Foundation repeat succeeded in 6.80 seconds; idle-based pose authoring build succeeded in 23.68 seconds. Content authoring saved all packages and editor exited cleanly without logged Python/fatal/world-leak errors. Recovery baseline checkpoint 0bae815 precedes the integration.

## Runtime configuration and first visual diagnostic — 2026-10-08

Fresh PIE initially selected the old medical GameMode and the presentation component had no saved Profile. Corrected map authoring with an explicitly modified WorldSettings and forced map save, and exposed the native presentation default subobject through a reflected character property so Blueprint component defaults serialize. Fresh startup now loads Manny and the native animation instance; all six region lookups and seven attachment anchors resolve. Build succeeded in 22.80 seconds.

A development-only transient pose fixture uses native SpawnActor because Unreal's internal deferred spawning functions are not exposed to Python. Corrected its skeletal actor include path; repeat build succeeded in 4.49 seconds. Python body-region binding returns the region or None, rather than a tuple; corrected the diagnostic accordingly. Runner releases references before stopping PIE and exiting; the diagnostic editor runs closed cleanly.

Rendered pose atlas is diagnostic evidence only, not gameplay-state acceptance. Inspection found seated legs spreading too far and severe owner torso clipping when looking down. Lying and climbing poses render but their RV placement remains unvalidated. Gate 8.5 remains IN PROGRESS / NOT ACCEPTED. Next: correct pose axes and owner view, then test actual gameplay controls and network-sensitive character states.

## Native-control RV validation and pose iteration

Separate-process host-driver baseline completed (39 server / 35 client checks, no failed checks). Reversed client-driver / host-walker with 100 ms latency and 2% packet loss also completed; receipts remain under Saved/Gate8_5Validation until final evidence selection. These exercise native held controls for physical door entry/exit, E seats, occupied-driver rejection, moving passenger 3-to-aisle, moving-driver rejection, both dinette seats staying awake, bed Z/R, cab/rear return, ladder/roof and walk-away paths. No direct seat/rest completion calls.

Actual remote-player screenshots exposed high seat presentation and an incorrectly centered lying mesh despite passing gameplay-state checks. Added configurable seated mesh offset (-25 cm Z) and corrected lying visual centering (+85 cm X; bed -15 cm Z). These modify mesh placement only, preserving gameplay capsule and authority. Fresh remote bed image now shows the body on the mattress; driver knees and hands are roughly positioned in the cab. Owner camera adds a tunable 20 cm forward visual offset; inspected downward view no longer shows the initial open torso clipping.

Native animation-data authoring aligns limbs from the selected skeleton's local tracks rather than assuming identical left/right bone axes. Refreshed compressed data through public engine APIs before saving. An attempted protected compression-clear API failed compilation and was removed; public API repeat build succeeded. No engine code changes or leak-detection suppression.

Moving dinette screenshots were inconclusive because the transient observation camera was left in world space while the RV advanced. Fixed the development-only camera fixture to follow its context actor; this is observation tooling, not character attachment. Dinette visual recapture, medical/downed presentation, on-foot visuals, highway passenger presentation and final regressions remain pending. Gate 8.5 is not accepted yet.

## Saved pose and normal medical-menu checkpoint

Final cab mesh offset -25 cm Z; dinette offset 0; bed yaw +90, offset (-85,0,0); downed offset (85,0,15). Native animation-data limb alignment removes tilted idle legs penetrating the mattress/floor. Owner camera/authoritative eyes share the same configurable 20 cm forward offset. Only tagged fallback prototype primitives are hidden; future clothing is not indiscriminately hidden.

Final reversed-role separate-process pose run at 100 ms/2% loss passed seat/dinette/bed control paths and rendered captures. Native foot heights correspond to lower cab floor and higher dinette floor. Normal OS F9 + UMG clicks successfully dressed/revived nearby downed teammate and bandaged self; each supply consumed once. On-foot remote captures show idle, directional locomotion, jump and falling, and owner downward view shows body without face obstruction. Workstation/broad smoke and closure remain pending.

## Final implementation and visual review (supersedes interim pose values above)

- Asset: Epic installed-template SKM_Manny_Simple / SK_Mannequin, migrated with AssetTools; 43 packages and dependencies, no weapon/attack content and no purchase. See epic-migration.json.
- Replaceable Primary Data Asset, URVCharacterPresentationComponent and URVHumanoidAnimInstance; native animation graph and directional Blend Space. Editor-only URVCharacterContentLibrary authors ordinary Animation Sequences and AnimGraph nodes, not a runtime animation engine.
- Native CharacterMovement velocity selects idle/walk/jog and eight directions; native jump/fall/short landing presentation. Default movement remains 600 cm/s outside and accepted 200 cm/s inside; no separate sprint mechanic was introduced. Actor turning uses accepted controls; dedicated turn-in-place foot IK is future polish.
- Owner full body uses head-bone hiding and a shared tunable 20 cm camera/authority-eye offset. Remote players retain full head/body. Looking down was inspected without face obstruction; minor close-body edge clipping is prototype quality.
- Cab seated mesh offset (0,0,-25), dinette (0,0,0); final remote foot heights approximately 74 cm and 99 cm in RV local space respectively. Driver arms approximately reach the cab controls; no final steering-wheel hand IK.
- Bed visual yaw +90, offset (-85,0,0), with flattened legs above mattress. Existing Z rest/sleep and R/E stand-up remain the gameplay path. Downed offset (85,0,15) places a controlled supine body above ground; revive restores locomotion and preserves injuries.
- Ladder prototype arm directions face the rungs; signed sequence rate follows climb up/down. Final climb capture shows raised arms instead of normal walking or the initial sideways arm. Roof collision/parked restriction and climb mechanics are unchanged.
- Treatment uses a generic reach pose while existing authoritative treatment GUID is active. Normal F9/UMG teammate dressing/revive and self-bandaging passed, consumed one supply each and closed back to gameplay. No forced cinematic movement or final kneeling/contact animation.
- Six configurable medical regions: head (neck/head), torso (pelvis/spine/clavicles), left/right arm (upper-arm descendants) and left/right leg (thigh descendants). ResolveBodyRegion walks the skeleton to the nearest configured ancestor; region world transforms use configured anchors. Manny names belong to the profile, not dispersed medical gameplay.
- Seven deterministic bone-attached Scene Component anchors: backpack, long gun, handgun holster, tool, carried item, flashlight and medical bag. No equipment/weapon gameplay or final gear art. Alternate meshes/clothing remain profile/animation configuration; only tagged old prototype primitives are hidden.

## Actual validation and risk selection

Evidence is in Docs/Gate8_5Results; full runtime logs/receipts remain under Saved/Gate8_5Validation. Native-held-key tests inject normal Unreal key events into the existing Enhanced Input routes, not direct seat/rest/door/ladder completion functions. OS F9 and actual UMG mouse clicks separately cover the medical menu. Fixture setup, medical fault/supply seeding and controlled speed holds are explicitly development diagnostics. These are agent-operated player-control tests and inspected rendered evidence, not a claim of a new human playtest.

| Area | Result / scope |
|---|---|
| On foot and owner view | Inspected idle, forward/backward, both strafes, jump/fall/land captures; CMC rising/falling states and directional speeds agree. Full remote body, usable owner downward view. |
| Seats/possession | Both host/client role combinations; E cab/dinette seats, occupied rejection, V switching, 1/2/3 transitions, moving passenger rear and stopped driver rear. Both dinettes remain awake. |
| Repeated V | 20 V-to-passenger / 1-to-driver cycles under separate-process 100 ms/2% loss; no below-floor or collision/movement lock. |
| Moving interior | Controlled low 500, road 1800, highway 2700 cm/s (~60 mph), native front/rear/sideways walking and standing; acceleration, braking, resume, gentle highway/stronger road turns. Own animation speed stays around 200 instead of inheriting RV speed. Reversed impaired-network run logged maximum correction 0.0 cm in its measured route; no accumulating local error/floor fall. This does not claim zero corrections for every possible network or terrain. |
| Bed/downed/medical | Final remote seated/dinette/bed renders checked after actual controls; Z/R stand-up. Separate-process emulated downed/treatment/revive in both healer roles, independent patient state, retained injuries and once-only supplies. Actual F9/UMG teammate and self actions additionally passed. |
| Ladder/roof | Final broad E/W/S route: ladder reservation, roof walking past fixtures, parked propulsion lock, ladder return/down and clean ground movement. Focused final arm-pose capture and up/down/return passed; mechanics unchanged by arm-only asset correction. |
| Workstations | Native E workbench, kitchen, real medical station, power and navigation while parked/driving; Escape and walk-away restore usable movement/base. Actual remote character images in narrow aisle inspected, including moving workstation. Correction maximum 0.0 cm in this route. |
| Gate 4/5 smoke | Moving pantry E/T/Tab transfers during turning preserve condition; exterior shared container contention has one conserved tool; G drop/E repick retains exact GUID/.62 condition. Weight/volume rejection, one-hour needs drain and duplicate owned consumption rejection passed. |
| Other foundations | Shared interaction counts through native holds; real Chaos driving in control routes, accepted collision/entry/door/roof and parked restrictions; fuel/electrical authoritative controls, resource state/conservation and disconnect checks reviewed with explicit fixture history below. No historical entire-gate suite repeated after visual-only adjustments. |

Separate-process receipts contain different server/client PIDs. Representative 100 ms outgoing latency / 2% loss is configured in PIE and relevant runner console settings. Final pose and moving-medical/stored-item runs use impaired networking. State assertions alone did not certify poses: actual images caught and drove fixes for cab height, bed centering, floor/mattress leg clipping, observation-camera placement and ladder arms.

## Failures, harness corrections and cleanup

- Saved GameMode/profile initially did not persist: reflected native default subobject, modified Blueprint/CDO/WorldSettings and forced project-side saves fixed fresh-start configuration.
- UE API/compiler mismatches (FRotator initial mesh offset, TObjectPtr graph arrays, SkeletalMeshActor include) were corrected and rebuilt. A protected compression-clear call was removed in favor of public animation cache/wait APIs. No engine modification or leak suppression.
- Prototype limb axes were unsuitable; native animation-data alignment fixed actual poses. Cab and dinette need different mesh offsets; bed orientation/centering and flattened leg tracks fix the rendered placement.
- Observation cameras initially remained world-space and became occluded; fixtures now follow the observed context. Authority/local aim fixture predicts the new configured eye position after yaw changes. Inconclusive captures were not accepted as evidence.
- A brake test held reverse through zero speed and then incorrectly tested parked-only transitions. Corrected fixture releases braking at actual stop, applies/releases handbrake appropriately. Reversed 20-cycle run passed without relaxing parked restrictions.
- Old workstation fixture searched for Medical instead of Gate 8's actual Medical station. Updated identity; full parked/moving native-E route passed.
- Python Guid wrapper equality produced a false repick failure. Native GuidLibrary equality and recorded strings verify identical world/inventory GUID and condition. Gameplay code was unchanged.
- Resource regression initially had client access failures from old approach positions and authority-only relocation under prediction. Recorded failures remain in failed-iteration-history.json; synchronized/surface-derived diagnostic placement and isolated client control tests distinguish legitimate reach/occlusion from gameplay mutation failures. Final scope/results are recorded in the closure below; these failed runs are not silently counted as passes.
- Scoped runner modules release Unreal wrappers and event closures before Stop PIE. Authoring/auditing functions return primitive receipts before collection/quit. No world-leak detection disabled; no known recurring automation crash in this pass.

## Known limitations and retained qualifications

Prototype poses are controlled sequences, with no final seat entry/exit, steering/ladder contact IK, kneeling treatment, turn-in-place polish, ragdoll or clothing system. Equipment anchors are an attachment foundation only. Capsule remains primary movement collision; skeletal bodies do not provide combat hit authority yet. Historic maps retain accepted fallback presentation; use Gate8_5CharacterTest to play the humanoid. Driver/rest/seat-to-seat/roof parked rules remain accepted limitations. Refrigerator collision remains deferred and was not materially worsened or changed.

Gate 8 qualification is retained unless an explicitly documented matched healthy/downed positive-control follow-up proves otherwise. Successful healthy panel access alone does not resolve its downed resource-control gap. No Gate 9 or combat implementation.

## Checkpoints

0bae815 recovery/review; fd70f75 skeletal/native-animation foundation; 05b1431 clearly labeled WIP persistence/visual diagnostics; 22afc44 owner/RV visual refinements with targeted networking; bbb8030 final bed/dinette/clothing-safe presentation and normal medical menu. Final validation/closure checkpoint follows saved audit/build. All meaningful content milestones were saved to disk; purchased vendor files and prior maps were excluded from modifications.

## Resource follow-up and Gate 8 qualification — final matched control

Mixed-resource fixture: all 31 host checks passed; client panel switching/convergence, stale requests and disconnect passed, while its old fuel/exterior approach assertions did not. These remain recorded as failures, not a blanket regression pass. The isolated normal client E/I/F flow then opened the real fill and transferred exactly 20 L from its valid /Game/Resources/DA_FuelCanFull record; native E also opened the specific exterior compartment. One diagnostic iteration used an invalid /Game/Items path, another indexed a Python output string and aborted authority placement; both were harness errors. Normal approach needs clear line of sight, and direct diagnostic relocation needs a settled client/server position. No resource gameplay code was changed or authority bypassed.

The bounded Gate 8 qualification follow-up now has a valid matched positive control in Gate8_5CharacterTest: normal E registered the real power panel; the healthy client's owned request changed InteriorLights; after authoritative downing, the same client's request from the same location was rejected, load/revision stayed unchanged, and owner feedback cleared panel access. Both peers passed in separate processes under 100 ms/2% loss. See character_resource_guard_server/client.json. This closes the specific ab601cf downed resource-control coverage qualification; historical inconclusive receipts remain preserved. No broader medical guarantee or Gate 9 work is implied.
