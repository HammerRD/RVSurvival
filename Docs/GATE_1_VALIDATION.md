# Gate 1 setup and acceptance

Status: **ACCEPTED** — local PIE validation completed on 2026-10-05. Gate 2 has not begun.

## Environment and build

- Unreal Engine **5.8.3**, changelist **58210709** (`++UE5+Release-5.8`). Installed engine: `D:/Epic Games/UE_5.8`.
- The user reported a successful Visual Studio **Development Editor / Win64** build before this validation. The local `RVSurvivalEditor.target` receipt confirms Development, Win64, x64, Editor, and UE 5.8.3. The built module dated 2026-10-05 09:23:25 was loaded and exercised in PIE.
- No C++ changes were needed; no new compilation was performed or claimed during this session. No UHT/compiler failure was encountered during validation.
- Validation used the existing checkout and running Editor; no worktree was created.

For a future rebuild, from the project root in Windows PowerShell:

```powershell
$UE = 'D:/Epic Games/UE_5.8'
& "$UE/Engine/Build/BatchFiles/Build.bat" RVSurvivalEditor Win64 Development "-Project=$PWD/RVSurvival.uproject" -WaitMutex
if ($LASTEXITCODE -ne 0) { throw 'Editor build failed' }
```

## Saved fixture

- Saved the previously open `Game1Test` level, including its unsaved actor changes, as **`/Game/Maps/Gate1Test`** (`Content/Maps/Gate1Test.umap`). The original `Game1Test.umap` was retained.
- Set and verified World Settings GameMode Override **`/Script/RVSurvival.RVGameMode`**. PIE logs also identify `RVGameMode` as the game class.
- Set **Editor Startup Map** and **Game Default Map** to `/Game/Maps/Gate1Test.Gate1Test` in `Config/DefaultEngine.ini` and the running Editor settings.
- The actual level contained **three** Player Starts. Preserved all three, separated them by 220 cm, raised them to Z=100, and aimed them toward the cube. Locations: `(-600,-670,100)`, `(-600,-450,100)`, `(-600,-230,100)`.
- All Player Start capsule bottoms are Z=8; floor top is Z=-0.5, giving **8.5 cm clearance**. Successful PIE spawning and movement confirmed usable starts.
- Moved the single `RVTestInteractable` from `(-600,-450,0)` to **`(-360,-450,150)`** and rotated its label toward the starts. Mesh collision is **Query and Physics / BlockAll**, with **Visibility = Block**.
- With each start aimed toward the cube, horizontal trace entry distances are approximately **190 cm** or **258 cm**, inside the 300 cm interaction range. The cube spans the pawn eye height.
- Added one movable cube wall named **`Gate1Occluder`**, parked at `(-480,0,160)`, scale `(0.2,2,3)`, with BlockAll collision. The test temporarily moved its PIE copy into the aiming ray during a hold. The saved wall remains out of the starting interaction rays.

## Method and observed results

These were executed in real Unreal PIE worlds, including a separately launched client process. Timing-sensitive tests used Unreal's `Input.+key` / `Input.-key` Enhanced Input console commands through Python Slate tick callbacks. They exercised the configured W/S/A/D, SpaceBar, MouseX/MouseY, and E mappings and their bound gameplay callbacks. They did not directly call interaction completion or write the counter. Cancellation setup used runtime pawn relocation/control rotation and a Visibility-blocking wall. Those changes affected PIE copies only.

Counts were read independently from the server actor and client replica; server completion logs identify the interacting pawn. The HUD prompt and shared-count labels were visually observed in Editor and remote-client windows. Native mouse capture also visibly changed the remote client's view. This validates the input mappings and gameplay behavior with synthetic key inputs; it is not a physical keyboard hardware certification.

| Acceptance case | Actual result | Outcome |
| --- | --- | --- |
| Single-player WASD | W/S changed X in opposite directions; A/D changed Y in opposite directions, approximately 82 cm per scripted pulse | PASS |
| Mouse look | MouseX and MouseY changed yaw and pitch; native viewport mouse capture changed the view | PASS |
| Space jump | Pawn Z rose from approximately 89.65 to 152.15 | PASS |
| Aiming prompt | `Hold E to increment shared counter` displayed when aimed within range; absent behind the blocker | PASS |
| Hold E for 0.5 seconds | Count remained 0 at the pre-completion sample; server timer completed once and count became 1 | PASS |
| Continue holding E | Count stayed 1 through the continued hold | PASS |
| Release E after 0.2 seconds | Count stayed 1 | PASS |
| Look away during hold | Changed control yaw after 0.2 seconds; count stayed 1 | PASS |
| Leave range during hold | Relocated pawn outside 300 cm after 0.2 seconds; count stayed 1 | PASS |
| Break line of sight during hold | Moved the blocking wall into the ray after 0.2 seconds; count stayed 1 | PASS |
| Two players, Listen Server, one process | Each moved while the other remained stationary | PASS |
| Host interaction | Both server/client counts became `[1,1]` | PASS |
| Remote interaction | Both counts became `[2,2]` | PASS |
| Simultaneous holds | Both counts changed from `[2,2]` to `[4,4]`; server logged one completion per pawn | PASS |
| Continued multiplayer holds | Both stayed at 4; no additional completions | PASS |
| Remote early release | Both stayed at 4 | PASS |
| Run Under One Process disabled | Separate game process connected to listen host on port 17777; independent movement and counts 0 -> 1 -> 2 -> 4 passed on both processes | PASS |
| Remote look-away cancellation, separate processes | Both stayed at 4 | PASS |
| Disconnect during hold | Remote disconnected 0.2 seconds after starting; server connection closed before completion and server stayed at 4 | PASS |
| Late join | Disconnected client reconnected to the existing server and received count 4 | PASS |
| Restart PIE | Fresh worlds started at 0 after the previous session reached 4; also verified on single-player restart | PASS |
| Network emulation | PIE emulation enabled, server outgoing min/max latency 100/100 ms, packet loss 2%; separate-process counts converged to 1, 2, then 4, with no duplicate completions | PASS |
| Cancellation/disconnect under emulation | Early release, looking away, and disconnect left server at 4; client agreed before disconnect | PASS |
| Late join under emulation | Rejoining client received existing server count 4 | PASS |

The latency/loss run used the PIE settings' default **Server Only** target and **outgoing traffic**. This is a 100 ms delay on server-to-client packets, not a claim of bidirectional 100 ms injection. The local baseline and emulated runs both exercised actual client RPCs and replicated properties.

## Evidence

Permanent result files and timestamped log excerpts are in [Gate1Results/2026-10-05](Gate1Results/2026-10-05):

- `build.json`: local build receipt/version and the distinction between the user's build result and this session's runtime checks.
- `fixture.json`: saved package, GameMode, collision, starts, floor clearance, and range measurements.
- `single.json`: complete passing single-player run.
- `multi_baseline.json`: two-world, one-process listen-server run.
- `process_baseline_host.json` / `process_baseline_client.json`: independent results from separate processes.
- `process_network_host.json` / `process_network_client.json`: separate-process network-emulation results.
- `late_join_baseline.json` / `late_join_network.json`: count 4 observed after reconnecting to the existing server.
- `editor-results.log` / `network-client-results.log`: extracted completion/result records, with original UTC timestamps.

Full Editor and client logs remain in `Saved/Logs`. The local Python runners remain in `Saved/Gate1Validation` (ignored by Git). Initial runner API/property/spawn errors were corrected in the validation scripts and rerun; they were not gameplay failures. No counter values were changed to make a test pass.

## Known issues and final Editor state

- Unreal emitted `CreateSavedMove: Hit limit of 96 saved moves` warnings around window switching/background execution. Temporarily disabled background CPU throttling and capped the emulated run at 60 FPS. The measured independent movement and interaction/count assertions passed. These warnings remain a diagnostic limitation of the local PIE run, not an observed lost/duplicate counter update.
- The disconnect test leaves the client in a new standalone default-map world. Its injected held E can complete once in that **offline** world; this is distinct from the original server, which remained at 4. The runner cleared forced E before reconnecting. The late-join results confirm the original server count.
- Saving the new, untracked map produced a revision-control checkout warning; the package was successfully written and validated.
- No unresolved Gate 1 acceptance failures were observed. Network-emulation testing is a finite local sample, not an exhaustive network fault proof.
- PIE is stopped. Network emulation is disabled again, Run Under One Process is enabled, Number of Players is 2, and Listen Server mode remains selected. Background throttling was restored and the temporary FPS cap cleared. `Gate1Test` remains open and saved.

## Deliberate limits

No body mesh, hands, UMG assets, menu/session browser, campaign persistence, or vehicles. Canvas HUD is temporary presentation only. Interaction is Visibility-channel trace + hold; supports one active target per pawn. Input is runtime-created prototype mapping; content-configured rebinding remains future work. Start/complete/cancel are authority events; cosmetic replicated progress is not implemented. Rate limiting limits accepted starts, not hostile RPC bandwidth. Production abuse controls remain future work.

No vehicles, inventory, zombies, survival systems, or other Gate 2 gameplay were added. Multiplayer remains server-authoritative.
