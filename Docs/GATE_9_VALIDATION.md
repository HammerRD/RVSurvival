# Gate 9 — basic combat and infected foundation

Status: IN PROGRESS. Gate 8.5 baseline: 3256c27. Gate 10 is excluded.

## Framework review

Use existing Actor Components, Primary Data Assets, Gameplay Tags, Enhanced Input,
CharacterMovement, native RPC/property replication and the accepted GAS medical
attributes. No replacement movement, inventory, networking or animation engine.
Magazine rounds are per-instance inventory data, not an abstract reserve pool.
Player damage extends the medical injury transaction and GAS vital attributes;
it must not introduce parallel player health.

Infected use AIController, AI Perception sight/hearing and NavigationSystem native
path following. Behavior Tree/Blackboard are preferred for inspectable behavior;
StateTree is an alternative supported framework, not a second simultaneous brain.
Native timers handle attack/reload completion with authority revalidation. Animation
Montages/slots support presentation independently of authoritative hit timing.
The existing replaceable humanoid profile remains the body-region boundary.

Official framework references reviewed:
- [AI Perception](https://dev.epicgames.com/documentation/unreal-engine/ai-perception-in-unreal-engine?lang=en-US)
- [Behavior Tree overview](https://dev.epicgames.com/documentation/en-us/unreal-engine/behavior-tree-in-unreal-engine---overview)
- [Animation Montages](https://dev.epicgames.com/documentation/en-us/unreal-engine/animation-montage-in-unreal-engine)

## Recovery and scope

Initial working tree contains unrelated Config/DefaultEngine.ini, .vsconfig,
Automation_RVSurvival.slnx and RVSurvival.slnx changes. Exclude them from Gate 9
commits. Preserve prior maps and all 108 Content/RV vendor files against 0b6eff6.
Editor is closed at the accepted saved baseline. Refrigerator collision remains
deferred. No Gate 9 build, runtime or visual acceptance is claimed yet.

## Validation pending

Firearm/magazine transactions; real remappable input paths and visible presentation;
six-region medical damage; native AI perception/navigation/attack/death; separate
process host/client and representative 100 ms/2% loss; meaningful stress; one final
risk-based prior-gate regression; saved asset/vendor audit; build and clean shutdown.
