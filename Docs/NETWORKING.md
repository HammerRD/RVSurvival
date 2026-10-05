# Networking
Listen server first; authoritative logic does not depend on a local player or UI, preserving a future dedicated-server path. Movement uses Unreal CharacterMovement. No custom client position or speed RPCs.

Clients send begin/end intent through their owned replicated interaction component. Server derives pawn, view origin, control rotation and trace target; client cannot send a target, duration or result. Visibility trace limits range and rejects occlusion. The server checks eligibility at start, during the hold and at completion. Remote control rotation is still client aim intent, never permission to modify arbitrary gameplay state.

Each pawn owns one pending timer/target. Release cancels, invalid aim/permission cancels, teardown clears timers. Starts are throttled. The test actor serializes mutations on the authoritative game thread, increments once per completed hold and replicates only the changed count to all relevant clients. RepNotify updates presentation and is called explicitly on the listen host. Completion implementations must independently validate mutable actor state.

Required two-player and latency checks: GATE_1_VALIDATION.md. Not executed yet.
