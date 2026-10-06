# Inventory foundation — Gate 4

Gate 4 is accepted; actual logistics validation is recorded in GATE_4_VALIDATION.md. Gate 5 adds metadata-driven food/water consumption and is accepted with results recorded separately below. Medicine, crafting, combat and fuel effects remain unimplemented.

## Definitions and instances

URVItemDefinition is a Primary Data Asset. CatalogId is a stable catalog identifier; display name and description are presentation. Definitions provide category/gameplay/crafting tags, optional mesh/icon references, kg and litres per unit, stack configuration, condition support, equipment eligibility and physical-carry requirements. Gameplay behavior does not dispatch on display-name strings. Native registered tags classify the inert prototype definitions.

FRVItemInstance stores GUID, definition asset reference, quantity, normalized condition, location identifier and key/value custom-state entries. Stored records contain no world Actor reference. Each non-stackable item has quantity one; a stack is one identified record with compatible shared instance state and a bounded quantity. Full transfers preserve its GUID. Partial transfers retain the source GUID and assign a new GUID to the separated portion. Compatible stacks are not automatically merged in this prototype; capacity is physical mass/volume, not a slot count.

These reflected records can later serialize with catalog/asset identity and GUIDs. Transport bookkeeping is reset when a record enters another FastArray. Full persistence, reconnect recovery, death inventory and save-game migration are not implemented.

## Storage and authority

URVInventoryComponent tracks player contents; URVContainerComponent reuses its rules for cabinets and other storage. Player defaults: 25 kg / 35 L. RV cabinets use 100 kg / 60 L; external storage uses 100 kg / 120 L. Capacities, names and allowed-tag filters are configurable and replicated. Definition and instance values are validated before admission. No item is removed from its source unless its destination accepts it.

Transactions run serially on the authoritative server game thread. Clients submit GUID, quantity and direction, not an item definition or arbitrary instance payload. Every mutation checks authority; transfers revalidate the selected container, 300 cm reach and Visibility line of sight. Stale IDs, unavailable quantities and capacity failures preserve the source. Client UI uses returned record copies and owns no gameplay state.

Local RequestTransfer/RequestDrop/RequestCloseContainer intents dispatch on the next native game tick using weak delegates, then invoke owned reliable RPCs. This avoids editor Python execution guards forcing RPC implementations to run locally. Requests recheck local control after possession changes, and weak delegates do not retain worlds or pawns.

Contents use FFastArraySerializer delta replication. Shared container records replicate to relevant clients; selected-container/feedback state is owner-only. Player item records currently replicate with the character so server and cooperative observers can inspect them. Presentation selection indexes are never trusted as server item identity.

## World interaction and dropping

ARVInventoryInteractable implements the accepted IRVInteractable lifecycle without inheriting the Gate 1 counter. ARVWorldItem uses the accepted 0.5 s hold and claims the pickup only after authoritative capacity admission. Serial completion and claimed/destroyed state prevent two winners. ARVStoragePoint opens a reusable container through the same hold system.

Drop searches several directions with clearance and floor checks. It rejects excessive floor height changes, protecting against drops underneath an interior floor, and preserves instance state. Items supported by tagged moving passenger floors use native replicated attachment to that floor and inherit platform network relevancy. Unattached pickups retain native distance culling. This is object placement; passenger CharacterMovement and its accepted reference-frame implementation are unchanged.

Current world visuals are small query-only cube placeholders, not final physics props. Generalized mesh-dependent drop bounds and active hand/two-person carrying remain future work. The large battery is explicitly excluded from ordinary player storage even if a future backpack capacity increases. Container storage can accept physical-carry items; a future hands/equipment system will handle their transport.

## RV and workstation preparation

Saved Gate4InventoryTest contains the purchased Class C derivative and five attached storage points: pantry, general cabinet, medical storage, tool storage and exterior compartment. Pantry accepts food/water tags, medical accepts medical tags, and tool storage accepts tool/material/automotive tags. General/exterior storage are unrestricted within capacity. All six accepted Gate 3 workstation placeholders remain separate.

Future workstations can query linked/nearby container components and their item definition tags, then use authoritative inventory transactions. Recipe/tool checks and atomic multi-container ingredient consumption belong to later crafting work, not this component. Cargo weight does not yet modify Chaos chassis mass or handling.

## Prototype UI and items

Canvas presentation: I toggles inventory, Tab selects player/container panel, Up/Down selects a row, T transfers one unit, G drops one unit. It displays quantity, kg/L capacity and condition, with authoritative feedback. It does not pause walking or mouse look and uses no rarity colors. Final UMG, icons, rebinding, large-list pagination and seated-driver inventory presentation remain future work.

Inert definitions: bottled water, canned food, bandage, pain medication, fuel can, engine part, scrap metal, hand tool, ammunition box, bulky supply crate and large battery. The tool is marked equipment-eligible; metal/tool crafting tags are metadata only. Prototype instances have a Batch custom-state value for transfer/drop validation.

## Gate 5 integration (accepted)

FRVConsumableMetadata on the existing definition supplies enabled flag, nutrition/hydration gains, minimum condition and future dietary metadata. ServerConsume resolves the requesting PlayerState's survivor inventory, validates owned GUID/metadata/benefit/cooldown, then ConsumeOneAuthority removes one existing runtime quantity serially before applying needs recovery. Definition names do not dispatch behavior. Stored items remain lightweight FastArray records; partial stacks preserve GUID/condition/custom state. Consumables in a shared cabinet must first be authoritatively transferred to the player. No second inventory, spoilage/cooking or medicine effects exist.
