# Gate 8 medical validation

Status: **IN PROGRESS — NOT ACCEPTED**. Authorized 2026-10-08. Gate 9 is not started.

## Baseline and recovery

Accepted Gate 7 baseline: `0b6eff6`. Pre-existing unrelated working-tree changes are `Config/DefaultEngine.ini`, `.vsconfig`, `Automation_RVSurvival.slnx`, and `RVSurvival.slnx`; these are excluded from Gate 8 checkpoints. Preserve all 108 vendor packages and prior maps. Refrigerator collision remains deferred unless directly relevant to medical placement.

## Framework review

Gate 8 uses Epic GameplayAbilities for replicated medical attributes and timed medication effects. An additive PlayerState-owned AbilitySystemComponent and AttributeSet leave accepted needs, inventory, seats, and native CharacterMovement prediction intact. Persistent PlayerState ownership is appropriate when the player possesses the RV; passive medical effects target PlayerState rather than assigning injuries to the vehicle pawn.

Injury identity, body region, wound treatment rules, resource requirements, and patient eligibility are RVSurvival gameplay. Reflected GUID-backed injury records and Primary Data Assets represent these rules. GAS owns attribute replication and medication duration/aggregation. Native component replication/RepNotifies, owned RPCs, TimerManager, Enhanced Input and UMG remain the engine mechanisms for interaction and presentation. CommonUI and Lyra experience/game-feature infrastructure are unnecessary for this focused gate. No parallel inventory or custom networking framework is planned.

Primary sources reviewed:

- [Epic GAS overview](https://dev.epicgames.com/documentation/en-us/unreal-engine/understanding-the-unreal-engine-gameplay-ability-system)
- [Epic Lyra PlayerState ability ownership](https://dev.epicgames.com/documentation/unreal-engine/abilities-in-lyra-in-unreal-engine?lang=en-US)
- [Epic attribute/ASC integration](https://dev.epicgames.com/documentation/unreal-engine/gameplay-ability-system-component-and-gameplay-attributes-in-unreal-engine?lang=en-US)

## Implementation progress

Initial foundation: GameplayAbilities plugin/module dependencies, persistent ASC, replicated Blood/Vitality/Analgesia attributes, serializable injury/body-region types, configurable medical profile and existing-item medical capability metadata. This is a foundation only; treatment, injury simulation, medical station, UI, downed/revive and runtime validation remain unfinished.

## Validation policy

Compile and exercise changed medical features first. PlayerState additions require targeted possession/state replication checks; speed/downed policy will require targeted native moving-interior checks. Inventory consumption must reuse accepted serial transactions and validate GUID/revision/ownership at completion. One representative Gates 1–7 pass, vendor/saved-content audit, separate-process medical matrix with 100 ms/2% loss, final build and clean shutdown are required for acceptance. Do not count compile success as gameplay validation.

At the initial architecture review, runtime validation and map creation were pending. Subsequent progress is recorded below.

## Foundation checkpoint — 2026-10-08
Development Editor/Win64 builds passed (21.29 s foundation, 19.56 s medication). Initial C++ replication macro parameter naming failed, then was corrected. Focused live PIE component diagnostic passes 21 checks: authoritative moderate blood loss, GUID-backed wound, existing inventory admission, one-item bandaging, stopped bleeding with retained injury, stale revision rejection, fracture scale query, pain/burn/concussion state, clamping/downed/reset. This is NOT normal-player or multiplayer acceptance. Three Python fixture failures (reflected attribute accessor, default-only temporary Data Asset editing, out-parameter return assumption) were corrected; failed receipts/logs remain under Saved/Gate8Validation. PIE stopped and editor shutdown completed cleanly without fatal/world-leak/Python errors in the final run. All 108 vendor hashes match. No prior maps changed. Treatment UI, station support, movement/action restrictions, multiplayer/revive/medication duration tests and final regressions remain pending.


## Station/UI implementation checkpoint (pending validation)
Gate8MedicalTest saved with nine medical pickups, a functional station at the accepted runtime station-definition position, linked existing Medical storage, normal medical profile and Gate8-only PlayerState/GameMode derivatives. Prior layouts/vendor meshes are unchanged. F9 uses the existing remappable Enhanced Input catalog. UMG offers self/nearby teammate, injury/supply selection, treatment/cancel/close, with qualitative symptoms and HUD urgency warnings.
Downed guard changes touch speed-query policy, input eligibility, interaction, inventory request authority and seat/controller requests. No native solver, prediction, base or transport is replaced. Targeted Gate3 moving and Gate4/7 resource regressions are now required by the risk policy. Treatment interruption uses passenger-frame-local anchors so vehicle translation itself is not cancellation; moving away over50cm or changing frame cancels before consumption.
Setup failures retained: workstation editor-actor assumption, unavailable Python get_root_component (use exposed Mesh), reflected boolean sampler accessor. Saved map setup recovered in place; references released and editor exited cleanly. First-header ordering diagnostics were corrected although UBT still reported build success. Current build success20.16s plus medical warning build18.37s. UI/multiplayer/advanced medical behavior is not accepted yet.


## Normal-player medical panel observation
An initial injury/supply fixture was seeded, then the native window received F9 and visible UMG button clicks. The player completed a normal four-second bandage: active bleeding cleared, injury remained stabilized rather than erased, Bandage quantity changed from three to two, and the HUD changed to the leg-mobility warning. Next-injury selection visibly displayed the left-leg fracture. Fracture treatment, medication, cancellation, teammate treatment and network acceptance remain pending. The first sampler encoded GUIDs as Python struct display strings; these are not GUID-conservation evidence. Future sampling uses GuidLibrary string conversion. Preserved samples: Gate8Results/manual-ui-bandage-samples.json. Managed PIE stop and editor shutdown completed cleanly. Treatment guards reject invalid GUIDs/non-finite supply tuning and require bleeding control before revive. Development Editor build passed in 5.85 seconds.

Focused treatment transaction diagnostic passed all 16 targeted cases: cancel retains supply and leaves fracture untreated; completed splint consumes once, preserves fracture and uses configured 0.65 mobility; GAS analgesia applies without erasing injury; burn dressing and antiseptic consume once and update treatment/risk; condition and GUID survive; invalid GUID consumes nothing. The initial Python GUID wrapper comparison failed and is retained separately. Final PIE/editor shutdown clean. This diagnostic does not replace normal UI or multiplayer acceptance. Medication expiry and concurrent/teammate cases remain pending.
