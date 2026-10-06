# Gate 5 — core survival needs validation

**Status: ACCEPTED — 2026-10-05. Final live validation, regressions, saved-content audit and build passed.**

Gate 4 was accepted by the user. Gate 5 only is authorized; Gate 6 fuel/electrical gameplay has not begun. This report records actual Unreal testing, not compile-only acceptance. Detailed development/failure chronology is retained in `Gate5Results/DEVELOPMENT_NOTES.md`.

## Implementation and Unreal framework review

`URVNeedsComponent` is a native replicated component on `ARVPlayerState`. It owns nutrition, hydration, fatigue, a minimal survival reserve, elapsed simulation time and rest mode. PlayerState ownership survives driver/passenger possession changes. `FRVNeedsState` is reflected scalar data; persistent scalar fields have SaveGame flags. Rest reservations are transient and do not serialize as gameplay identity. No full save system, offline progression or region streaming is implemented.

RVSurvival rules are hour-based metabolism, activity classification, thresholds, recovery, inventory consumption validation and exclusive parked rest. Unreal provides component lifetime/ticking, PlayerState ownership, Primary Data Assets, Gameplay Tags, native replication/RepNotify/RPC transport, weak TimerManager dispatch, CharacterMovement prediction/based movement, UMG and native queued reconnect travel. No custom transport, scheduler, prediction layer or general effect stack was introduced.

**GAS decision:** evaluated installed UE 5.8 GameplayAbilities APIs and official Epic GAS/Lyra patterns before continuing major implementation. Retained the component for three slow scalar needs and one rest mode; current gameplay does not need predicted abilities, duration stacking or effect aggregation. Do not build a custom medical effect system later: reassess PlayerState-owned ASC/AttributeSets/GameplayEffects before injuries, bleeding, medication or timed/stacking buffs. Current APIs/data separate that boundary from inventory and RV movement. This decision preserves working Gates 1–4 rather than migrating them into Lyra's larger framework.

Sources reviewed:
- [Epic GAS overview](https://dev.epicgames.com/documentation/en-us/unreal-engine/understanding-the-unreal-engine-gameplay-ability-system)
- [Epic attributes/ASC](https://dev.epicgames.com/documentation/en-us/unreal-engine/gameplay-ability-system-component-and-gameplay-attributes-in-unreal-engine)
- [Epic Lyra abilities/PlayerState ownership](https://dev.epicgames.com/documentation/en-us/unreal-engine/abilities-in-lyra-in-unreal-engine)

UMG supplies the new restrained survival readout. Native RepNotify/delegates drive updates and are unbound during widget teardown. Accepted Gate 4 Canvas inventory controls remain; CommonUI's layered/device-routing framework is deferred until required. Accepted movement/driving/interaction still use Enhanced Input. Inventory selection uses the existing native PlayerController key queries, with C consume, Z sleep/rest and R wake added; no custom input framework.

## Tuning and consequences

`URVNeedsProfile` is a Primary Data Asset; `/Game/Survival/DA_NormalNeeds` configures Gate 5's PlayerState. Server component tick interval is 0.25 seconds. Normal rates are not accelerated test rates.

| Need | Start / maximum | Awake idle change per hour | Warning / critical |
|---|---:|---:|---:|
| Nutrition | 90 / 100 | −6 | ≤30 / ≤10 |
| Hydration | 90 / 100 | −12 | ≤35 / ≤12 |
| Fatigue | 10 / 100 | +4 | ≥60 / ≥85 |

Walking multiplier 1.3; heavy-carry multiplier 1.25; driving 1.05; seated passenger 0.8. Standing-passenger activity uses character acceleration, not inherited vehicle velocity. Rest/sleep metabolism is 0.65/0.5; fatigue recovers 10/25 per hour respectively. Sleeping never replenishes nutrition/hydration.

Critical nutrition/hydration/fatigue cap movement at 0.8/0.6/0.65 of native speed; the strongest applicable limit wins. `GetMaxSpeed` reads this policy without mutating/restoring the accepted base movement settings or replacing prediction. Critical hunger/thirst reduce a minimal modular survival reserve at 1/5 per critical hour; integration accounts for threshold crossing within a time step. Reserve clamps above zero; this gate adds no elaborate health/injury/death system. Values, rates, thresholds, recovery and severity are editable tuning data; final balancing is not claimed.

Developer controls require authority, non-shipping/test builds and `rv.Needs.AllowDebug=1` (default off). `DebugSetValues`, `DebugSetTimeScale` and `DebugAdvanceTime` clamp/reject invalid values. Development needs acceleration changes neither Chaos time nor interaction/RPC cooldown clocks.

## Inventory and RV integration

`FRVConsumableMetadata` extends existing item definitions with enabled flag, nutrition/hydration gains, minimum condition and future dietary/calorie metadata. `/Game/Items/DA_Food` gives 25 nutrition; `DA_Water` gives 35 hydration. Their Gate 4 mass/volume/stack/condition/category rules remain intact. Other test items remain inert; medicine, fuel, cooking and spoilage are absent.

Owned reliable consume intent sends only an item GUID. Authority resolves that player's survivor inventory (including the retained driving survivor), rejects stale/unowned/non-consumable/no-benefit requests, removes one existing runtime quantity serially and applies clamped recovery. Remaining stack GUID, condition and custom state survive. Last-item duplicate requests cannot produce a second completion. Clients cannot supply effects or mint item state. Shared items must first transfer through the accepted authoritative container transaction.

`ARVRestPoint` is a reusable exclusive interactable, independent of RV art. Rear bed and dinette reservations replicate occupants as PlayerStates. Hold E begins rest; Z toggles sleeping/resting; R leaves. The character remains at its current native floor/base, with walking/jumping restricted while resting; no sleep teleport/attachment or elaborate animation. Disconnect/teardown releases reservations. Rest/sleep currently requires platform speed ≤50 cm/s and wakes when the RV moves. Both rest surfaces were validated simultaneously.

`/Game/Maps/Gate5SurvivalTest` is saved with 64 editor actors: preserved purchased RV/drive space, eleven pickups, seven storage points and two rest points. It uses `/Game/Survival/BP_Gate5GameMode` and `BP_SurvivalPlayerState`. Water supplies are a finite filtered cupboard, not a water-tank simulation. Existing pantry, general/medical/tool/exterior cabinets and six workbench/medical/kitchen/storage/power/navigation placeholders remain. Vendor art and accepted maps/fallbacks are unchanged.

## Actual validation

UE 5.8.3 CL 58210709, Development Editor / Win64; VS 14.44.35229 and Windows SDK 10.0.22621.0. Listen-server tests use two players. Independent-process cases use Run Under One Process **disabled**, confirmed distinct PIDs. Representative emulation uses outgoing-server min/max latency 100 ms and 2% packet loss; it is not a claim of bidirectional 100 ms or arbitrary fault tolerance.

| Test | Actual result |
|---|---|
| Final single-player | 27/27 passed: real pickup/consume, stacks/last item, stale/invalid GUID, condition/custom state, rest/sleep, clamping/status/consequences and analytical day |
| Survival separate process, baseline | 13 server + 13 client checks passed; 32 paired checks |
| Survival separate process, 100 ms/2% | 13 server + 13 client checks passed; 32 paired checks |
| Host drives / client walks, baseline | 70 server + 71 client checks passed; paired local discrepancy max 10.34 cm |
| Client drives / host walks, baseline | 72 server + 65 client checks passed; discrepancy max 8.69 cm |
| Host drives / client walks, emulated | 70 server + 71 client checks passed; discrepancy max 10.23 cm |
| Client drives / host walks, emulated | 72 server + 65 client checks passed; discrepancy max 26.88 cm |
| Native remote UI, 640×480 | 7 state checks and visual review passed; physical I/Down/C/Z/R controls |
| Accelerated stress, initial complete run | 200 consumptions / 200 GUIDs, 100 actual shared withdrawals, 20 rest/sleep/wake cycles; 86,404.89 seconds through real component ticks; no item/reservation/actor residue |
| Native same-process reconnect, emulated | Two corrected settled repeats each passed 7 server + 5 client checks; clean teardown |
| Gate 1–4 final regression | Gate 1: 23/23; Gate 2: 24/24 plus 4/4 possession checks; Gate 3: all four full moving matrices; Gate 4: 24/24 |
| Saved map startup/shutdown review | 23/23 checks; Gates 1–5 loaded twice, five assets and metadata verified, Save All and clean exit |
| Final accelerated stress repeat | 6/6 aggregate checks; 200 consumes, 100 shared withdrawals, 20 rest cycles, 86,403.47 simulated seconds; no residue |
| Final build | Development Editor / Win64 succeeded; final verification up to date, zero build actions |

Moving routes retain front/rear/sideways walking, standing, acceleration, braking, low/moderate/highway speed, gentle/strong turns, stop/resume, exit/reentry, six stationary/moving workstation interactions, pantry/medical/tool transfers, drop/repick and observer checks. Gate 5 adds stationary/highway/turning eating, road-speed drinking, continuing riding needs, independent possession state and confirmed parked sleep → movement wake. Storage actions were delayed eight seconds to insert the parked sleep test; no original movement requirement was removed.

All eight moving receipts recorded **zero floor-loss samples** in measured travel/storage windows. Largest actual passenger correction was **1.798 cm** in the emulated client walker; baseline/server-walker measured windows recorded zero. Paired observer timing discrepancy is reported separately from true local correction. Standing-drift and floor/correction receipts are in `movement-telemetry.json`; setup fixture teleports/corrections are not misrepresented as gameplay movement.

Permanent compact receipts: `Docs/Gate5Results`. High-frequency raw samples and private full logs: `Saved/Gate5Validation`. Counts target specific failure modes; stress operation counts are not presented as hundreds of artificial assertions.

## Failures, recovery and cleanup

- UHT name collision between struct/class resolved by naming the Data Asset `URVNeedsProfile`; builds then passed. Deprecated net-frequency assignment and float warnings were removed.
- Read-only Python tag-container setter repaired with Unreal's GameplayTag library. Partial content was immediately Save All'd and preserved, not recreated.
- Single harness live-struct alias/non-exported movement getter repaired. Stress elevated fixture was re-aimed after floor settling.
- UMG initially off-screen because UE's position setter resets anchors. Position-before-anchor ordering fixed; font enlarged for 640×480 and verified physically. Widget subscriptions clean up on teardown.
- Moving drinking's initial fixed expectation omitted genuine accumulated hydration drain; checks now measure pre-consumption value plus configured recovery. Rest was initially attempted at 1,465 cm/s; the parked policy correctly rejected it. Test now verifies actual parked speed and confirmed sleep before wake.
- Disconnect caller initially read globals after clearing its module. It now returns immediately. Reconnect readiness/name/world-scope/timing issues were fixed without changing gameplay checks. Native queued travel uses only primitive persistent Python state and reacquired active-world references.
- A failed reconnect timeout repeatedly reset its exit deadline after Stop PIE. The guard was fixed. Windows UI activation failed twice; only that exact already-stopped/All Saved test process was terminated after command-line verification. This failed run is recorded as **forced cleanup**, not clean shutdown. Corrected runs use native clean teardown.
- Final audit used an incorrect Python boolean attribute spelling; replaced it with the reflected property getter. The corrected audit passed all checks. One idle, fully saved editor was closed through graceful Windows taskkill without force, with clean engine exit recorded.
- No new reproducible World Memory Leak fatal error was found; leak detection was not disabled. Unsupported World asset duplication/reload cleanup was not used.

## Limits and persistence boundary

Prototype balance, UI/art and logical standing rest poses remain. Parked-only sleep/rest is intentional; auto-wake on movement is validated. There is no full save/offline progression, persistent reconnect inventory, disease/temperature/nutrition-science/spoilage/contamination, full health/medical effects, cooking, fuel/electrical or streaming implementation. Reconnect creates a valid new session pawn; shared storage/other players are preserved, not a claim of full persistent character recovery. Existing seated inventory UI and Gate 3 rough-terrain/larger-party limits remain. Full timed/stacking medical effects require a fresh GAS decision before implementation.

Future persistence records need nutrition, hydration, fatigue, survival reserve, simulation time and a stable player identity; rest reservations should safely restore awake. Relevant saved timestamps/offline policy remain future design. The RV remains interactive during planned authored/procedural regional transit; no survival rule depends on one pawn or editor test state. Long-term region/party-cohesion decisions are in GAME_DESIGN.md and TECHNICAL_ARCHITECTURE.md.

## Saved files and checkpoints

New native files: `Public/Private/Survival/RVNeedsComponent`, `RVRestPoint`; `Private/Player/RVPlayerState.cpp`; `Public/Private/UI/RVSurvivalWidget`. Modified inventory definition/component, PlayerState/controller/survivor, CharacterMovement speed policy, HUD, vehicle seat-entry guard and Build.cs (UMG). Content: Gate5SurvivalTest, DA_NormalNeeds, BP_SurvivalPlayerState, BP_Gate5GameMode and Food/Water metadata. Validation tooling and required design/network/inventory/RV/roadmap/changelog documentation are committed.

Checkpoints: `61178dc` foundation; `e518d58` framework/UMG; `7c4c0e6` saved content; `5677c47` single-player/framework decisions; `7502418` UI/lifetime/stress; `41b06a8` native controls; `42273e5` baseline authority/moving roles; `2cb14dc` emulated movement/reconnect/telemetry. `f41330a` final regressions/stress; final acceptance checkpoint follows this report. See local Git log for its exact hash.

Vendor SHA-256: 108/108 match accepted import. Accepted Gate 1–4 maps and existing vehicle/fallback files have no diff from `7881ab0`. Existing unrelated `Config/DefaultEngine.ini`, `.vsconfig`, `Automation_RVSurvival.slnx`, `RVSurvival.slnx` are preserved outside commits; the configuration's security token is not reproduced in reports.

Final regression milestone: final single-player 27/27; Gate 1 23/23; Gate 2 24/24 plus 4 inventory-possession checks; Gate 4 expanded inventory 24/24 (including consumable drop/repick, mass/volume, container contention and disconnect integrity); final stress all six aggregate checks passed. Corrected settled reconnect repeats each passed 7 server + 5 client checks under emulation. All completed final regression editors shut down cleanly. Saved-map review passed 23/23 and the final build succeeded. All meaningful Gate 5 requirements passed; Gate 5 is ACCEPTED. Unreal is closed, all content is saved, and Gate 6 has not begun.

## Gate 5 post-manual-playtest refinement — ACCEPTED (2026-10-06)

Gate 5 remains ACCEPTED after this refinement. Gate 6 has not begun. This section supersedes the old Gate 5 fixture counts/configuration while preserving the preceding technical-acceptance history. Evidence and executable harness snapshots are in Docs/Gate5Refinement and Tools/Validation/Refinement; raw timelines/logs remain locally in Saved/Gate5Refinement.

### Feedback, measured cause and entry/collision changes

Manual feedback covered low/close chase camera, getting stuck in the cabin, invisible entry stairs, missing seat switching and exterior cargo storage. The exact original manual stuck position/state was not recorded, so it cannot be conclusively reconstructed. The investigation did confirm concrete geometry/placement defects: the old entry collision was centered at x=122 cm, while the purchased stepwell is centered at x=92.4; a full front-floor slab covered the recessed real treads; and the dinette collision protruded to x=95 while the visible furniture ends around x=51. Native baseline walking at the old approach stopped against an invisible lip. The baseline center aisle itself was walkable; this is not a claim that every original manual symptom was independently reproduced.

The project derivative splits the floor around the well, aligns the doorway to x=55..130 and limits the dinette to x=55. Simple collision follows the real 28.9/57.7 cm interior treads. A visible prototype exterior tread (local top 8 cm) supplies the outside approach; only that tread needs additional prototype art. House door/glass project components are open at -90 degree yaw. Query-only boxes represent the open leaf, cab sides, hood and front fascia. Vendor meshes remain unchanged and supply no per-poly character/Chaos collision.

Hold E at the side entry places a standing character in a full-capsule-clear aisle near local (130,0,180), including other-player/furniture clearance. The exit search is near (92.4,240,0), with full outside capsule radius considered before restoring movement. A first single route exposed the old cab-side exit leaving the character behind the house-door sight line; that actual placement problem was fixed. Natural physical step entry/exit also works. No passenger transform is forced every tick; capsule height 88 cm, outside radius 34 cm and accepted interior radius 30 cm/speed policy are retained. No emergency teleport command substitutes for collision repairs.

### Camera, seats and exterior compartments

The current production/test derivative is /Game/Vehicles/Gate5Refinement/BP_ClassCRefinedMotorhome, used in Gate5SurvivalTest. Tunable native spring-arm settings: length 1400 cm; pivot (-70,0,340); pitch -12 degrees; socket offset (0,0,60); FOV 85; probe radius 16 cm; collision enabled; camera lag/inherited pitch/roll disabled. Default camera local position is approximately (-1425,0,697), well above the roof and about 10.7 m behind the rear bumper. Native sphere sweep retracted approximately 612 cm / 1056 cm for the two obstacle placements and recovered the full arm. Physics/drivetrain/wheel/chassis assets and steady driving controls are unchanged.

Seated controls displayed on HUD: 1 driver, 2 first passenger, V next available seat, E normal exit. Stop before switching (existing configurable 150 cm/s limit). Owned intent RPC validates source controller/pawn/reservation and free target before serial transfer; driving inputs are cleared on leaving the driver seat. The same survivor/needs/inventory is retained; occupancy, possession and cleanup use the accepted native seat system. Additional passenger seats can participate in V cycling. Standing players can Hold E at compact cabin seat markers. Shared constructor defaults make those marker dimensions identical on server/client; an initial server-only dimension adjustment was corrected before final tests.

Seven separate purchased doors SM_RV_Van_Compartment_01..07 now each expose an independent ARVExteriorStoragePoint/URVContainerComponent. The replicated/configurable DoorPartName identifies its corresponding Art_RV_Van_Compartment_XX component and FindVisualPart exposes the existing separate pivot for future animation. Current doors remain closed/static; E opens the container UI. Capacities/labels/positions/tag filters are editable. See INVENTORY.md for the seven-door table. Inside, pantry/medical/water supplies remain and Personal supplies replaces General cabinet at 10 kg / 12 L. Empty generic tool/exterior markers were removed only from this map; all six workstations and two rest locations remain.

Saved map: 62 editor actors, 11 pickups, 5 saved storage actors, 2 rest points and BP_Gate5GameMode. Runtime adds seven exterior compartments, giving 12 storage actors including the standalone outside test container. Accepted Gate 1-4 maps/vehicle/fallback content have no changes from 0e7a2cb. All 108 vendor-file hashes match the accepted import after the final audit.

### Actual validation

| Suite | Result |
| --- | --- |
| Native physical entry/aisle/exit, door interaction, seat transitions and exterior shell movement | 22/22 final; earlier targeted route 17/17 |
| Driving camera: low/road/about 60 mph, turns, reverse, far/near obstacles, recovery and visual review | 17/17; highway 2673 cm/s |
| Separate-process custom seats/doors/cargo/contention, baseline | 51 server / 48 client, all pass |
| Same custom suite, outgoing-server 100 ms / 2% packet loss | 51 server / 48 client, all pass |
| Host driving / client walking, baseline and emulated | 72 server / 73 client in each, all pass |
| Client driving / host walking, baseline and emulated | 74 server / 67 client in each, all pass |
| Gate 1 movement/jump/look/interaction regression | 23/23 |
| Gate 2 seats, possession, both drivers, reverse/exit and disconnect | 24/24 plus 4/4 inventory-possession |
| Gate 4 inventory/capacity/stacks/containers/contention/drop/repick/disconnect | 24/24 |
| Gate 5 food/water/quantity/invalid requests/rest/sleep/wake | 27/27 |
| Saved assets/maps, every Gate 1-5 map reopened twice, save and clean shutdown | 30/30 |
| Final Development Editor / Win64 build | Succeeded; up to date |

Moving routes use actual native input and approximately 60 mph, stationary/low/road speed, acceleration, braking, gentle/strong turns, stop/resume, mouse look, front/rear/sideways walking, physical door exit/re-entry, all six workstation interactions, cancellation, rest/wake and moving pantry/medical/personal transfers. They also consume food/water while riding and perform actual floor-attached drop/repick. Host/client run in distinct processes. Shared exterior-door contention is tested independently for all seven compartments, including last shared food ownership, preserved GUID/condition/custom state, an 18 kg engine part in compartment 03, occupied-seat rejection, numeric/V controls and disconnect while seated. No duplicated or lost successful transfers were observed.

Measured moving/storage windows (setup/intentional entry/exit excluded): zero floor-loss samples and maximum recorded passenger correction 0 cm in all eight process reports. Worst standing-phase horizontal drift 2.502 cm. Independent-process maximum local differences: host baseline 10.33 cm; client baseline 10.24; host emulated 10.41; client emulated 28.54. These retain the accepted baseline/emulated thresholds; no acceptance limit was relaxed. Native game captures were visually reviewed for chase framing/clipping and the real/visible entry steps. This is automated input/measurement and visual inspection, not a claim of a new human subjective handling playtest.

### Failures, corrections and automation stability

- An initial compile used a nonexistent inherited ShadowMesh field; corrected to the existing Mesh and rebuilt successfully.
- The first door-exit route exposed the cab-side exit/sight-line problem described above; source was fixed and the complete route rerun.
- Python fixture setters and unexported camera-spawn wrappers were corrected to reflected setters and safe PIE-only prop reuse. Braking waits check actual speed rather than assuming a delay stops the RV.
- The old moving fixture tried an 18 kg engine part in the newly limited 10 kg personal drawer. Capacity correctly rejected it; the old test's unconditional item lookup failed. It now asserts bulk rejection, transfers fitting bandages/tools and tests the engine part outside.
- Facing the rear drawer gave no safe drop path: native logging named Bathroom obstruction and Bed support about 76 cm above the feet. The item was retained with No safe drop location. The revised test asserts conservation, looks toward the clear aisle and retries the same native request; floor attachment and repick must actually pass.
- A new observer diagnostic incorrectly demanded owner-only inventory feedback on the non-owning driver. The check now respects COND_OwnerOnly while verifying replicated item conservation everywhere.
- One uninstrumented timed interior-seat run failed. Its original cause is unconfirmed. An instrumented repeat passed; the fixture was also corrected to release Space after braking before character possession. Corrected baseline/emulated repeats pass, and failed receipts remain archived. No speculative gameplay rewrite was used to hide it.
- A PowerShell result parser misread the Gate 2 array as null rows; the native receipts already passed 24+4. Replaced with a schema-aware Python validator and resumed only unfinished regressions.

No current editor crash, World Memory Leak or Python error occurred in the completed final suites. Temporary callbacks/runners are released, PIE stops before map changes, audit functions return only primitive data and actors/worlds are not held across reloads. Leak detection remains enabled. All final editors shut down cleanly.

### Files, checkpoints and remaining limits

New native classes: ARVInteriorAccessPoint, ARVExteriorStoragePoint, ARVVehicleInteriorSeatPoint; new configurable FRVExteriorCompartmentDefinition. Modified ARVInteriorMotorhome, ARVVehicleBase, ARVPlayerController, ARVPrototypeHUD and only an outside-capsule getter in URVPassengerReferenceFrameComponent. No passenger movement solver, inventory transaction/needs implementation or Chaos tuning was replaced. Content changed only Gate5SurvivalTest and the new refined project Blueprint. Required RV/inventory/network/changelog docs and validation tooling/results are saved.

Local checkpoints: cc05a60 baseline/recovery; 765cc89 saved compiled refinement foundation; 0c0edce initial separate-process seat/storage validation; 5bf48ef native cabin marker fix and passing camera; 8528379 corrected baseline/emulated seats/cargo; d3a15dd first full moving route/safe drop recovery; 40a1ba7 full role/emulation movement matrix. Final regression/documentation checkpoint follows; inspect local Git log for its exact hash.

Known limits: static compartment doors and static open house door/prototype exterior tread; no final animation/art/rebinding; parked seat switching and entry/exit; accepted parked-only rest/sleep and seated-inventory limitations; no full save/cargo-mass/rough-terrain/larger-party claims. The exact original manual stuck pose and original timed harness miss were not conclusively reproduced. Current full routes have no reproduced trapping or networking blocker. A fresh manual usability review of Gate5SurvivalTest is recommended before authorizing Gate 6.

All content is saved. The unrelated pre-existing Config/DefaultEngine.ini, .vsconfig, Automation_RVSurvival.slnx and RVSurvival.slnx are preserved outside refinement commits; security/config values are not copied into this report. No Git push or Gate 6 work was performed.

## Gate 5 front / engine-bay collision follow-up — 2026-10-06

**Result: Gate 5 remains ACCEPTED. Checkpoint c3d38e5 already contains the front collision fix in Gate5SurvivalTest's BP_ClassCRefinedMotorhome.** No additional Source or Content change was necessary. Older Gate 3/4 maps and the original/fallback Blueprint intentionally retain their accepted configurations; this result does not claim every legacy RV placement uses the refined derivative.

### Cause and existing protection
Purchased visual parts have NoCollision; the Chaos chassis intentionally ignores Pawn/Visibility to preserve passenger physics. The old walking shell's FrontWall ended around local x230, while the purchased cab/nose extends to approximately x400. Without project-side nose/cab queries, a standing character could enter visual bodywork and bring the camera inside it.

The refined Blueprint already has separate query-only boxes, in centimetres (center; half extent):
- FrontFascia: (402,0,95); (5,101,77).
- HoodTop: (314,0,156); (90,97,6).
- CabExteriorLeft/Right: (310,+/-101,85); (90,5,70).
- Existing FrontWall/cab-firewall boundary: (230,0,195); (5,120,105).

These supplement the house walls and rear boundary; they do not create an oversized full-RV box, change Chaos driving physics, reduce the outside capsule, or edit vendor meshes. The current 34 cm outside capsule stopped at local x441.5 in the center/front-offset tests, outside the fascia's x407 surface.

### Fresh validation and actual scope
Archived scripts, compact receipts and native game screenshots: Tools/Validation/FrontAudit and Docs/Gate5FrontAudit. Runtime logs and full trajectories: Saved/Gate5FrontAudit and Saved/Gate5Refinement.

- Exterior suite: **33/33 pass**. Nineteen actual native-input approach tests cover center/offset frontal walking, a normal frontal jump, diagonal corners, cab sides, actual front/rear wheel positions, both house sides and rear. Corner assertions inspect the complete trajectory rather than rejecting safe sliding around the exterior.
- Twelve short native Visibility query checks cover bumper/grille/fascia, hood, engine sides, firewall, cab/windshield boundary, house sides, rear and lower frontal body. Python exposes hit existence but not protected hit-component metadata; these checks do not claim component-identity/impact-point measurements.
- One continuous five-waypoint exterior walk-around passed without intermediate teleportation; one unchanged capsule-radius check passed. Native front-center/left/right and rear screenshots were visually inspected. Solid hood/grille/bodywork did not expose the interior by camera penetration. Genuine windshield glass remains transparent.
- Separate-process shared seat/cargo suite: **51 server / 48 client checks pass**, including both drivers, driver/passenger switching, occupied-seat rejection, all seven independent exterior containers, shared transfers/contention, preserved item GUID/state, food/water, drop/repick and disconnect seat release.
- Host driver/client walker: **72 server / 73 client pass**; client driver/host walker: **74 server / 67 client pass**. Each independent-process comparison passed 187 sample checks. Maximum paired local-position differences were **10.52 cm** and **8.92 cm**, respectively.
- These fresh moving routes include approximately 60 mph, acceleration, braking, turns, standing/front/rear/sideways walking, physical side-door exit/re-entry, workstation interaction, moving storage, food/water and survival state across possession. Measured movement/storage windows (setup and intentional transitions excluded) had **zero floor-loss samples and maximum recorded passenger correction 0 cm** in all four process reports. No acceptance threshold was weakened.
- This follow-up reran baseline separate-process conditions; the accepted c3d38e5 refinement's 100 ms / 2% packet-loss results remain documented above and were not represented as newly executed tests.
- All **108 vendor files** still match preserved SHA-256 hashes. Source/Content have no diff from c3d38e5. Final editor inspection reopened the saved Gate5 map, confirmed the refined vehicle/collision configuration, saved before/after inspection and shut down cleanly. No World Memory Leak or runtime/editor crash occurred in the successful final sequences.

### Boundaries and harness corrections
The mechanical underside contains genuine openings: a vertical line through local (320,0) from z-10 to z120 can be unobstructed. Normal standing players cannot pass beneath the tested front structure: its ground clearance is far below the 176 cm full-height capsule. Lower frontal approaches were blocked. This is not a watertight-hull, crawling, noclip, elevated-platform or roof-climbing certification. Windows are allowed to show the cabin through actual glass.

The original human playtest pose/map was not recorded, so the reproduction uses ordinary head-on/offset/jump approaches in the current refined Gate5 map rather than claiming an identical historical pose. No current engine-bay walk-in was reproduced. Initial harness iterations used an unavailable Python BreakHitResult wrapper/protected hit metadata and an overly restrictive corner endpoint check; these were corrected to supported native hit-existence checks and whole-path intrusion checks. Failed exploratory receipts/logs remain under Saved; they did not justify speculative gameplay changes.

This follow-up changes validation/documentation only. All work is saved; the local checkpoint follows this section (use Git log for its hash). Pre-existing Config/DefaultEngine.ini and IDE-generated files remain untouched outside the checkpoint. **No Gate 6 work.**
