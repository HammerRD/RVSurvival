# Gate 5 post-playtest refinement — 2026-10-06

Status: IN PROGRESS. Gate 5 technical acceptance is retained as historical evidence; refinement acceptance requires new live tests. Gate 6 is not authorized.

User feedback: chase camera too close/low; interior trapping; invisible entry stairs; in-cabin seat switching; actual lower exterior compartments should hold primary general/bulky cargo, with pantry/medical/personal supplies inside. Preserve driving physics, vendor source and prior maps.

Recovery baseline: 0e7a2cb. Saved layout inspection is baseline-layout.json. Three entry boxes have no visible step art. Seven separate purchased compartment meshes are available. Baseline character capsule is 34 cm radius / 88 cm half-height; the cabin policy reduces radius to 30 cm. Root cause investigation and actual results follow.

Compiled and saved refinement foundation. Measured real stepwell center x=92.4 cm versus old collision x=122 cm; the full front-floor box incorrectly covered the recessed treads, and oversized Dinette collision reached x=95 instead of the approximately x=51 visible furniture edge. New collision splits the floor around the well, aligns the 75 cm doorway, uses the two real interior treads and one visible prototype exterior tread, and opens the house-door/glass project components. Native character capsule and moving-base policy are unchanged.

Single-player final route passed 17/17, including native walking entry/exit and front/rear return, clearance-checked door entry/exit, interior driver interaction, driver/passenger transfer, invalid-seat rejection, native V control and normal seat exit. A first run exposed the old cab-side exit position placing the survivor behind the open house door's sight line; fixed standing exit to search beside the house door using full outside capsule clearance. Build succeeded. Camera/compartment content is saved; separate-process and driving-camera validation remains pending.
