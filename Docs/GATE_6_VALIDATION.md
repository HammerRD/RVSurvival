# Gate 6 fuel and electrical validation

Status: IN PROGRESS. Gate 5 accepted; Gate 7 is not authorized.
Baseline recovery checkpoint: 8e80050. Pre-existing Config/DefaultEngine.ini and IDE files remain outside Gate 6 commits.

## Framework review (2026-10-06)
Use native replicated ActorComponents/default subobjects for fuel, batteries and power bus; Primary Data Assets for immutable tuning; Gameplay Tags for fuel compatibility; Unreal RepNotifies/delegates, owned controller reliable RPCs and TimerManager weak dispatch for intent. Inventory remains the accepted FastArray system. CharacterMovement and Chaos server simulation stay intact. Supported Chaos SetMaxEngineTorque gates propulsion without changing suspension/transmission tuning. No custom replication transport, timer scheduler, movement solver, or generalized effects framework.

Reviewed installed UE 5.8 headers and Epic documentation:
- [Replicated Actor Components](https://dev.epicgames.com/documentation/unreal-engine/replicating-actor-components-in-unreal-engine?lang=en-US)
- [Gameplay timers](https://dev.epicgames.com/documentation/en-us/unreal-engine/gameplay-timers-in-unreal-engine)
- [Data Assets](https://dev.epicgames.com/documentation/en-us/unreal-engine/data-assets-in-unreal-engine)

GAS is not needed for slow machine resource balances and switching: no abilities or stacked medical effects are being introduced. Lyra's component/data-driven separation is relevant; importing its experiences/game features is unnecessary. Existing UMG needs HUD and Canvas inventory remain; the prototype power panel extends readable presentation, with no duplicate UI-owned state. Reflected scalar structs/IDs prepare SaveGame; full persistence is deferred.

## Plan and units
Fuel in litres, energy in watt-hours, rates in litres/hour and watts, simulation seconds converted centrally to hours. Dedicated Gate 6 vehicle/content derivative preserves prior maps and vendor sources. Main propulsion fuel and optional separate generator source; independent house/chassis battery components; one configurable priority bus supplies reusable domain-tagged loads before charging batteries. Fuel-can state lives on accepted runtime item records, never in a second item actor inventory.

No validation is claimed yet. Actual build, PIE, separate-process, network, stress and regression receipts will be recorded as executed.
## First live milestone — 2026-10-06
Compiled foundation 6369b4e; saved new map/content 92d3699. Corrected compiler include-order/const access; corrected Python SaveMap/setter/boolean accessor APIs and resumed existing map in place after an overwrite message. No editor/world leak crash occurred. Smaller 10 L can has 12 L prototype volume / 6 kg, preserving 25 kg/35 L player limits; original Gate 4 definition remains inert and unchanged.

Live single-player PIE: 46/46 passed (single-foundation.json), including idle/load/road rates, clamp/nonfinite checks, native pickup/refuel, 195-to-200 L tank partial transfer leaving 15 L, stale revision rejection, GUID/condition/drop/repick/exterior storage, partial/empty/incompatible cans, generator fuel/charging/reserve stop/noise, solar/alternator/shore input, loads/depletion, panel stale/invalid requests, accelerated 24 h bounds and actual Chaos propulsion. Empty-tank W moved 0.65 cm; refilled W moved 3909 cm in four seconds and burned fuel. These are executed technical input tests, not final multiplayer acceptance. Network/moving/regression work remains pending.
Separate-process resource milestone: final 31 server / 29 client checks pass, distinct process IDs. Fuel total conserved under two-client native pickup/refuel/repick/shared-container contention; client debug mutations rejected; stale controls and invalid request burst rejected; shared generator survives client disconnect and host can stop it afterward. Keyboard input samples revealed that two simultaneous toggle presses legitimately produced two serialized changes (off then on); corrected test verifies host/client presses separately while retaining explicit same-revision contention. New panel keys moved to native Enhanced Input Started bindings on the controller, keeping presentation separate and preventing render-dependent control polling. Remaining network emulation, moving matrix, stress/regressions not yet accepted.
