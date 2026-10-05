using UnrealBuildTool;
public class RVSurvivalTarget : TargetRules
{
    public RVSurvivalTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Game;
        DefaultBuildSettings = BuildSettingsVersion.Latest;
        IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
        ExtraModuleNames.Add("RVSurvival");
    }
}
