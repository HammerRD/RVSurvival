using UnrealBuildTool;
public class RVSurvival : ModuleRules
{
    public RVSurvival(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        PublicDependencyModuleNames.AddRange(new[] { "Core", "CoreUObject", "Engine", "InputCore", "EnhancedInput", "ChaosVehicles", "PhysicsCore", "GameplayTags", "NetCore" });
        if (Target.bBuildEditor) PrivateDependencyModuleNames.AddRange(new[] { "MeshDescription", "StaticMeshDescription" });
    }
}
