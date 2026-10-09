"""Append ASCII architecture notes while preserving existing document bytes/encoding."""
from pathlib import Path
root=Path('D:/GitHub/RVSurvival/RVSurvival')
notes={
'TECHNICAL_ARCHITECTURE.md':'''## Gate 9.5 refinement architecture

Enhanced Input User Settings remains the only binding store. Native UMG key selectors and look/orbit mouse-stick dropdowns call MapPlayerKey, ApplySettings and AsyncSaveSettings; native key profiles supply current prompt labels. Personal sensitivity/inversion uses local GameUserSettings config. No second input framework or UI networking protocol is introduced.

URVDifficultyProfile Primary Data Assets describe bounded rules and presets. ARVGameState replicates authoritative rules, preset and revision through Unreal replication. Owned controller requests permit only the listen host to mutate shared rules. Existing needs, GAS-backed medical, infected perception/damage, fuel and mechanical components query centralized multipliers. Loot/population remain future configuration, without world generation.

Existing combat item metadata configures grip, first/third-person offsets, support target, actual sight/eye relief/FOV blend, muzzle/eject and future holster references. M1911 is a separate .45 ACP/seven-round definition; accepted 9mm remains. Sight ADS moves the cosmetic weapon using the native camera with owner-only native AnimGraph Two Bone IK. Authority hits still use server-derived eye/control view; CharacterMovement/reference-frame transforms are untouched.

Melee reuses owned inventory GUIDs, replicated combat component, native sphere/obstruction traces, PointDamage/body regions, hearing, montages and needs effort. One completion per validated request/cooldown and one target per sweep prevent duplicate hits. Epic raised armed locomotion is the prototype tool-ready pose. No full durability, combos, separate stamina pool or custom animation engine is added.''',
'NETWORKING.md':'''## Gate 9.5 shared rules and melee

Shared difficulty lives on replicated ARVGameState with a revision guard. Only the local authoritative listen-host controller may change it; client requests cannot overwrite server rules. Joining clients receive the same rules. Dedicated-server administration/session persistence remains future work.

Bindings, look preferences and UI remain client-local. Native Enhanced Input profiles apply locally with native asynchronous saves. Separate PIE processes on one Windows account share a physical save location; the runtime isolation test changes only the client's in-memory profile and verifies host LeftMouseButton/client Q independently fire, without writing that test change to shared disk. Real menu persistence is tested separately across clean launches.

Melee uses reliable owned requests with sequence, ownership/revision/condition, action-state and cooldown validation. Authority derives the view, sweeps within bounded range and checks line of sight before PointDamage. One swing admits one target once; multicast montage/noise is cosmetic. Damage/stagger/sequence converge under representative 100 ms/2% loss. No lag-compensation/custom replication layer is added. Owner sight IK does not teleport or attach walking characters.''',
'INVENTORY.md':'''## Gate 9.5 pickup and equipment refinement

Ordinary definitions default PickupSeconds to zero for tap pickup. Timed/committed actions retain configurable durations. The physically carried prototype battery explicitly keeps a 0.5-second hold. Capacity, GUID/condition/quantity, partial magazines, server pickup claims and container transactions remain the accepted inventory implementation.

Free .45 ACP M1911 and crowbar definitions live in /Game/Combat/Gate9_5, using existing inventory/equipment. Per-item grip/sight/muzzle/support/FP/TP data separates art from gameplay. Crowbar remains a tool-category prototype with future utility/durability hooks; this pass adds only light melee. Sources/licenses/credit are in THIRD_PARTY_ASSETS.md.''',
'GAME_DESIGN.md':'''## Gate 9.5 player-facing refinement

Ordinary loot uses tap interaction; treatment, revive, repair and committed actions remain timed. Grounded defensive shove and one crowbar complement firearms. Melee effort uses fatigue rather than a new arcade stamina meter. Free M1911 is .45 ACP/seven rounds, independent of retained 9mm.

Relaxed, Standard, Harsh and Custom expose tunable survival/consequence/combat/RV multipliers. Personal controls/view preferences are local; world rules belong to the host. Loot/population fields are preparation only, without generation. Final balance is not established. RV remains the central survival base; Gate10 is outside this refinement.''',
'ROADMAP.md':'''## Gate 9.5 authorized refinement

Gate9.5 is the authorized combat/input/difficulty/free-asset refinement before Gate10, tracked in GATE_9_5_VALIDATION.md. World/scavenging, director, population and region systems are not implemented. Acceptance requires rendered controls/combat, separate-process authority, emulation and selected regressions.'''
}
for name,text in notes.items():
 path=root/'Docs'/name;original=path.read_bytes();marker=text.splitlines()[0].encode('ascii')
 if marker not in original:path.write_bytes(original+b'\r\n\r\n'+text.replace('\n','\r\n').encode('ascii')+b'\r\n')
print('Architecture notes saved; prior document bytes preserved.')
