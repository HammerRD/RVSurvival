# Gate 5 — core survival needs validation

Status: IN PROGRESS / NOT ACCEPTED. Gate 4 was accepted by the user; Gate 6 has not begun.

## Foundation checkpoint

PlayerState owns URVNeedsComponent so driver possession does not replace survival state. Nutrition, hydration, fatigue, minimal survival reserve, simulation time and rest mode replicate from the server. URVNeedsProfile provides tunable Data Asset values; defaults use hours rather than minutes. Walking, heavy carrying, driving, passenger, rest and sleep metabolism are separate inputs. Critical needs reduce movement speed through GetMaxSpeed without rewriting CharacterMovement prediction or the accepted moving-base solver. Survival reserve is a minimal replaceable consequence, clamped above zero; no injury or death system is implemented.

Item definitions now contain FRVConsumableMetadata. Consumption uses an owned inventory GUID, validates metadata and benefit, removes exactly one item on the server game thread, then applies clamped recovery. Remaining stack identity, condition and custom state remain unchanged. A real-time cooldown is independent of accelerated needs simulation. Clients send intent only. Editor automation dispatches requests through weak native next-tick delegates to avoid the previously diagnosed editor script RPC callspace guard.

ARVRestPoint reserves one occupant and uses ordinary CharacterMovement at the character's current position. No sleep animation or cosmetic attachment is used. Rest/sleep requires a parked platform and ends when it moves or the reservation becomes invalid. Disconnect and teardown release reservations. Sleep reduces fatigue while continuing nutrition/hydration drain.

Developer controls require server authority, a non-shipping build and rv.Needs.AllowDebug=1. Their time scale does not change Chaos physics or interaction timers.

## Build / failures

Initial UnrealHeaderTool failure: URVNeedsTuning and FRVNeedsTuning shared a reflected engine name. The Data Asset class was renamed URVNeedsProfile. The next Development Editor / Win64 build succeeded. A new deprecated NetUpdateFrequency assignment was replaced with SetNetUpdateFrequency before further validation.

## Remaining validation

Content/map setup, usable UI verification, single-player and separate-process multiplayer, latency/loss, realistic accelerated stress, rest/disconnect cleanup, moving-RV eating/drinking/pantry, Gates 1–4 regressions and final startup/shutdown are pending. Compilation is not acceptance.

## Recovery discipline

Foundation source saved before editor work. Accepted maps and purchased vendor content remain untouched. Existing unrelated Config/DefaultEngine.ini and IDE files will not be staged. Stable milestone commits will be recorded here as work progresses.

## Unreal framework review (user course correction)

Reviewed current source plus installed UE 5.8 GameplayAbilities AttributeSet.h/AbilitySystemComponent.h, GameplayTags library and Epic's official GAS/Lyra/CommonUI guidance before further major implementation.

RVSurvival-specific rules: hour-based metabolic drain/recovery, activity classification, threshold severity, owned-item transaction validation, rest reservation/parked policy and future persistence fields. These belong in project gameplay code.

Engine services reused: ActorComponent lifetime/tick; PlayerState ownership across possession; Primary Data Assets for tuning/catalog; Gameplay Tags for classification/status; native UPROPERTY replication/RepNotify and owned reliable RPCs; weak TimerManager dispatch; accepted Enhanced Input and CharacterMovement prediction/based movement; UMG for the new needs display; existing FastArray inventory. No custom transport, scheduler, prediction, general effect stack or UI framework is being created.

Decision: do not introduce GAS during this gate. Three slowly changing scalar needs, a single exclusive rest mode and derived threshold consequences do not currently need predicted abilities, duration stacking, cancellation graphs or effect aggregation. GAS would require new avatar initialization across character/vehicle possession and a migration of state without a demonstrated Gate 5 benefit. This is not a blanket rejection: before implementing injuries/bleeding/medication or timed/stacking buffs, evaluate an ASC on PlayerState with AttributeSets and GameplayEffects rather than inventing a custom effect system. The needs API and item metadata isolate the eventual integration boundary. Do not add a parallel replicated attribute store now.

UMG is appropriate for the added restrained survival readout. CommonUI's layered menus/device-routing framework is deferred until the product needs those features; replacing accepted Gate 4 controls now has no demonstrated benefit. Serialization uses reflected value structs; SaveGame flags will identify relevant values, but no save system/offline progression is implemented.

Sources:
- https://dev.epicgames.com/documentation/en-us/unreal-engine/understanding-the-unreal-engine-gameplay-ability-system
- https://dev.epicgames.com/documentation/en-us/unreal-engine/gameplay-ability-system-component-and-gameplay-attributes-in-unreal-engine
- https://dev.epicgames.com/documentation/en-us/unreal-engine/abilities-in-lyra-in-unreal-engine

Content setup encountered a Python read-only GameplayTagContainer property error, not a crash. The partially completed Gate 5 map was immediately saved through Editor Save All (All Saved verified). Repair will use the official GameplayTags Blueprint library API and in-place configuration, without recreating the map or its existing rest markers.

## Live validation progress

Single-player corrected run: 27/27 passed, including actual hold-interaction pickups, owned consumption, stack/last-item/stale-GUID handling, condition/custom-state preservation, exclusive rest entry, sleep recovery with continued metabolism, movement restriction/wake cleanup, status tags/warnings, consequences and 24-hour-equivalent clamping. Initial harness errors (live struct alias and non-exported Python movement getter) were repaired; initial evidence retained.

First independent moving host/client run retained the complete accepted Gate 3 movement/workstation route and Gate 4 storage/drop route. Stationary and highway food consumption and turning food consumption passed. A fixed hydration target incorrectly omitted ~0.67 points of genuine drain accumulated over the route. The check now records pre-consumption values and verifies configured gain plus ongoing normal metabolism; no gameplay acceptance limits changed. Paired inventory/container/status receipts matched; maximum independently sampled passenger-local discrepancy was 10.51 cm. The run is not counted accepted until repeated with corrected expectation.

First separate-process survival transaction/rest run passed 11 server and 12 client gameplay checks. Python cleanup cleared the active callback module, but its caller then continued reading cleared globals (NameError after disconnect). The runner now returns immediately after teardown. No crash or leak occurred; a clean repeat is required before counting this sequence complete.

Source review improvements queued for the next closed-editor build: UMG now binds native needs notifications and removes its delegate on widget destruction; HUD teardown removes the widget. Persistent value copies are no longer overwritten by subsequent BeginPlay initialization. Awake fatigue rates clamp nonnegative. Float font-color literals remove a compiler warning.

Visual inspection found the survival widget positioned above the viewport: installed UE 5.8 UGameViewportSubsystem::SetWidgetSlotPosition explicitly resets anchors to top-left. The new HUD calls position before bottom anchoring/alignment; this is a supported API ordering fix, to be verified visually after rebuilding.

Stress fixture's initial hold missed its cupboard after the elevated pawn settled on the floor. It now reacquires the aim immediately before pressing E, as the accepted Gate 4 harness did. No interaction range/LOS/collision rule was relaxed.

Stress run passed: 200 successful owned consumption operations with 200 unique GUIDs, 100 actual shared-container withdrawals, 20 hold-E rest/sleep/wake cycles, and 86,404.89 simulated seconds through accelerated real component ticks. No remaining inventory records, rest reservations or extra pickup actors. End values clamped (nutrition 0, hydration 0, fatigue 100; reserve 1.825). Editor shut down cleanly. This is accelerated engineering validation, not a claim of a real-time 24-hour session.

Rebuilt event-driven UMG lifetime, anchor ordering and persistent-copy fixes successfully with no new warnings in build-ui-lifetime.log. Final live testing remains pending on this rebuilt binary.
