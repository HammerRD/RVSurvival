# Gate 9.5 — Combat, input and difficulty refinement

Status: ACCEPTED at prototype quality after manual weapon refinement. Gate 10 has not started. Accepted Gate 9 baseline: `566ae69`.

## Framework review and recovery baseline

Reuse Enhanced Input mapping contexts, native User Settings key profiles and asynchronous settings saves. Extend the existing UMG controls rather than introducing a second binding store. Actor Components, replicated GameState rules, owned PlayerController requests, Primary Data Assets, native traces, montages and the existing inventory/needs/GAS medical systems remain the foundations. Gameplay-specific difficulty factors and melee rules belong to RVSurvival; networking, animation playback, input persistence and timers remain engine-owned.

Initial working tree contained unrelated `Config/DefaultEngine.ini`, `.vsconfig`, `Automation_RVSurvival.slnx` and `RVSurvival.slnx` changes. Preserve and exclude these from refinement commits. Never print account configuration contents. Preserve prior test maps and all 108 RV vendor files.

## Free asset acquisition

Xeradev **M1911 (FREE)**: https://www.fab.com/listings/77247d26-33a3-4dba-a840-7a7d8c92bb9c . Fab listing inspected October 8, 2026: free, Standard License, Unreal 5.3–5.8, FBX and textures, explicitly **.45 ACP**. Added to the user's Fab library without a payment or additional agreement prompt. Browser download receipt stalled; downloaded archive inspection found the complete non-rigged pistol, magazine, cartridge and rigged pistol FBX entries. Import and presentation validation are pending. Do not claim this model represents 9mm. Listing NoAI designation remains respected: no training or generative asset transformation.

## Initial validation plan (historical)

Tap pickup and retained timed actions; full controls/conflict/default/persistence/current prompts; difficulty presets/custom and server authority; data-driven grip/sights/muzzle; actual sight ADS; unarmed and one melee weapon with geometry/range/ownership/cooldown checks; real player-visible presentation; separate-process multiplayer and representative 100 ms latency/2% loss; affected-system regressions; final saved-map/build/shutdown/vendor verification.

No acceptance claim is made before those checks pass.

## Free asset integration checkpoint

Xeradev **M1911 (FREE)**, Fab listing https://www.fab.com/listings/77247d26-33a3-4dba-a840-7a7d8c92bb9c, is offered under the Fab Standard License. The listing identifies .45 ACP, game-ready FBX, basic rig, PBR textures and Unreal 5.3–5.8 support. No payment was made. The asset was added to the owned library; the user explicitly approved the Fab agreement for these free downloads. No generative asset transformation or training was performed.

Imported the non-rigged pistol/magazine FBX and Unreal PBR textures under `/Game/ThirdParty/Xeradev/M1911`. Project-side materials live under `/Game/Combat/Gate9_5/Materials`. Original downloaded files are preserved. A separate .45 ACP item configuration uses seven-round magazines; accepted 9mm assets remain unchanged.

The initial authoring script used incorrect reflected FBX boolean property names (`ImportMesh` instead of `bImportMesh`). It exited cleanly, without a crash. Correcting the names against installed engine headers allowed the script to save the new map and content successfully. Both authoring runs shut down cleanly.

Focused single-player PIE normal-input handgun validation: **18/18 passed** (`foundation-input.json`). Covered owned equip, reload, single click, continued hold without repeat, partial reload conservation, aim press/release, holster/re-equip, unload and GUID uniqueness. These results do not establish visual grip/ADS correctness or multiplayer acceptance. Texture material assignment receipt: `materials.json`.

## Resumed recovery and focused input validation — 2026-10-09

Resumed WIP checkpoint `26762ed` without discarding the free-asset milestones `1c68a38` and `27ed4d3`. Saved package bytes matched that checkpoint; fresh editor audit loaded every new Gate9.5 asset and saved the map. All 108 RV vendor packages match baseline `0b6eff6` (`vendor-resume.json`). Development Editor resume and current-binding HUD builds passed.

Added a native timed counter fixture to the new test map. Ordinary definitions default to a zero-duration tap; the physically carried battery explicitly retains a configurable 0.5-second pickup hold. Existing medical/repair/revive/bed durations remain on their accepted implementations. Inventory and melee help now read the current native key profile. Back/Settings reuses the remappable ClosePanel action, closing active panels before opening Settings; no second key-binding store was added.

Focused normal-input receipt `feature-input.json`: **20/20 passed**. Includes 80ms ordinary pickup, owned melee equip, short-range defensive shove, weapon damage, missed/distant attack, wall occlusion, cooldown, existing fatigue effort, Relaxed/Custom/Standard rules, nonfinite request rejection, early-release timed counter cancellation, successful hold and no repeat during continued hold.

Retained failed fixtures are not gameplay passes: initial aiming before the pawn settled missed a tiny magazine; the shove target was at the edge of its short range; a generic wall selection and retained infected obscured later timed targets. Native development-only trace output identified `RVInfected_0 / CharacterMesh0` as the actual timed-ray blocker. Moving that fixture out of the ray resolved the hold/no-repeat checks. Python did not expose the engine's internal spawn/break-hit helpers, so the test uses a saved native counter and a development-only read-only native trace description. No leak detection was disabled. Each run stopped PIE and shut down normally.

Free RED2000 Crowbar is imported under `/Game/ThirdParty/RED2000/Crowbar`, CC BY 4.0; required credit/source/license are in `THIRD_PARTY_ASSETS.md`. No purchase. Weapon visual/ADS and settings UI/persistence/network acceptance are still pending. Mesh export inspection established the M1911's local -X barrel direction and actual rear/front sight coordinates for subsequent render-based alignment.

### Presentation/UI findings before animation iteration

The first rendered M1911 pass is not accepted visually: hand/grip alignment needs improvement, and ADS requires a settled render rather than its first transition frame. Initial mesh-measured offsets are saved in the new weapon definitions only; existing 9mm and RV vendor source remain unchanged.

Actual F10/key-selector interaction exposed an engine callback issue missed by source-only checks: Slate `SInputKeySelector::SetSelectedKey` emits the selection delegate. Restoring the old key after a detected conflict recursively cleared the pending key/warning and saved the old binding. Added a scoped programmatic-update guard and restrained key-button styling. Build passes; UI retest is pending. Existing binding save was backed up under Saved/Gate9_5Validation before remapping.

Epic's supported Two Bone IK / Hand IK Retargeting pattern is being evaluated for keeping the owner hands on the sight-aligned weapon. Native animation nodes will remain cosmetic and will not modify CharacterMovement, reference-frame transforms or hit authority. See https://dev.epicgames.com/documentation/unreal-engine/animation-blueprint-hand-ik-retargeting-in-unreal-engine .

### Native hand IK iteration — not yet visually accepted

Saved a Gate9.5-only humanoid profile and Animation Blueprint derived from the accepted character assets. Native Two Bone IK nodes and a hand rotation node run only for the locally controlled owner's sight ADS; reload, seated, bed, downed and ladder poses disable the cosmetic targets. No character movement, base or authoritative shot transform changes were introduced. Native build and content authoring passed; the editor released references and shut down cleanly.

Settled rendered evidence exposed an incorrect initial grip rotation: the Epic hand bone already faces approximately opposite actor forward, while the M1911 barrel points toward mesh-local -X. Applying another 180-degree grip yaw pointed the ready pistol backward. The asset-specific grip is being corrected independently of the sight reference. The sight line aligns in the settled render, but hand placement remains visibly poor and is not accepted. This is an active presentation iteration, not a completed visual milestone.

Expanded current-binding prompts for the timed test counter, electrical controls, RV driving/exit, ladder and Settings back action. Development Editor build `current_prompt_build.txt` succeeded. Full menu interaction/persistence and paired multiplayer acceptance remain pending.

### Resumed player-facing and paired validation

Actual Windows player inputs opened F10 Settings, selected Fire's key button, attempted conflicting K and received the retained Fridge warning. Choosing Q saved and applied immediately; Q fired once and consumed one round. Melee N, Interact P and Accelerate Y were selected through their real rows. A clean shutdown/restart loaded all four bindings, confirmed by native Enhanced Input profile inspection and actual Q/N gameplay inputs. A subsequent Fire M change also fired immediately. The native framebuffer shows M in gameplay help. Some window captures retained an earlier rendered frame; native `shot showui` evidence was used to cross-check presentation. Restore Defaults was clicked in the actual menu; native profile inspection then confirmed LeftMouseButton/B/E/W.

Dragging the RV fuel-consumption slider activated Custom. Clicking Relaxed updated the displayed hunger/thirst/fatigue sliders to 0.70x. These were actual menu actions, not direct GameState calls. Shared difficulty still needs the final client read-only UI/network-emulation pass. Look/orbit rows now offer a native UMG mouse/stick dropdown because Slate's key selector does not capture pointer movement; it reuses the same native MapPlayerKey/apply/save path. This addition compiles; its visual interaction check remains pending.

Separate-process Listen Server receipt `network_trace`: host and client .45 ACP reload/fire, independent ammo, authoritative host preset/Custom convergence, rejected client changes, crowbar equip/damage and cooldown protection passed. Earlier attempts are retained: the first launch inherited Standalone mode and timed out cleanly; the initial melee fixture was already killed by preceding gunshots; one subsequent client swing missed. Isolated live targets and native view-ray inspection produced a passing paired rerun. Representative latency/loss and broader final regressions remain pending; no range, obstruction or authority check was weakened.

Native hand-bone measurement corrected the asset-specific grip and support position. Settled sight ADS now has a clear view through the weapon sights; the HUD reticle hides during settled sight ADS. Hand/finger polish remains prototype quality. A real ADS-to-holster input probe confirmed FOV returns to 90 degrees with the weapon unequipped (`ads-holster-camera.json`). Fixed the missing-definition holster path, which previously bypassed camera restoration. Reload disables cosmetic hand IK.

Crowbar idle initially left the hands below first-person view. Reused Epic's raised armed locomotion for the prototype melee-ready pose; the native montage still presents the swing and authority traces still decide damage. The rendered ready/swing probe and remapped N input confirmed the raised state and one melee completion. Crowbar grip was moved from the wrist to the palm using project-side item data. Final remote/moving render validation is still pending. All resumed editor runs closed cleanly; no world-leak detection was disabled. Recovery checkpoint `4020083` precedes these iterations. Gate9.5 remains IN PROGRESS.

## Final closure - 2026-10-09

Gate 9.5 is ACCEPTED at prototype quality. Gate10 has not started. Earlier pending statements above describe historical checkpoints, not the final state.

### Implemented architecture

Native Enhanced Input User Settings is the single binding store: MapPlayerKey, ApplySettings and AsyncSaveSettings. Native UMG controls use the existing restrained theme, grouped remappable actions, conflict warning/intentional confirmation, defaults, sensitivity and invert. Mouse/stick axis rows use UComboBoxString with readable themed entries because UInputKeySelector cannot capture mouse motion. Keyboard remapping was manually exercised; controller-compatible key/axis configuration was exercised, but physical controller hardware was not tested. No development controls appear in the normal menu. HUD/panel help reads the current profile; a read-only PlayerController binding-label wrapper supports future Blueprint prompts.

URVDifficultyProfile Primary Data Assets configure 16 bounded factors. Replicated ARVGameState snapshot/revision and owned PlayerController requests enforce host-only changes; client UI is read-only. Presets Relaxed/Standard/Harsh and Custom feed existing needs, GAS medical, infected, fuel, generator, cooling and engine wear. Loot/population remain clearly marked configuration preparation. Shared rules reset per PIE/session; lobby/dedicated-server administration and world-save persistence remain future work. Personal preferences never alter authoritative rules.

FRVCombatItemSpec contains configurable grip, support hand, sight/eye-relief, muzzle/ejection, holster and FP/TP offsets. M1911 is .45 ACP with seven-round magazines, separate from retained 9mm. Final grip (-14,-1.5,3.5) cm, rear-sight reference (3.1,0,6.35) cm/pitch .16/yaw180, eye relief30cm, muzzle(-15.5,0,4) cm/yaw180. Cosmetic owner ADS blends the mesh through actual rear/front sights and solves hand IK in the project-side Animation Blueprint; reticle hides when settled. Server hit validation remains independent of visual offsets. Reload disables IK and holster restores FOV90. Crowbar grip(-11,-1.5,-8) cm. Holster attachment data is prepared; unequipped weapons currently hide rather than displaying final holstered equipment.

Project-side ABP/profile reuse Epic locomotion, slot/montages and native TwoBoneIK/ModifyBone nodes. Melee-ready uses Epic raised armed locomotion; prototype shove/crowbar montages show the attack. No CharacterMovement, movement-base or character replication rewrite. Per-weapon visual data remains replaceable. Capsule remains movement collision.

Ordinary pickups default to tap; carried battery remains a .5-second hold. Accepted treatment/revive/repair/bed actions retain their durations. One inventory/equipment GUID system supports firearm and crowbar. Melee owned RPC validates state, revision/request, range, cooldown and geometry; sphere sweep plus occlusion ray yields one hit per attack. Shove is short-range/low damage with infected stagger; crowbar has one light attack. Effort uses existing fatigue and exhaustion scaling. No new stamina system, heavy combos, final durability or tool utility.

### Actual validation and evidence

* Single-player native inputs: foundation-input.json and feature-input.json passed handgun equip/reload/fire/conservation, tap pickup, retained timed hold/cancel/no-repeat, shove, crowbar, cooldown, range, wall obstruction, fatigue, difficulty contract and invalid request.
* Real Settings UI: remapped Fire Q then M, Interact P, Melee N and RV accelerate Y; actual firing/melee inputs worked. Conflict warning persisted correctly. Clean restart loaded bindings; Restore Defaults restored LMB/B/E/W. Native controller-axis dropdown selection saved, then defaults restored MouseX. Personal bindings are now defaults after this test. binding-label-probe.json verified immediate Q, settled Q, and reset Left Mouse Button.
* Real UI difficulty: fuel slider moved mode to Custom; Relaxed displayed .70x needs. Saved audit loaded all three profiles with16 valid bounded rules and ordered hunger factors. Server preset/Custom convergence and rejected client override passed in separate processes.
* Manual/rendered views: actual M1911 sights, ready/fire/reload/holster and crowbar ready/swing were inspected. Remote handgun/crowbar renders show full character/equipment. Prototype finger/hand contact and static slide/magazine presentation remain imperfect but usable. No paid asset or custom animation engine was introduced.
* network_emulated_server/client.json: separate-process listen server, configured outgoing100ms latency/2%loss, host/client reload/fire, independent ammo, client-local runtime FireQ without changing hostLMB, host Custom1.7 convergence, denied client difficulty, crowbar hit/cooldown. Passed. Runtime client remap was deliberately not saved because both local PIE processes share one Windows save directory.
* storage_regression_server/client.json: native E/3/T/Tab/G paths; moving pantry transfers during turns, both dinette seats/stand, exterior shared-container contention, drop/repick stableGUID/condition .62, capacity rejection, needs drain and owned consumption. Passed.
* moving_regression_server/client.json: client driver/host standing passenger under100ms/2%loss; low500cm/s, road1800cm/s, highway2700cm/s (about60mph), front/rear/sideways walking, standing, acceleration, turning, braking/resume, firing while riding,20 V-to-passenger/1-to-driver cycles. Passed without floor fall. Server/client reference-frame diagnostics reported0 corrections/max0cm. Speed phases use an explicitly recorded server physics fixture to bound coverage, not a claim of final handling tuning. Animation speed reached200cm/s while walking. Storage run also covered host driving/client interactions.
* resource_rates_final_server/client.json: healthy client normal-E panel plus owned request changed InteriorLights; downed repeat left circuit/revision unchanged and cleared access. This supplies the formerly missing Gate8 healthy positive control. Native difficulty-effect fixture doubled hunger/thirst/fatigue rates: [80,80,20] -> Standard[79,78,20.6667], 2x[78,76,21.3333] over600 simulated seconds. This fixture checks effects, not UI authority (tested separately).
* final-saved-audit.json freshly loaded all new assets, saved dirty content/map and verified .45/7round/sightADS and profile data. final_build.txt succeeded Development Editor/Win64 (target up to date after prior successful changed-source builds). final_saved_editor.log and bounded regression logs ended with clean editor exit. Persisted PIE restored standalone/one-player/one-process/emulation-off/no child automation command.
* vendor-resume.json: all 108RV source files SHA256 match0b6eff6. Prior accepted test maps preserved. Refrigerator collision remains deferred and unchanged.

### Failures, fixes and testing scope

Recovered pause checkpoint rather than recreating content. Fixed native key-selector restore recursion (warning was cleared by OnKeySelected re-entry), axis remapping capture limitation, stale hardcoded help, gun orientation/grip, ADS reticle/hand alignment, holster FOV restoration and low melee-ready hands. Earlier fixture misses/blocked rays and a killed melee target were diagnosed, not counted as passes. The added needs probe initially modified copies returned by an Unreal struct-array iterator; writing modified entries back into the array fixed the fixture. Initial final-regression launch used ExecutePythonScript, which exited before callbacks; using the established interactive py command path completed the bounded run. No world-leak suppression or gameplay authority relaxation. No resumed editor crash.

Risk-based regressions targeted interaction, inventory, survival tuning, seats/possession, moving interior, electrical controls, medical downed guard and combat/infected. Did not rerun every Gate1-9 map after pose/offset/style changes or repeat unrelated full stress matrices. No new claim of comprehensive long-duration coverage. Separate-process emulation was concentrated on affected authority/presentation states.

### Recovery/checkpoints and final scope

566ae69 acceptedGate9; 1c68a38 freeM1911; 27ed4d3 freecrowbar; 26762ed pauseWIP; fc94fa3 focused input; 002c5da and4020083 animation recoveryWIP; 9c66b41 settings/presentation recoveryWIP; 00788f2 emulated authority/binding checkpoint. Final closure checkpoint follows this document. Exact changed paths are recorded in Gate9_5Results/changed-files.txt.

Saved map: /Game/Maps/Gate9_5CombatRefinementTest. New project character ABP/profile/montages, combat game framework/presets/itemdefinitions/materials and imported free meshes/textures are confined to their Gate9_5/ThirdParty folders; accepted battery definition explicitly retains timed physical pickup. Original source archives remain preserved locally. Free-source/license/credit record: THIRD_PARTY_ASSETS.md (Xeradev FabStandard, RED2000 CC BY4.0).

Known limitations: prototype hand/finger/reload artwork, controlled montage rather than final melee animation, one light attack, physical controller hardware untested, session-only world difficulty, no dedicated-server/lobby UI, no final holstered equipment, refrigerator collision deferred. No world scavenging, procedural loot/population, hordes, extra weapon catalog, paid art or Gate10 implementation.

Pre-existing unrelated Config/DefaultEngine.ini, .vsconfig, Automation_RVSurvival.slnx and RVSurvival.slnx remain excluded. Raw editor logs/intermediate captures are preserved locally under Saved/Gate9_5Validation; curated receipts/render evidence are committed. Unreal and child PIE/build processes are closed before stopping. Recommended next task: manual Gate9.5 review using the saved map/settings; start Gate10 only after explicit authorization.


## Additional manual weapon refinement - 2026-10-09 (in progress)

Recovery baseline26be374. User reported pitch hand separation, wrong ready/ADS posture and two-hand crowbar presentation. Inspection found ADS-only world-derived targets, a separately repositioned weapon and shared pistol-ready locomotion for melee. The revised weapon remains attached to the primary hand; native IK rotates primary before solving support in primary-bone space. Family profiles distinguish handgun and one-handed melee. Native Enhanced Input retains the saved Fire row identity but labels it Primary Attack; old separate Melee row is deprecated/hidden. Ordered owned-GUID cycling includes unarmed and preserves loaded magazines. Server chooses three one-hand montage variants and resolves one validated strike at the configured hit time; switching during that brief pending hit is rejected.

First pitch render matrix showed effectively zero support target error, but exposed owner torso-camera penetration and open crowbar fingers. Reduced owner torso pitch is family-configurable; hand IK still receives full pitch. Crowbar ready now retains Epic pistol finger grip while returning the other arm to a free unarmed posture. Build API mismatch for TwoBoneIK target was corrected against UE5.8 native headers. Initial identity assertions used Python struct equality instead of native Guid equality and are being corrected. No new acceptance claim until refined visual/control/network checks pass. No Gate10.


## Manual weapon refinement closure - 2026-10-09

Gate9.5 remains ACCEPTED at prototype quality after this focused refinement. Gate10 was not begun. This section supersedes the earlier shared tool-ready pose, weapon-repositioning ADS and separate B melee control descriptions.

### Cause and presentation solution

The reported hand drift came from competing cosmetic weapon repositioning/ADS-only IK and support targets evaluated independently of the rotating primary hand. The old shared raised pistol overlay also gave the crowbar an inappropriate two-handed stance. Epic pistol assets were present already; no rifle animation pack or paid animation was needed. The gun now stays attached to its primary-hand anchor. Native AnimGraph right TwoBoneIK/rotation precedes left TwoBoneIK in primary-bone space, so the weapon-defined support target follows the firing hand throughout pitch and ADS.

URVWeaponPresentationProfile separates Handgun and OneHandedMelee configuration; future LongGun/TwoHandedMelee are enum preparation only. Per-item grip/sight/muzzle/holster metadata remains. M1911 uses ReadyHand (40,3,50) cm, owner torso pitch scale0.25, sight eye relief45cm and high-angle reach retraction up to8cm. The actual rear/front sight reference drives arm placement, with smooth existing aim/FOV transitions. Native forearm twist nodes and shorter high-angle reach keep the arm chain from nearly locking straight. The full camera was not retuned around this weapon.

First-person full-body neck/collar geometry intersected the camera at steep pitch. A native CopyPoseFromMesh owner-only follower uses project-side material derivatives masking head/neck/collar vertices; arms remain visible and the full remote/medical body is unchanged. Shader failures from pre-skinned pixel-stage masking were fixed using a native VertexInterpolator. Existing packed M1911 ORM textures had normal-map sampler classification; project-side mask copies/material references corrected this without editing imported source textures.

Crowbar uses a one-handed ready overlay, wrapped finger/thumb pose and three project-side native animation sequences/montages: Diagonal, Horizontal, Downward. Server round-robin selection prevents immediate repeats. All have the same configured damage/cooldown and one authority hit at0.27s. Weak timer cleanup/revalidation prevents late invalid hits. Switching during this brief committed window is safely rejected. No combos, heavy attack or new durability system.

### Controls and equipment

LMB is Primary Attack: equipped firearm fires, melee swings, unarmed shoves. Fire's native saved mapping identity is retained, so existing attack remaps survive. Deprecated separate Melee rows are hidden/ignored rather than overwriting user bindings. Controls shows Primary Attack, Aim, Reload, Unload, Next/Previous and retained direct4/5 actions. Mouse Wheel Up = Next, Down = Previous, wrapping ordered usable owned GUIDs plus unarmed. Orders live on definitions; no pistol/crowbar-name branching. ServerEquip cancels ADS/reload, reuses one visible equipment mesh and preserves the loaded magazine/condition/GUID. UI-only input and cursor guard prevent cycling while menus scroll.

### Actual validation

* Native E/LMB/4/5/R/RMB/wheel input paths in the saved test map passed equip/reload/fire, all three swings, unarmed fallback, rapid12-step cycling, single visible weapon, magazine GUID/6-round preservation and FOV90 restoration.
* Rendered ready/ADS matrix at -60,-30,0,30,60 degrees was inspected. Both hands remain associated with the handgun; ready is centered nearer the right-hand stance, sights align, and return-to-ready is stable. First-person crowbar grip and three strike renders plus remote handgun/crowbar renders were inspected. These are prototype poses, not a claim of final finger/animation polish. Settled bone-space support metrics accompany the images; numbers were not substituted for visual inspection.
* Real Windows menu/player inputs opened F10, remapped Primary Attack toQ, swung the crowbar withQ, cycled down to the same loaded M1911 and firedQ (7->6). Scrolling Settings changed the panel scroll without equipment changes. The same row was restored to LMB; other mappings were not reset. Current-binding gameplay prompts displayedQ and then LMB.
* Focused interaction/melee regression: 80ms tap pickup, timed hold/cancel/no-repeat, low-damage shove, fatigue effort, cooldown, exactly one armed hit, distant miss and wall obstruction passed. No unrelated difficulty/RV stress matrix was repeated.
* Separate-process normal and 100 ms/2%loss listen-server runs exercised both players' fire/reload, ADS-to-crowbar camera reset, three attacks, remote variants, infected damage, unarmed action, rapid cycling, single equipment visual and partial-magazine identity. Final emulated server/client checks all passed. Firearm torso and melee guarding-arm injuries replicated to both peers.
* The initial normal medical fixture wrongly demanded a torso injury from a sweep intercepted by the guarding arm. The initial emulated montage fixture sampled one frame before a delayed montage arrived. Corrected tests use the actual configured body-region mapping and continuous montage observation with bounded attack windows. Original failing receipts are preserved; no gameplay authority/range check was relaxed.
* ADS fire remained authoritative (one round) and native camera recoil was measured without blocking screenshots during the0.18s effect. Early screenshot capture stalled the recoil observation window and produced an editor-view image; that image was rejected as evidence. The final receipt records the measured recoil and recovered FOV.
* Fresh saved-asset audit loaded family profiles, all 13 refinement assets, three attack montages, six medical mappings and owner-copy materials; saved the map/dirty packages. An initial JSON-only receipt error from Unreal Array serialization was fixed with a Python list conversion. Final Development Editor/Win64 build succeeded. Editor/PIE shutdown was clean, with no World Memory Leak crash or detection suppression.

Risk-based coverage targets character presentation, equipment/input identity, melee geometry, firearm and medical damage. Normal walking/needs/UI smoke remained functional; CharacterMovement/reference-frame, RV mechanical/survival/difficulty gameplay and prior maps were unchanged. Full historical Gate1-9 suites, unrelated separate-process RV/ladder/roof matrices and redundant network runs after individual finger edits were intentionally skipped.

### Saves, scope and limitations

Recovery d2da9db (clearly marked WIP) and stable c4a0858 precede this final closure commit. Authoring scripts saved every meaningful asset milestone; test launchers saved the map and released runner UObjects/callbacks before StopPIE/quit. All 108RV vendor SHA256 hashes match0b6eff6; free source/Epic mannequin paths remain unchanged relative to26be374. No new free asset acquisition or purchase.

Known limitations: prototype finger contact/forearm skinning, small owner collar-cut seams at steep downward views, controlled FK swing/reload presentation rather than final authored motion, no final visible holstered equipment and no physical controller hardware test. These do not detach hands, block the sight view or alter authority. Refrigerator collision remains deferred. Long-gun/two-hand profiles are preparation only. No Gate10.

Evidence/changed path manifest: Gate9_5Results/WeaponRefinement. Raw failed iterations/logs remain under Saved/Gate9_5Validation. Working tree exclusions remain pre-existing Config/DefaultEngine.ini, .vsconfig, Automation_RVSurvival.slnx and RVSurvival.slnx. Recommended next task: manual review of this saved refinement; await explicit authorization before Gate10.
