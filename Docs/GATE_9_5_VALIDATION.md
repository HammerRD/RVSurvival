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
