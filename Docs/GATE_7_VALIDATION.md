# Gate 7 mechanical failure and repair validation

Status: IN PROGRESS / NOT ACCEPTED. Authorized 2026-10-07; Gate 8 is excluded. Accepted Gate 6 recovery: 2ef5b83. Pre-existing Config/DefaultEngine.ini and three IDE files remain excluded.

## Framework review
Use replicated native Actor Components for machine state, Primary Data Assets for tuning/repair requirements, Gameplay Tags for fluid/tool/part/fault identity, normal owned-controller RPCs/RepNotifies and Unreal TimerManager for repair lifecycle. Reuse accepted lightweight FastArray item records and revisioned container-fluid fields rather than an independent coolant inventory. Native Chaos torque scaling composes fuel and mechanical limits. CharacterMovement, seats, moving interior and existing physics remain intact.

Epic sources reviewed: [Actor component replication](https://dev.epicgames.com/documentation/unreal-engine/replicating-actor-components-in-unreal-engine), [Gameplay Tags](https://dev.epicgames.com/documentation/unreal-engine/using-gameplay-tags-in-unreal-engine), [Data Assets](https://dev.epicgames.com/documentation/unreal-engine/data-assets-in-unreal-engine). Installed UE 5.8 TimerManager and ChaosWheeledVehicleMovementComponent headers are authoritative API references. GAS/CommonUI/Lyra experiences are not justified for slow machine balances or this bounded service panel; no custom transport/timer/effect framework is introduced. UMG presentation will read authoritative state, separate from rules.

## Planned composition and units
Gate7 opt-in ARVMechanicalMotorhome derivative preserves all earlier maps/Blueprints. Separate engine-condition and cooling records, coolant litres, temperature Celsius, condition 0-1, leak litres/second, heat degrees/second. Data-driven profiles provide normal tuning; development time acceleration is opt-in/nonshipping. Causal leak/cooling/heat/damage chain; no universal RV health/random breakdowns. Temperature approaches a bounded ambient/load-dependent balance; shutdown removes combustion heat while residual heat cools.

Temporary patch and full radiator replacement use tagged tool/consumable requirements, timed exclusive authority reservation, completion-time revalidation and atomic inventory consumption. Inspect/refill/service range and LOS must remain clear and vehicle stopped; hot/running refill is rejected. Debug controls are development-only. Future persisted scalar state and asset/tag IDs must not rely on service Actor pointers.

## Required validation
No build, PIE, multiplayer, stress or regression pass is claimed yet. Required user matrix remains governing acceptance, including both roles, separate processes, 100ms/2% loss, roadside recovery, item conservation, normal user input, moving diagnostics, Gate1-6 regressions, saved map/assets and clean shutdown.

## Recovery
Read current documentation/source and verified unrelated working-tree changes before implementation. All 108 vendor files and prior maps must remain unchanged. Save/checkpoint after each stable milestone. No Gate8 work.

## Compiled/saved foundation milestone
Compiled native cooling/engine condition, revisioned service endpoint, atomic tagged repair requirements and UMG engine/service display. Builds foundation52.44s, service19.29s, UI17.20s and checkpoint17.76s succeeded; installed Incredibuild license warning falls back to standalone and is not a compile failure. Engine torque/fuel composition uses default scale1 for accepted prior vehicles.

Saved separate Gate7MechanicalTest (77 actors), BP_ClassCMechanicalMotorhome, DA_NormalMechanical and seven item definitions: mechanic tool kit, radiator patch, radiator replacement, recoverable engine service, 5L full/1.75L partial/empty coolant. Coolant reuses legacy-named Fuel metadata/instance litres/revision with Resource.Fluid.Coolant tag; gasoline/diesel compatibility remains exact and never treats coolant as fuel. Record identity, quantity, condition and transfer/drop behavior remain the existing inventory system. Normal tuning:12L capacity,20C ambient,.25C/s idle plus1C/s load heat, bounded exponential cooling, .001/.015L/s minor/major leaks,95/105/115/130C thresholds. Service requires parked/off/cool<=60C. B patch8s,N radiator15s,M engine20s;E opens inspection,F selected owned coolant refills,Escape closes/cancels. Engine repair does not silently repair the radiator or erase a temporary patch.

Recovery commits65a2d08 (accepted baseline/framework plan),15622e7 (compiled foundation). Map/assets saved before/after configuration. All108 vendor hashes match. First live tests are running; no acceptance is claimed from compilation/content setup.
