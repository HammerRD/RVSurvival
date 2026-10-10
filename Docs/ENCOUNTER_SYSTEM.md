# Gate 10 encounter foundation (in progress)

Native WorldSubsystem session state and native Actor timers schedule only small,
authored contextual zones. A Primary Data Asset weights Quiet, Infected Cluster,
and Supply Cache outcomes. Context uses Gameplay Tags; spawn anchors are authored,
not a custom procedural world generator. Profile choices must include positive
quiet weight. A global non-quiet cooldown and reduced weight for the immediately
previous outcome avoid constant repeated action.

Only the server selects outcomes or spawns gameplay. Selected outcomes remain
stable for the session. Native replication carries relevant zone outcome and AI
state; clients never create supplies or damage targets locally. Existing infected
Character/AIController, Behavior Tree, AI Perception and Recast navigation remain
unchanged. Population difficulty sets initial finite group count (maximum six per
zone); a global active cap defaults to twelve (hard maximum sixteen). Difficulty
changes do not reroll already visited/depleted zones.

Spawn attempts require a projected navigation floor, capsule clearance, minimum
player separation and no unobstructed forward player view. Unsafe candidates wait,
rather than popping into view. Far-away populations suspend into value-only
snapshots of health, position, limb injury and death. Native timers are cleared on
EndPlay; actors are weak references, not retained world/level pointers. A chasing
member close to any player keeps its zone engaged. Authored small director anchors
are non-spatial; geometry and gameplay containers remain spatially streamed.

This is not the final Encounter Director. No weather/time simulation, hordes,
migration, human AI, campaign saving or cross-region travel. Runtime validation,
visual pop-in checks, navigation, cooldown/quiet outcomes and multiplayer are
pending; compilation alone is not acceptance.
