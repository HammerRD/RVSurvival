# Gate 6 interior usability refinement evidence

Reproducible tools: Tools/Validation/Gate6Refinement. Raw logs, samples and failed identity receipts: Saved/Gate6Refinement and Saved/Gate6RefinementMoving (local recovery evidence; not production content).

Passing evidence:
- rear-single.json: 9 parked rear/seat checks.
- bed-door-stations-final.json: 67 repeated bed, safe wake/obstruction, six-station audit and hidden-target checks; bed-head-camera.png is actual PIE presentation.
- refine_host_door_fixed: 18 checks per process, moving door and rear walking.
- refine_client_baseline_repeat, refine_host_emulated, refine_client_emulated: 22 server/20 client checks with sleep/disconnect cleanup; use the repeat rather than the original client-baseline receipt whose teardown produced a Python NameError.
- refine_final_camera_client_emulated: 22/20 on final configurable head-camera source.
- refine_final_inside_client_emulated: 25/25; all paired checks pass; includes moving rear-to-passenger re-entry and parked driver/standing exchanges. The final harness reacquires remote actors after native relevancy recreation.
- refine_moving_host_baseline: 82/84 and 227 paired checks.
- refine_moving_client_emulated: 85/77 and 227 paired checks with 100 ms outgoing latency/2% loss.
- Regressions: accepted Gate 1 movement/interaction, Gate 2 seats/possession, Gate 4 inventory and Gate 5 needs suites on the refinement binary.
- final-measurements.json: standing drift/correction windows and 108/108 vendor hash integrity.

Paired-position limits remain 30 cm baseline / 75 cm emulated. Thresholds were not relaxed. Counts describe distinct targeted checks, not a claim of exhaustive production testing. Engine/client logs are scanned for Python errors, fatal errors and world leaks. See GATE_6_VALIDATION.md for final audit status, failures, recovery and limitations.

Final audits: refinement-exterior.json (33), refinement-camera.json (17), refinement-editor.json (54). Repeated saved-map loads release local UObject references before map changes. The final editor audit saves dirty packages and exits normally.
