# Gate 1 setup and acceptance
Status: NOT ACCEPTED. Source checks do not substitute for Unreal compilation or PIE.

## Prerequisites and build
Install the exact Unreal Engine 5.8 distribution using authorized Epic access, Visual Studio 2022 with Game development with C++, the engine-supported MSVC toolset and Windows SDK. This cloud machine has no discovered Unreal installation or build tool; proprietary engine binaries cannot be fabricated or installed from an unverified source.

Use the existing isolated checkout; do not create a worktree unless explicitly requested.
From the repository root in Windows PowerShell, with `$UE` pointing to the installed engine root:

```powershell
& "$UE/Engine/Build/BatchFiles/GenerateProjectFiles.bat" "-project=$PWD/RVSurvival.uproject" -game -engine
& "$UE/Engine/Build/BatchFiles/Build.bat" RVSurvivalEditor Win64 Development "-Project=$PWD/RVSurvival.uproject" -WaitMutex
if ($LASTEXITCODE -ne 0) { throw "Editor build failed" }
& "$UE/Engine/Binaries/Win64/UnrealEditor.exe" "$PWD/RVSurvival.uproject"
```

Do not advance if UHT/compiler errors occur. Record actual engine version and build output.

## Editor-only fixture
1. Create a Basic level; save as `/Game/Maps/Gate1Test`. No binary map is supplied in this source-only checkout.
2. Add a large floor with collision (e.g. cube scale 20,20,0.2), lighting, and two PlayerStarts separated by at least 200 cm, clear of the floor.
3. Place one `RVTestInteractable` cube with its center about 100 cm above the floor. Ensure Visibility blocking remains enabled. Rotate its text toward the starts.
4. Confirm World Settings GameMode is RVGameMode (or uses the project default). Set Editor Startup Map and Game Default Map to Gate1Test, and save.
5. PIE: Number of Players 2; Net Mode Play As Listen Server; separate windows. Also repeat with Run Under One Process disabled to catch process-local assumptions.

## Required acceptance checks (not yet run)
- Single player: WASD, mouse look and Space work; aim at cube within 300 cm. Hold E for 0.5 seconds; shared count increments once. Continuing to hold must not repeat.
- Release E early: count stays unchanged. Look away, walk out of range or behind an occluder during hold: count stays unchanged.
- Both players move independently. Each completes a hold, and both see the same resulting count. Simultaneous completions produce two increments without a lost update.
- Remote client works as well as listen host. Disconnect during hold produces no late completion for an unpossessed pawn.
- A late-joining client observes the existing count; re-enter PIE starts at zero (no persistence in Gate 1).
- Repeat using PIE network emulation with 100 ms latency and 2% packet loss; check eventual shared count agreement and no duplicate completion.
- Record build result, executed cases, actual counts, logs and any failures here. Gate 1 remains closed until these pass.

## Deliberate limits
No body mesh, hands, UMG assets, menu/session browser, campaign persistence, map binary, or vehicles. Canvas HUD is temporary presentation only. Interaction is Visibility-channel trace + hold; supports one active target per pawn. Input is runtime-created prototype mapping; content-configured rebinding remains future work. Start/complete/cancel are authority events; cosmetic replicated progress is not implemented. Rate limiting limits accepted starts, not hostile RPC bandwidth. Production abuse controls remain future work.
