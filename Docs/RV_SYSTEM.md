# RV system plan
Gates 1, 2 and 3 are accepted. Gate 2 isolates supported Chaos Vehicles behind ARVVehicleBase and URVVehicleMovementComponent, and composes ARVMotorhome with authoritative driver/passenger URVVehicleSeatComponent instances. Gate 3 uses a reusable passenger reference-frame component around native CharacterMovement.

The preserved Gate 2 fallback content configuration is `/Game/Vehicles/BP_PrototypeMotorhome`. It uses Epic's installed UE vehicle-template off-road rig/physics/animation and a primitive shell labeled PROTOTYPE RV. The RV prototype has 3500 kg mass, automatic gears, rear-wheel drive and basic W accelerate, S brake/reverse, A/D steer, Space handbrake and E exit controls. Handling and physical body dimensions are prototype settings, not production Class C tuning. Test map: `/Game/Maps/Gate2VehicleTest`; Gate1Test is preserved.

Each seat defines a label, driver role, local entry offset and preferred exit offset. Runtime entry panels reuse the accepted 0.5-second interaction hold. Authority prevents double occupancy. Driver possession switches to the RV; the original survivor remains attached to its seat. Passengers retain survivor possession, remain attached, and cannot walk/jump or drive from a passenger seat. Driver exit waits for the entry key to be released after possession. Stationary E exit checks ground slope, height and capsule clearance, tries alternate roadside candidates, restores walking/possession and frees occupancy. If all candidates are unsafe, the seat remains occupied. Entry/exit speed limit is 150 cm/s. Disconnect releases the seat and parks the surviving shared vehicle.

The vehicle base, seat components and entry adapters contain gameplay; the Blueprint configures presentation and rig/tuning. Replacing art requires configuring a suitable skeletal physics rig/wheels and adjusting seat/entry/exit offsets, without rewriting networking or seat assignment. No engine, fuel, cooling, battery, electrical, water, storage or other future gameplay subsystem is implemented in Gate 2.

Gate 3 proved two networked players, highway-speed driving, front-to-rear passenger walking and stable based movement. There is no separate static interior. Stop after this accepted gate; later inventory/combat/world work requires a new user instruction.

Future systems separate fuel, individual mechanical conditions, automotive power and house power; no generic RV health. Cooling dependencies and empty-fuel propulsion blocking belong to later gates.

## Purchased Class C integration and Gate 3 (accepted)

The owned Class C RV Motorhome – Low Poly by MSWoodvine was imported through the signed-in Fab UE plugin into `/Game/RV`. Imported files remain unchanged; project-side derivatives live in `/Game/Vehicles/Gate3`. The original BP_PrototypeMotorhome and Gate2VehicleTest remain fallback/regression fixtures. The production derivative retains ARVMotorhome seats, possession and server-only vehicle forces.

The Class C visual assembly is approximately 7.65 m long and 2.58 m wide. Interior art includes a front floor at approximately 87.19 cm and raised rear floor at 101.49 cm in model coordinates. Simple box collision supplies floor, cabin walls, ceiling, furniture and open-entry steps. The walkable test aisle extends approximately x=-190 to x=130 cm; the rear bed is blocked rather than traversed as empty space. Imported art supplies presentation only, with no per-poly character or chassis collision.

A project-side chassis box and four measured wheel positions adapt the existing Chaos rig. Wheel bones must remain distinct from the chassis bone: Chaos disables wheel bodies during setup. Project-side offsets place the existing four wheel bones at the measured Class C wheel centers. Wheel radius is 39.25 cm. Prototype engine/suspension configuration is validated for the Gate 3 highway-speed tests and is not final production tuning. The exterior shell/compartment and wheel/steering visuals remain separate parts for later adaptation.

Six fixed placeholder endpoints reserve workbench, medical, kitchen/food preparation, storage, power controls and navigation/radio. Their only gameplay is an authority-completed test count. Future mobile-base systems remain modular and absent in this gate: food/water and needs, sleeping/fatigue, injury treatment, automotive/house power, generator/solar/battery, repairs/maintenance, crafting and storage. No detailed art dressing or Gate 4 systems are added.

Standing movement uses URVPassengerReferenceFrameComponent around native CharacterMovement bases. See GATE_3_VALIDATION.md for actual role/speed/correction/workstation results and known limits.

## Gate 4 storage foundation (accepted Gate 4)

The Gate 4 test map preserves the purchased Class C visual/physical derivative and adds reusable project-side pantry, general, medical, tool and exterior storage points. Storage actors attach to the vehicle mesh and contain URVContainerComponent; no cabinet-specific mutation code was added to ARVMotorhome or passenger movement. The six Gate 3 workstation points remain. Capacity and tag filters are configuration.

Future food/water, medical supplies, repairs, crafting, equipment and long-term storage can consume this data model through separate authoritative systems. Gate 4 adds no survival effects, recipes, fuel usage or electrical simulation. Vendor source assets remain unchanged; cargo mass/handling integration is deferred. See INVENTORY.md and GATE_4_VALIDATION.md for current tests and limitations.
