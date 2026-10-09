# Gate 9.5 — Combat, input and difficulty refinement

Status: IN PROGRESS. Gate 10 has not started. Accepted Gate 9 baseline: `566ae69`.

## Framework review and recovery baseline

Reuse Enhanced Input mapping contexts, native User Settings key profiles and asynchronous settings saves. Extend the existing UMG controls rather than introducing a second binding store. Actor Components, replicated GameState rules, owned PlayerController requests, Primary Data Assets, native traces, montages and the existing inventory/needs/GAS medical systems remain the foundations. Gameplay-specific difficulty factors and melee rules belong to RVSurvival; networking, animation playback, input persistence and timers remain engine-owned.

Initial working tree contained unrelated `Config/DefaultEngine.ini`, `.vsconfig`, `Automation_RVSurvival.slnx` and `RVSurvival.slnx` changes. Preserve and exclude these from refinement commits. Never print account configuration contents. Preserve prior test maps and all 108 RV vendor files.

## Free asset acquisition

Xeradev **M1911 (FREE)**: https://www.fab.com/listings/77247d26-33a3-4dba-a840-7a7d8c92bb9c . Fab listing inspected October 8, 2026: free, Standard License, Unreal 5.3–5.8, FBX and textures, explicitly **.45 ACP**. Added to the user's Fab library without a payment or additional agreement prompt. Browser download receipt stalled; downloaded archive inspection found the complete non-rigged pistol, magazine, cartridge and rigged pistol FBX entries. Import and presentation validation are pending. Do not claim this model represents 9mm. Listing NoAI designation remains respected: no training or generative asset transformation.

## Required validation still pending

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
