# Gate 5 validation tooling

The gameplay implementation uses native Unreal networking, components, tags, timers, movement and UMG. These scripts are development-only test harnesses; they do not participate in game authority.

The saved maps and Data Assets are committed content. Do not recreate or overwrite Gate5SurvivalTest to resume validation. `gate5_configure.py` repairs project-side metadata/configuration in place; the original one-time map-copy fixture is deliberately not presented as a repeatable recovery workflow.

Archived `gate5_*.py` files correspond to `Saved/Gate5Validation/<name-with-gate5_-removed>.py`. Archived `run_gate5_*.py` correspond to `Saved/Gate5Validation/run_<suffix>.py`. Restore needed copies before using launch shims. Keep the registered-module `runner_runtime.py` available on the existing Saved/Gate3Validation Python path. Gate 1/2 regression wrappers reuse the accepted existing Saved/Gate1Validation and Saved/Gate2Validation harnesses; do not rewrite their completed gate logic.

`run_gate5_matrix.ps1` runs serial independent-process survival and moving-interior cases, baseline and outgoing-server 100 ms/2% loss. It requires the restored Saved launchers, primitive case JSON, and paired comparison helpers. `run_gate5_regressions.ps1` runs the final single/Gate1/Gate2/Gate4/stress sequence. Failures stop the helper for inspection; they never disable engine leak checks or weaken gameplay validation.

Reconnect tests reacquire the active world from the controlled pawn's owning level. World iteration alone can include old map objects. Only primitive state persists across native queued disconnect/reconnect travel; no Actor/World/Component wrappers cross it. Stage readiness checks floor/base, parked speed and replicated fixture metadata. Aim precedes E to permit native authoritative view-state convergence. The suite requires a real sleep reservation before testing disconnect cleanup.

Never run two launch helpers concurrently. Save/recovery checkpoint before risky editor work. Stop PIE, unregister callbacks, release registered runner modules and allow native teardown before another map/test. Bound local quit/log callables before clearing a module's globals. No callback caller may continue accessing globals after its own module is released.

Compact permanent receipts live in Docs/Gate5Results. High-frequency raw samples and full private Unreal logs live in Saved/Gate5Validation (ignored by Git). Paired metrics distinguish independent process positions from true local corrections. Fixture teleport/correction samples are excluded from moving-state measurements and identified separately; gameplay never uses a passenger transform-forcing tick.
