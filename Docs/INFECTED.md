# Infected foundation — Gate 9

Status: implementation and validation in progress; see GATE_9_VALIDATION.md.

ARVInfected is a server-driven Character with native CharacterMovement replication.
URVInfectedProfile is a replaceable Primary Data Asset for humanoid mesh/material,
animation class, body-region mapping, perception, movement, attacks and durability.
The free Epic mannequin with a project-side green material distinguishes the
prototype infected. Final infected art and animations are not required by this gate.

ARVInfectedController uses AI Perception sight/hearing, native NavigationSystem and
path following. A small native Behavior Tree runs one RV-specific task at engine
intervals. This avoids a second custom scheduler or perception/navigation system.
A Blackboard or asset-authored subtrees can be added when variants require them;
there is no competing StateTree brain. Current policy covers wandering, investigation,
sight acquisition, chase, melee windup and death. Gunshot noise is reported through
native Hearing; other noise sources may use the same API later.

Attack completion independently rechecks active victim, range and Visibility line
of sight. Windup/cooldown use native timers; death clears pending attack, stops brain
and movement, changes controlled lying presentation and cannot deal later damage.
Native PointDamage reuses survivor medical injury handling. Head/limb multipliers
and leg movement impairment are configurable. No networked ragdoll, loot director,
horde population, human AI or regional spawning is implemented.

Navigation in the new Gate9 map is authored on a Static driving ground with a
saved NavMesh. Editor generation waits for native asynchronous load locks to clear;
it never suppresses navigation locks or world-leak checks. Prior accepted maps are
preserved. Prototype attacks use controlled presentation rather than final claw/bite
animation assets. Full hearing/obstruction/aggro stress and multiplayer results must
be verified before acceptance.
