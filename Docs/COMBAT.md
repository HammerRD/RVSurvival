# Combat foundation — Gate 9

Status: implementation and validation in progress; consult GATE_9_VALIDATION.md.

URVCombatComponent is an opt-in replicated Actor Component on the survivor. The
Gate9 survivor Blueprint enables it; accepted earlier test-map classes retain their
configuration. Inventory owns item state, presentation owns skeletal visuals, and
the medical component owns injuries and GAS vitality.

## Supported engine systems

Enhanced Input and the existing remapping registry handle 4 equip/holster, LMB
semiautomatic fire, RMB aim, R reload and U unload. Actor Component RPCs serialize
owned intents on the server. Native TimerManager revalidates delayed reloads.
Unreal PointDamage carries hit/bone information to injury application. Native
Animation Blueprint Blend Spaces, Epic pistol Aim Offset, DefaultSlot Montages,
SkeletalMesh PhysicsAsset queries and configurable bone anchors provide visuals.
No custom networking, movement or animation engine is introduced.

## Ammunition and ownership

Each magazine is one non-stackable FRVItemInstance with its own GUID, condition,
caliber definition, bounded rounds, CombatRevision and LoadedInWeapon GUID. A loaded
magazine remains a reserved real inventory record. Swapping preserves the old
magazine's remaining rounds. Holstering preserves the loaded relationship; U
unloads before inventory transfer/drop. A loaded weapon/magazine cannot be dropped
or transferred until unloaded. This initial prototype has no separately modeled
chamber. Cartridge mass is included in nominal magazine definition mass, not
recomputed per fired round. Typed fields are SaveGame-compatible; no full save or
offline persistence implementation is added.

Fire validates ownership, weapon identity/revision, action state, cadence and a
monotonic accepted request sequence before consuming one round. The server derives
its trace origin and view direction; clients do not submit hit targets. Invalid
requests cannot advance the accepted sequence and block later valid player input.
No lag compensation or rewind is implemented in this foundation.

## Damage and presentation

Player hits resolve six logical body regions through the replaceable humanoid
profile and native hit bones. An optional absolute-scale bone query preserves head
hits even when first-person owner presentation hides head rendering. Capsule
movement collision remains unchanged. Native point damage creates medical wound
records, bleeding/pain/contamination and modifies the existing GAS vitality.
Friendly fire is configurable on the combat component.

The project-authored primitive handgun mesh, generated sound and bounded transient
muzzle/impact effects are replaceable prototype assets. Unreliable cosmetic multicast
loss cannot replay damage or ammunition consumption. Animations use the free Epic
assets already installed with Unreal; no paid character/weapon assets are acquired.
Presentation and multiplayer acceptance remain subject to recorded tests.
