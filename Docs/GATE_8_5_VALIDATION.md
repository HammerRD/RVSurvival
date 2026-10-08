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
