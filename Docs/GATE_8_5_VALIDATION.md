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
