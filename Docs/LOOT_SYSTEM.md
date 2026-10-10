# Contextual finite supplies

Gate 10 foundation, currently unvalidated in a playable world.

URVLootProfile is a Primary Data Asset with a context Gameplay Tag, regional
abundance and entries referencing accepted URVItemDefinition assets. Entries have
chance, quantity and condition ranges. Host-owned Loot multiplier feeds generation;
no preset-name branches or alternate inventory system.

ARVScavengeContainer is an opt-in ARVStoragePoint. Its authored ContainerId must be
unique and valid. Missing/duplicate identity refuses generation. Authority chooses
initial supplies once and adds them using accepted capacity/identity transactions.
It replicates searched state and normal FastArray contents with distance relevance.

URVRegionStateSubsystem retains generated/searched state and remaining item records
for the current world session. EndPlay records remaining contents; recreation uses
the same GUID to restore them rather than generating again. Empty/depleted results
remain generated. Weak active claims prevent two loaded actors sharing an identity.
No MMO refill, arbitrary loot respawn or disk campaign save is implemented.

Future persistence must serialize authored container ID, searched/generated flags,
definition asset identity, GUID/quantity/condition/custom state and fuel/magazine
fields. Dropped world items additionally need a stable world location record; the
accepted free-standing pickup Actor is not itself a complete campaign save format.

Generation ranges, empty outcomes, capacity rejection, repeated claims, unloading,
world teardown, host/client convergence and user-facing search/transfer still require
runtime tests. Lifecycle diagnostic results do not substitute for actual streamed
cell traversal or normal E/container controls.
