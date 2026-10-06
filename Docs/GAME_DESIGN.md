# Game design
RV Survival is a 1–5 player cooperative survival road trip across compressed regions of a collapsed United States. The RV is transportation and home. Travel → discover → assess risk → park → scavenge → survive → return → repair/organize → choose route → travel.

Every major system asks: can players keep the RV moving? Supplies have physical uses, risk is chosen, the world evolves independently, and stories emerge from interacting systems. No character levels, glowing rarity tiers, bullet-sponge progression, static-base focus, MMO, extraction or battle-royale redesign.

Current scope: Gates 1�4 are accepted (movement/interaction, RV driving/seats, purchased Class C moving interior/workstations and authoritative inventory/storage). Gate 5 survival needs are accepted after live validation; its acceptance status is recorded in GATE_5_VALIDATION.md. Gate 6 fuel/electrical implementation is in validation; later systems remain unimplemented. Preserve the user design brief as the governing requirements.

## Gate 5 survival and long-term travel decisions

The RV is the central mobile survival base. Survival remains a core gameplay pillar, with nutrition, hydration and fatigue tuned for long-form road trips rather than minute-scale failure. Sleeping recovers fatigue while food and water continue to decline. Inventory ownership and the standing passenger reference frame remain the foundation for using survival supplies inside the RV.

Future geography combines authored regions with PCG/environment generation and procedural dressing, loot, encounters, population and weather variation. Launch progression is Western New York → Pennsylvania/Ohio → Midwest → Great Plains → Rockies → Los Angeles/Pacific Coast. Las Vegas, Grand Canyon, Arizona, Utah and other regions are expansion candidates.

Future travel uses seamless streamed regional transitions without traditional loading screens. Playable highway/transit corridors allow the next region to stream while the RV interior remains interactive. Party-cohesion streaming is planned when all active players are aboard. Eating, drinking, storage and appropriate rest/workstation use must remain available during transit. Gate 5 only preserves these architectural requirements; it does not implement streaming, generation or campaign geography.

## Gate 6 authorized scope (2026-10-06)
Fuel and electrical systems are the current gate: can the group keep the RV moving and livable? Driving/idle converts propulsion fuel into mobility and alternator energy; generator converts finite fuel into dependable house energy plus a future gameplay-noise signal; solar depends on available environmental input; conserving loads extends battery endurance. House and chassis power are distinct. Tuning remains provisional for long-form survival travel. The existing hybrid-region/seamless playable-transit decisions stand; Gate 6 implements no streaming, weather, AI, medical or mechanical failures. Preserve Gates 1-5 and stop after actual Gate 6 acceptance.
