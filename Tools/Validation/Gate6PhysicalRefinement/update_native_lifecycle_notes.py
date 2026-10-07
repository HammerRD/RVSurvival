"""Keep generated notes aligned with the observed native lifecycle fix."""
from pathlib import Path
base=Path(__file__).parent
replacements={
 'Seated native movement ticking is paused while the authoritative attachment owns the transform, then its previous tick policy is restored before standing.':'Seated CharacterMovement is natively deactivated while the authoritative attachment owns the transform, then Activate(true) restores required simulation ticks before standing.',
 'Native movement ticking now pauses only while seated; world/interior prediction and server correction rules remain intact and ticking is restored on release/restart transitions.':'Native CharacterMovement is deactivated only while seated; its supported IsActive guards reject stale move/adjustment RPCs. Activate(true) restores simulation on release/restart; world/interior prediction and correction rules remain intact.',
 'Survivor seat RepNotify/Restart pauses native CMC ticking during seat attachment, restores prior tick policy before walking and clears/ignores seated walking vectors.':'Survivor seat RepNotify/Restart deactivates native CMC during seat attachment, calls Activate(true) before walking and clears/ignores seated walking vectors.',
 'Native CMC ticking now pauses only during the authoritative seated transform, restores its prior tick policy before standing, and clears/ignores seated walking input.':'Native CMC deactivation now protects the authoritative seated transform, rejects stale character-move/adjustment RPCs through engine IsActive guards, then Activate(true) restores simulation before standing. A tick-only attempt left stale RPC corrections; restoring a cached remote-proxy tick flag left outside floor/reference-frame state stale. Both failed attempts are retained. Seated walking input is cleared/ignored.',
 'Build-remap-hints.log records Development Editor/Win64 Succeeded.':'build-native-seat-reactivation.log records the final lifecycle build Development Editor/Win64 Succeeded.',
}
for name in ('document_refinement.py','complete_validation.py'):
 p=base/name;text=p.read_text(encoding='utf-8')
 for old,new in replacements.items():text=text.replace(old,new)
 p.write_text(text,encoding='utf-8')
