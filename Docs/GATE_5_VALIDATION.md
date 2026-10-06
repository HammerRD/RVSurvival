# Gate 5 — core survival needs validation

**Status: ACCEPTED — 2026-10-05. Final live validation, regressions, saved-content audit and build passed.**

Gate 4 was accepted by the user. Gate 5 only is authorized; Gate 6 fuel/electrical gameplay has not begun. This report records actual Unreal testing, not compile-only acceptance. Detailed development/failure chronology is retained in `Gate5Results/DEVELOPMENT_NOTES.md`.

## Implementation and Unreal framework review

`URVNeedsComponent` is a native replicated component on `ARVPlayerState`. It owns nutrition, hydration, fatigue, a minimal survival reserve, elapsed simulation time and rest mode. PlayerState ownership survives driver/passenger possession changes. `FRVNeedsState` is reflected scalar data; persistent scalar fields have SaveGame flags. Rest reservations are transient and do not serialize as gameplay identity. No full save system, offline progression or region streaming is implemented.

RVSurvival rules are hour-based metabolism, activity classification, thresholds, recovery, inventory consumption validation and exclusive parked rest. Unreal provides component lifetime/ticking, PlayerState ownership, Primary Data Assets, Gameplay Tags, native replication/RepNotify/RPC transport, weak TimerManager dispatch, CharacterMovement prediction/based movement, UMG and native queued reconnect travel. No custom transport, scheduler, prediction layer or general effect stack was introduced.

**GAS decision:** evaluated installed UE 5.8 GameplayAbilities APIs and official Epic GAS/Lyra patterns before continuing major implementation. Retained the component for three slow scalar needs and one rest mode; current gameplay does not need predicted abilities, duration stacking or effect aggregation. Do not build a custom medical effect system later: reassess PlayerState-owned ASC/AttributeSets/GameplayEffects before injuries, bleeding, medication or timed/stacking buffs. Current APIs/data separate that boundary from inventory and RV movement. This decision preserves working Gates 1–4 rather than migrating them into Lyra's larger framework.

Sources reviewed:
- [Epic GAS overview](https://dev.epicgames.com/documentation/en-us/unreal-engine/understanding-the-unreal-engine-gameplay-ability-system)
- [Epic attributes/ASC](https://dev.epicgames.com/documentation/en-us/unreal-engine/gameplay-ability-system-component-and-gameplay-attributes-in-unreal-engine)
- [Epic Lyra abilities/PlayerState ownership](https://dev.epicgames.com/documentation/en-us/unreal-engine/abilities-in-lyra-in-unreal-engine)

UMG supplies the new restrained survival readout. Native RepNotify/delegates drive updates and are unbound during widget teardown. Accepted Gate 4 Canvas inventory controls remain; CommonUI's layered/device-routing framework is deferred until required. Accepted movement/driving/interaction still use Enhanced Input. Inventory selection uses the existing native PlayerController key queries, with C consume, Z sleep/rest and R wake added; no custom input framework.

## Tuning and consequences

`URVNeedsProfile` is a Primary Data Asset; `/Game/Survival/DA_NormalNeeds` configures Gate 5's PlayerState. Server component tick interval is 0.25 seconds. Normal rates are not accelerated test rates.

| Need | Start / maximum | Awake idle change per hour | Warning / critical |
|---|---:|---:|---:|
| Nutrition | 90 / 100 | −6 | ≤30 / ≤10 |
| Hydration | 90 / 100 | −12 | ≤35 / ≤12 |
| Fatigue | 10 / 100 | +4 | ≥60 / ≥85 |

Walking multiplier 1.3; heavy-carry multiplier 1.25; driving 1.05; seated passenger 0.8. Standing-passenger activity uses character acceleration, not inherited vehicle velocity. Rest/sleep metabolism is 0.65/0.5; fatigue recovers 10/25 per hour respectively. Sleeping never replenishes nutrition/hydration.

Critical nutrition/hydration/fatigue cap movement at 0.8/0.6/0.65 of native speed; the strongest applicable limit wins. `GetMaxSpeed` reads this policy without mutating/restoring the accepted base movement settings or replacing prediction. Critical hunger/thirst reduce a minimal modular survival reserve at 1/5 per critical hour; integration accounts for threshold crossing within a time step. Reserve clamps above zero; this gate adds no elaborate health/injury/death system. Values, rates, thresholds, recovery and severity are editable tuning data; final balancing is not claimed.

Developer controls require authority, non-shipping/test builds and `rv.Needs.AllowDebug=1` (default off). `DebugSetValues`, `DebugSetTimeScale` and `DebugAdvanceTime` clamp/reject invalid values. Development needs acceleration changes neither Chaos time nor interaction/RPC cooldown clocks.

## Inventory and RV integration

`FRVConsumableMetadata` extends existing item definitions with enabled flag, nutrition/hydration gains, minimum condition and future dietary/calorie metadata. `/Game/Items/DA_Food` gives 25 nutrition; `DA_Water` gives 35 hydration. Their Gate 4 mass/volume/stack/condition/category rules remain intact. Other test items remain inert; medicine, fuel, cooking and spoilage are absent.

Owned reliable consume intent sends only an item GUID. Authority resolves that player's survivor inventory (including the retained driving survivor), rejects stale/unowned/non-consumable/no-benefit requests, removes one existing runtime quantity serially and applies clamped recovery. Remaining stack GUID, condition and custom state survive. Last-item duplicate requests cannot produce a second completion. Clients cannot supply effects or mint item state. Shared items must first transfer through the accepted authoritative container transaction.

`ARVRestPoint` is a reusable exclusive interactable, independent of RV art. Rear bed and dinette reservations replicate occupants as PlayerStates. Hold E begins rest; Z toggles sleeping/resting; R leaves. The character remains at its current native floor/base, with walking/jumping restricted while resting; no sleep teleport/attachment or elaborate animation. Disconnect/teardown releases reservations. Rest/sleep currently requires platform speed ≤50 cm/s and wakes when the RV moves. Both rest surfaces were validated simultaneously.

`/Game/Maps/Gate5SurvivalTest` is saved with 64 editor actors: preserved purchased RV/drive space, eleven pickups, seven storage points and two rest points. It uses `/Game/Survival/BP_Gate5GameMode` and `BP_SurvivalPlayerState`. Water supplies are a finite filtered cupboard, not a water-tank simulation. Existing pantry, general/medical/tool/exterior cabinets and six workbench/medical/kitchen/storage/power/navigation placeholders remain. Vendor art and accepted maps/fallbacks are unchanged.

## Actual validation

UE 5.8.3 CL 58210709, Development Editor / Win64; VS 14.44.35229 and Windows SDK 10.0.22621.0. Listen-server tests use two players. Independent-process cases use Run Under One Process **disabled**, confirmed distinct PIDs. Representative emulation uses outgoing-server min/max latency 100 ms and 2% packet loss; it is not a claim of bidirectional 100 ms or arbitrary fault tolerance.

| Test | Actual result |
|---|---|
| Final single-player | 27/27 passed: real pickup/consume, stacks/last item, stale/invalid GUID, condition/custom state, rest/sleep, clamping/status/consequences and analytical day |
| Survival separate process, baseline | 13 server + 13 client checks passed; 32 paired checks |
| Survival separate process, 100 ms/2% | 13 server + 13 client checks passed; 32 paired checks |
| Host drives / client walks, baseline | 70 server + 71 client checks passed; paired local discrepancy max 10.34 cm |
| Client drives / host walks, baseline | 72 server + 65 client checks passed; discrepancy max 8.69 cm |
| Host drives / client walks, emulated | 70 server + 71 client checks passed; discrepancy max 10.23 cm |
| Client drives / host walks, emulated | 72 server + 65 client checks passed; discrepancy max 26.88 cm |
| Native remote UI, 640×480 | 7 state checks and visual review passed; physical I/Down/C/Z/R controls |
| Accelerated stress, initial complete run | 200 consumptions / 200 GUIDs, 100 actual shared withdrawals, 20 rest/sleep/wake cycles; 86,404.89 seconds through real component ticks; no item/reservation/actor residue |
| Native same-process reconnect, emulated | Two corrected settled repeats each passed 7 server + 5 client checks; clean teardown |
| Gate 1–4 final regression | Gate 1: 23/23; Gate 2: 24/24 plus 4/4 possession checks; Gate 3: all four full moving matrices; Gate 4: 24/24 |
| Saved map startup/shutdown review | 23/23 checks; Gates 1–5 loaded twice, five assets and metadata verified, Save All and clean exit |
| Final accelerated stress repeat | 6/6 aggregate checks; 200 consumes, 100 shared withdrawals, 20 rest cycles, 86,403.47 simulated seconds; no residue |
| Final build | Development Editor / Win64 succeeded; final verification up to date, zero build actions |

Moving routes retain front/rear/sideways walking, standing, acceleration, braking, low/moderate/highway speed, gentle/strong turns, stop/resume, exit/reentry, six stationary/moving workstation interactions, pantry/medical/tool transfers, drop/repick and observer checks. Gate 5 adds stationary/highway/turning eating, road-speed drinking, continuing riding needs, independent possession state and confirmed parked sleep → movement wake. Storage actions were delayed eight seconds to insert the parked sleep test; no original movement requirement was removed.

All eight moving receipts recorded **zero floor-loss samples** in measured travel/storage windows. Largest actual passenger correction was **1.798 cm** in the emulated client walker; baseline/server-walker measured windows recorded zero. Paired observer timing discrepancy is reported separately from true local correction. Standing-drift and floor/correction receipts are in `movement-telemetry.json`; setup fixture teleports/corrections are not misrepresented as gameplay movement.

Permanent compact receipts: `Docs/Gate5Results`. High-frequency raw samples and private full logs: `Saved/Gate5Validation`. Counts target specific failure modes; stress operation counts are not presented as hundreds of artificial assertions.

## Failures, recovery and cleanup

- UHT name collision between struct/class resolved by naming the Data Asset `URVNeedsProfile`; builds then passed. Deprecated net-frequency assignment and float warnings were removed.
- Read-only Python tag-container setter repaired with Unreal's GameplayTag library. Partial content was immediately Save All'd and preserved, not recreated.
- Single harness live-struct alias/non-exported movement getter repaired. Stress elevated fixture was re-aimed after floor settling.
- UMG initially off-screen because UE's position setter resets anchors. Position-before-anchor ordering fixed; font enlarged for 640×480 and verified physically. Widget subscriptions clean up on teardown.
- Moving drinking's initial fixed expectation omitted genuine accumulated hydration drain; checks now measure pre-consumption value plus configured recovery. Rest was initially attempted at 1,465 cm/s; the parked policy correctly rejected it. Test now verifies actual parked speed and confirmed sleep before wake.
- Disconnect caller initially read globals after clearing its module. It now returns immediately. Reconnect readiness/name/world-scope/timing issues were fixed without changing gameplay checks. Native queued travel uses only primitive persistent Python state and reacquired active-world references.
- A failed reconnect timeout repeatedly reset its exit deadline after Stop PIE. The guard was fixed. Windows UI activation failed twice; only that exact already-stopped/All Saved test process was terminated after command-line verification. This failed run is recorded as **forced cleanup**, not clean shutdown. Corrected runs use native clean teardown.
- Final audit used an incorrect Python boolean attribute spelling; replaced it with the reflected property getter. The corrected audit passed all checks. One idle, fully saved editor was closed through graceful Windows taskkill without force, with clean engine exit recorded.
- No new reproducible World Memory Leak fatal error was found; leak detection was not disabled. Unsupported World asset duplication/reload cleanup was not used.

## Limits and persistence boundary

Prototype balance, UI/art and logical standing rest poses remain. Parked-only sleep/rest is intentional; auto-wake on movement is validated. There is no full save/offline progression, persistent reconnect inventory, disease/temperature/nutrition-science/spoilage/contamination, full health/medical effects, cooking, fuel/electrical or streaming implementation. Reconnect creates a valid new session pawn; shared storage/other players are preserved, not a claim of full persistent character recovery. Existing seated inventory UI and Gate 3 rough-terrain/larger-party limits remain. Full timed/stacking medical effects require a fresh GAS decision before implementation.

Future persistence records need nutrition, hydration, fatigue, survival reserve, simulation time and a stable player identity; rest reservations should safely restore awake. Relevant saved timestamps/offline policy remain future design. The RV remains interactive during planned authored/procedural regional transit; no survival rule depends on one pawn or editor test state. Long-term region/party-cohesion decisions are in GAME_DESIGN.md and TECHNICAL_ARCHITECTURE.md.

## Saved files and checkpoints

New native files: `Public/Private/Survival/RVNeedsComponent`, `RVRestPoint`; `Private/Player/RVPlayerState.cpp`; `Public/Private/UI/RVSurvivalWidget`. Modified inventory definition/component, PlayerState/controller/survivor, CharacterMovement speed policy, HUD, vehicle seat-entry guard and Build.cs (UMG). Content: Gate5SurvivalTest, DA_NormalNeeds, BP_SurvivalPlayerState, BP_Gate5GameMode and Food/Water metadata. Validation tooling and required design/network/inventory/RV/roadmap/changelog documentation are committed.

Checkpoints: `61178dc` foundation; `e518d58` framework/UMG; `7c4c0e6` saved content; `5677c47` single-player/framework decisions; `7502418` UI/lifetime/stress; `41b06a8` native controls; `42273e5` baseline authority/moving roles; `2cb14dc` emulated movement/reconnect/telemetry. `f41330a` final regressions/stress; final acceptance checkpoint follows this report. See local Git log for its exact hash.

Vendor SHA-256: 108/108 match accepted import. Accepted Gate 1–4 maps and existing vehicle/fallback files have no diff from `7881ab0`. Existing unrelated `Config/DefaultEngine.ini`, `.vsconfig`, `Automation_RVSurvival.slnx`, `RVSurvival.slnx` are preserved outside commits; the configuration's security token is not reproduced in reports.

Final regression milestone: final single-player 27/27; Gate 1 23/23; Gate 2 24/24 plus 4 inventory-possession checks; Gate 4 expanded inventory 24/24 (including consumable drop/repick, mass/volume, container contention and disconnect integrity); final stress all six aggregate checks passed. Corrected settled reconnect repeats each passed 7 server + 5 client checks under emulation. All completed final regression editors shut down cleanly. Saved-map review passed 23/23 and the final build succeeded. All meaningful Gate 5 requirements passed; Gate 5 is ACCEPTED. Unreal is closed, all content is saved, and Gate 6 has not begun.
