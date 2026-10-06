# Gate 5 — core survival needs validation

Status: IN PROGRESS / NOT ACCEPTED. Gate 4 was accepted by the user; Gate 6 has not begun.

## Foundation checkpoint

PlayerState owns URVNeedsComponent so driver possession does not replace survival state. Nutrition, hydration, fatigue, minimal survival reserve, simulation time and rest mode replicate from the server. URVNeedsProfile provides tunable Data Asset values; defaults use hours rather than minutes. Walking, heavy carrying, driving, passenger, rest and sleep metabolism are separate inputs. Critical needs reduce movement speed through GetMaxSpeed without rewriting CharacterMovement prediction or the accepted moving-base solver. Survival reserve is a minimal replaceable consequence, clamped above zero; no injury or death system is implemented.

Item definitions now contain FRVConsumableMetadata. Consumption uses an owned inventory GUID, validates metadata and benefit, removes exactly one item on the server game thread, then applies clamped recovery. Remaining stack identity, condition and custom state remain unchanged. A real-time cooldown is independent of accelerated needs simulation. Clients send intent only. Editor automation dispatches requests through weak native next-tick delegates to avoid the previously diagnosed editor script RPC callspace guard.

ARVRestPoint reserves one occupant and uses ordinary CharacterMovement at the character's current position. No sleep animation or cosmetic attachment is used. Rest/sleep requires a parked platform and ends when it moves or the reservation becomes invalid. Disconnect and teardown release reservations. Sleep reduces fatigue while continuing nutrition/hydration drain.

Developer controls require server authority, a non-shipping build and rv.Needs.AllowDebug=1. Their time scale does not change Chaos physics or interaction timers.

## Build / failures

Initial UnrealHeaderTool failure: URVNeedsTuning and FRVNeedsTuning shared a reflected engine name. The Data Asset class was renamed URVNeedsProfile. The next Development Editor / Win64 build succeeded. A new deprecated NetUpdateFrequency assignment was replaced with SetNetUpdateFrequency before further validation.

## Remaining validation

Content/map setup, usable UI verification, single-player and separate-process multiplayer, latency/loss, realistic accelerated stress, rest/disconnect cleanup, moving-RV eating/drinking/pantry, Gates 1–4 regressions and final startup/shutdown are pending. Compilation is not acceptance.

## Recovery discipline

Foundation source saved before editor work. Accepted maps and purchased vendor content remain untouched. Existing unrelated Config/DefaultEngine.ini and IDE files will not be staged. Stable milestone commits will be recorded here as work progresses.
