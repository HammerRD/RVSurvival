# Gate 5 front collision follow-up

Executed on the saved c3d38e5 refined Gate 5 vehicle, 2026-10-06.
No runtime Source or Content change was required.

Receipts and native screenshots are in `Docs/Gate5FrontAudit`.
Full samples and exploratory failures are in `Saved/Gate5FrontAudit`;
multiplayer raw samples/logs are in `Saved/Gate5Refinement`.

For an intentional repeat, copy exterior.py, launch.py and run.py into
Saved/Gate5FrontAudit. Launch UnrealEditor with the project and
`-ExecCmds="py D:/GitHub/RVSurvival/RVSurvival/Saved/Gate5FrontAudit/run.py"`.
The launcher starts/stops PIE and releases runner references before quitting.
Do not launch a second editor against the project while a suite runs.

run_regressions.ps1 reuses the accepted separate-process fixtures staged in
Saved/Gate5Refinement and the Gate 3 runner support. It executes the three fresh
role/seat/cargo cases sequentially and checks native receipts plus paired
movement comparisons. Its initial compact output directory is
Docs/Gate5Refinement; the completed follow-up receipts were moved into
Docs/Gate5FrontAudit to keep this audit together. Normal fixture input files in
Saved are overwritten when a repeat is requested.

final_save.py is an editor-only saved-map inspection: save before load, inspect
function-scoped actor wrappers, retain only primitive configuration, save and
quit. It resets PIE to one player without emulation for manual review.

See GATE_5_VALIDATION.md for actual test scope, underside/window limitations,
native input methods and the corrected exploratory Python harness errors.
