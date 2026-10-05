using UnrealBuildTool;
public class RVSurvivalEditorTarget : TargetRules
{
    public RVSurvivalEditorTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Editor;
        DefaultBuildSettings = BuildSettingsVersion.Latest;
        IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
        ExtraModuleNames.Add("RVSurvival");
    }
}
