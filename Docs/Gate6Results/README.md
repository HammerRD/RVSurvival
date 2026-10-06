# Gate 6 validation receipts

Use `GATE_6_VALIDATION.md` for the current acceptance decision and investigation history.
JSON files contain actual assertions, process IDs, configuration and compact measurements.
Full frame samples, native screenshots and logs remain under `Saved/Gate6Validation`.
Failed/legacy runs are named accordingly and are not acceptance passes.

The final native-root four-case matrix is named `moving_*_root_final`.
The last source/fixture repeat is `resources_emulated_final` and
`moving_client_emulated_final_boundary`; final single and map audits use `*-fixture`.
The additional tiny energy boundary is in `final-stress.json`.

On this workstation, with Unreal closed, stage committed scripts using
`Tools/Validation/Gate6/stage.ps1`. This restores missing accepted helper scripts
and copies Gate 6 scripts into their explicit local staging paths. It does not
create/reload a map, change assets, delete results or run tests.

Run `run_final_network.ps1`, `run_moving_root_final.ps1`, `run_regressions.ps1`
or `run_final_checks.ps1` deliberately and sequentially. They refuse concurrent
editors, require fresh receipts, retain failed assertions and inspect Python/fatal
errors. Each suite starts/stops PIE and closes its editor. Do not launch an editor
or rebuild while a pipeline is still running. No force-kill/reload cleanup is used.

`configure.py` is fixture creation/configuration, not routine test cleanup.
`clean_fixture.py` records the one-time removal of the copied inert can from the
Gate 6 map. Recover saved/committed assets instead of recreating them unnecessarily.
Map audit inspections return primitive data so UObject wrappers do not survive
level changes. Module runners capture their quit callable before clearing globals.

These scripts use the existing D: project/engine paths and are development tools,
not a packaged-game automation or persistent save system. Network emulation is
outgoing listen-server 100 ms latency and 2% packet loss, not a bidirectional WAN test.
