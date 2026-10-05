# Unreal validation lifecycle

Map assets must use EditorLoadingAndSavingUtils.save_map, not generic asset duplication followed by LoadLevel. Save Map writes a copy; explicitly load that copy before configuring it.

Keep map/world inspection in short function scopes. Return names, paths, numbers and GUID strings rather than Actors or Worlds. Release temporary UObject arrays and dictionaries before map transitions. Python gc alone does not unload a standalone initialized World created by the wrong duplication path.

Slate test runners are real imported modules, not detached exec namespaces. Unregister all callbacks before releasing module globals. Stop PIE and allow teardown to finish; release runner UObject references while Unreal/Python are still alive before editor shutdown. Never load/reload a map from a Slate test tick or use garbage collection to hide an outstanding reference.

Gate 4 recovery repeat uses unique scratch map paths and never overwrites accepted maps. ValidationRecovery maps are disposable recovery evidence, not gameplay content. Tests retain Unreal's world leak detection and do not modify engine object flags.

Regression wrappers currently reuse the saved accepted Gate 1–3 runners from Saved/Gate1Validation, Saved/Gate2Validation and Saved/Gate3Validation. Original archived test scripts are documented in the earlier gate evidence. Run one editor suite at a time. Gate 4 scripts and result JSONs are recorded alongside GATE_4_VALIDATION.md.
