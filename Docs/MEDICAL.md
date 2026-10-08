# Medical foundation (Gate 8, validation in progress)

## Ownership and engine integration

`ARVPlayerState` owns `URVHealthComponent`, `UAbilitySystemComponent` and
`URVMedicalAttributes`. Medical state belongs to the survivor even when the
controller possesses the motorhome. The additive GAS integration handles Blood,
Vitality and Analgesia attribute replication. Native gameplay effects own medication
duration and modifier aggregation. Accepted inventory, needs, movement prediction,
vehicle physics and passenger reference frames remain their existing systems.

RVSurvival rules live in the health component: injury eligibility, bleeding,
healing, treatment transactions and downed/revive policy. Native Gameplay Tags
identify injury/status categories. Primary Data Assets configure medical rates
and existing item definitions carry medical capability metadata. Item names are
presentation; treatment dispatch uses the metadata enum.

## Injury state and tuning

An `FRVInjuryInstance` has a GUID, injury kind/tag, body region, severity,
bleeding rate, pain, contamination risk, age, healing fraction, treatment flags
and revision. Regions cover head, torso and each arm/leg. Stored injuries are
lightweight reflected records, not spawned Actors.

`URVMedicalProfile` configures normal bleeding rates, recovery, downed thresholds,
timeout, treatment range and leg mobility. Default minor/moderate/severe bleeding
is 0.5/3/10 normalized blood units per minute. A normal untreated leg fracture
limits movement to 35%; splinting raises it to 65% until sufficient recovery.
Existing gameplay has no sprint action to bypass this movement policy.

Blood below the critical threshold also reduces Vitality. Blood at/below the
downed threshold or very low Vitality causes Downed. Zero blood or the configured
critical downed timeout causes Terminal. Terminal is a prototype state, not a
permanent-character replacement system.

Treating bleeding stabilizes it; injuries remain. Splints and burn dressings
stabilize rather than erase records. Antiseptic lowers contamination risk. Treated
injuries and concussion recover slowly when not bleeding, risk is low, and
nutrition/hydration are sufficient. Infection is a risk foundation, not disease
simulation. Pain is derived from remaining injuries minus temporary GAS analgesia.
Re-dosing refreshes one effect rather than stacking unlimited relief.

## Authoritative treatment transaction

The owned health component sends reliable requests to the server. A request names
patient PlayerState, injury GUID/revision and a supply GUID from the healer's
existing inventory. The server reserves the patient for one treatment, checks
eligibility/range/line of sight, and uses TimerManager for completion. It validates
again during the hold and at completion. Supplies are consumed exactly once at
successful completion through the accepted inventory transaction.

Cancellation, stale injury revision, unavailable/transferred supply, unsuitable
condition/severity, movement away or obstruction retain supplies. Healer/patient
positions are measured relative to their passenger frame when aboard the RV.
Vehicle motion alone is not patient movement. Changing frame or moving more than
50 cm within it interrupts the hold. Advanced kit use requires a reachable
configured medical station and a parked RV. Basic treatment can work in transit.

Revive requires a different conscious healer, a downed patient and controlled
bleeding. It restores partial Blood/Vitality and Active state while retaining
injuries. A downed seated patient must be treated while stopped. Downed players
cannot drive, change seats, move normally, consume/drop/transfer items, or issue
invalid service/resource/rest actions. Closing a panel remains possible.

## RV and UI

`ARVMedicalStation` reuses the accepted station interaction and links an existing
`URVContainerComponent`. Completed interaction opens the medical panel and medical
storage. Advanced treatment rechecks station reachability and its configured
power requirement rather than relying on a stale UI selection.

F9 is the default remappable Enhanced Input medical action. The native UMG panel
offers self/nearby patient assessment, injury/supply selection, begin, cancel and
close. It displays qualitative symptoms, treatment progress and authoritative
feedback. The survival HUD shows urgent medical warnings. Presentation never
creates authoritative injuries or inventory items.

## Development and persistence preparation

PIE-authority-only development functions apply test injuries, set Blood/Vitality,
set contamination risk, accelerate simulation and clear test state. Shipping/test
builds reject these functions. Short-duration diagnostic supply definitions live
under `/Game/Development/Medical`; normal supply durations are separate.

Injury records, life state and Blood/Vitality are SaveGame-compatible reflected
data. A future save system must also preserve downed elapsed time, medication
identity/magnitude/remaining duration, and profile identity. It must reapply GAS
effects through the ASC and cancel transient treatment reservations/timers rather
than serialize weak Actor pointers. Full save/offline simulation, medical
seamless-travel copying and permanent death are not implemented in this gate.

See `GATE_8_VALIDATION.md` for actual results, failed harness attempts and remaining
acceptance work. This architecture document does not claim the gate is accepted.
