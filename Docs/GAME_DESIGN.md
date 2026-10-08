# Game design
RV Survival is a 1–5 player cooperative survival road trip across compressed regions of a collapsed United States. The RV is transportation and home. Travel → discover → assess risk → park → scavenge → survive → return → repair/organize → choose route → travel.

Every major system asks: can players keep the RV moving? Supplies have physical uses, risk is chosen, the world evolves independently, and stories emerge from interacting systems. No character levels, glowing rarity tiers, bullet-sponge progression, static-base focus, MMO, extraction or battle-royale redesign.

Current scope: Gates 1�4 are accepted (movement/interaction, RV driving/seats, purchased Class C moving interior/workstations and authoritative inventory/storage). Gate 5 survival needs are accepted after live validation; its acceptance status is recorded in GATE_5_VALIDATION.md. Gate 6 fuel/electrical is accepted after live validation; later systems remain unimplemented. Preserve the user design brief as the governing requirements.

## Gate 5 survival and long-term travel decisions

The RV is the central mobile survival base. Survival remains a core gameplay pillar, with nutrition, hydration and fatigue tuned for long-form road trips rather than minute-scale failure. Sleeping recovers fatigue while food and water continue to decline. Inventory ownership and the standing passenger reference frame remain the foundation for using survival supplies inside the RV.

Future geography combines authored regions with PCG/environment generation and procedural dressing, loot, encounters, population and weather variation. Launch progression is Western New York → Pennsylvania/Ohio → Midwest → Great Plains → Rockies → Los Angeles/Pacific Coast. Las Vegas, Grand Canyon, Arizona, Utah and other regions are expansion candidates.

Future travel uses seamless streamed regional transitions without traditional loading screens. Playable highway/transit corridors allow the next region to stream while the RV interior remains interactive. Party-cohesion streaming is planned when all active players are aboard. Eating, drinking, storage and appropriate rest/workstation use must remain available during transit. Gate 5 only preserves these architectural requirements; it does not implement streaming, generation or campaign geography.

## Gate 6 authorized scope (2026-10-06)
Fuel and electrical systems are the current gate: can the group keep the RV moving and livable? Driving/idle converts propulsion fuel into mobility and alternator energy; generator converts finite fuel into dependable house energy plus a future gameplay-noise signal; solar depends on available environmental input; conserving loads extends battery endurance. House and chassis power are distinct. Tuning remains provisional for long-form survival travel. The existing hybrid-region/seamless playable-transit decisions stand; Gate 6 implements no streaming, weather, AI, medical or mechanical failures. Preserve Gates 1-5 and stop after actual Gate 6 acceptance.

Gate 6 final status: ACCEPTED on 2026-10-06. Final resource, separate-process/emulated moving, stress, prior-gate regression and saved-asset evidence is in GATE_6_VALIDATION.md. Gate6FuelElectricalTest is saved with 65 actors/14 pickups; the copied inert can fixture was removed only from this map. Prior maps and all 108 vendor source files remain unchanged. Gate 7 is not authorized or implemented.

## Gate 6 manual layout refinement policy

Interior storage must match its visible furniture and player-facing identity. Overhead cabinets carry light household/food/personal/medical supplies; automotive fluids, heavy parts and bulky cargo remain in the existing exterior compartments. Dinette cushions are reusable passenger seating, with safe standing return to the aisle. Rear ladder climbing is currently a parked controlled-endpoint prototype; roof travel is not promised until safe supporting collision is validated. Production climbing/sitting/sleep animations can replace the prototype presentation without replacing authority or movement systems.
Second Gate6 refinement: use the real dinette cushions for reusable sitting; the rear mattress for a replaceable horizontal rest pose; and real cabinet surfaces for lightweight interior supplies. Use the existing cab radio and switch bank for navigation/power interaction. Rear ladder is a parked prototype with a controlled endpoint, not roof traversal. No new survival, crafting, regional or Gate7 gameplay is included.

## Gate 6 second refinement closure (2026-10-07)
Purchased physical table/stove/sink/bathroom upper cabinet/bed-foot wardrobe now determine interaction roles. Light pantry/dry food/personal/medical/small-tool supplies use real interior and overhead cabinets;heavy/bulky cargo remains in seven exterior compartments. Normal-play targets are hidden so players interact with visible RV objects.
Two real dinette cushions support authoritative sitting. Rear bed has a visible replaceable lying prototype and Z/R/E controls;stations allow walking away without input/camera locks. Ladder provides a safe parked controlled endpoint, not roof access. V seat-to-seat and beds require stopping;passenger3-to-living remains moving-compatible. These limits are explicit. Gate6 remains ACCEPTED after real-input/live visual and separate-process tests. RV remains the central mobile survival base. Gate7 is not authorized or started.
## Gate 7 deterministic mechanical survival loop
The mobile base now supports causal cooling failures: radiator damage -> slow/severe leak/reduced cooling -> heat warnings -> limp output -> prolonged overheating engine damage/shutdown -> stop/inspect -> tagged tools/parts/coolant -> temporary roadside patch or replacement -> resume travel. Independent subsystem states replace a generic universal vehicle-health concept. No arbitrary random breakdown spam, skills/crafting or later mechanical subsystems. Normal rates are tuneable for road-trip play; accelerated development profiles are separate. Repair stock belongs in exterior service cargo; living interior remains usable and survival/inventory keep updating during travel. Gate8 is not started.

## Gate 6 physical-entry, seating and roof refinement - 2026-10-07

Dinette seating/dining is distinct from lying/rest/sleep; only the real rear bed currently recovers fatigue through rest. The open side door is primarily a physical walk-in/walk-out route with visible steps. Cab-to-living transition is a remappable intentional action: passengers may stand in the moving mobile base; drivers must stop first. Normal seat interaction returns standing passengers to available cab/rear seating.

The real rear ladder now targets parked roof access using collision at the purchased roof surface and fitted fixtures. Propulsion is locked while climbing or standing on the roof. No moving roof traversal or final climbing animation is promised. The RV remains the central mobile survival base; inventory, survival, fuel/electrical and the accepted interior reference frame are preserved. Current refinement is NOT ACCEPTED pending complete manual hold-route coverage and unresolved transition-smoothness assessment; no subsequent-gate work is authorized by these changes.

## Gate7 resumed integration - 2026-10-07
The user accepted Gate6 physical-entry/roof/seating after successful manual playtest on 2026-10-07 and authorized Gate7 only. The existing deterministic cooling/repair loop is being revalidated against that mobile-base layout. Gate8 remains unauthorized; no additional mechanical subsystems, combat, world generation or streaming are introduced.

Resumed Gate7 closure: ACCEPTED after fresh mechanical/both-role impaired network, stress and Gates1–6 representative regressions; see GATE_7_VALIDATION.md for exact scope/evidence/failed history. Saved physical-entry/roof layout retained,108vendor hashes unchanged. Refrigerator collision remains a nonblocking measured-layout follow-up. Full persistence/later systems remain unimplemented; no Gate8.

## Gate 8 medical prototype
Medical needs reinforce the RV as the mobile survival base: stabilize injuries using carried/linked supplies, support teammates, and preserve injury consequences after revive. Splints/bandages stabilize; medicine temporarily reduces pain. Advanced station treatment is parked-only; basic treatment supports transit. No combat, full disease/surgery, dependency or permanent-character replacement implementation. See MEDICAL.md for current prototype rules.
