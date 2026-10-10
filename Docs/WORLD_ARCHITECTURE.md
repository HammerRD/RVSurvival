# Western New York region foundation

Gate 10 begins at accepted checkpoint 81b65c9. Current work is not accepted yet.

The first map, `/Game/Maps/WNY_PrototypeRegion`, is intended as an editable seed for
the future Western NY region, not the entire launch region. Native World Partition,
external actors, Landscape, spline roads and editor-baked PCG own static world
construction. Static dressing does not replicate. Gameplay containers and nearby
infected use ordinary Unreal relevancy; the RV retains its accepted architecture.

The initial terrain target is 4032 m square, 16x16 Landscape components, 63 quads
per component, 4 m vertex spacing, gentle broad hills and a level road corridor.
Useful driving-route target remains 4-6 km with five deliberately authored locations.
No acceptance is inferred from these dimensions or from a successful build.

Expensive environment generation belongs in the editor. Runtime supply/population
variation belongs on authority. A server WorldSubsystem keeps session data across
cell unload; it must never retain a World, Level or Actor strongly. Temporary
editor automation releases Python references before map changes and stops PIE first.

Future travel remains authored regional worlds, procedural dressing and playable
highway transitions: Western NY -> Pennsylvania/Ohio -> Midwest -> Great Plains
-> Rockies -> Los Angeles/Pacific Coast. Party-cohesion preload/unload and fully
interactive mobile-base transit remain planned, not implemented here.
