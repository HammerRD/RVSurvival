using UnrealBuildTool;
public class RVSurvival : ModuleRules
{
    public RVSurvival(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        PublicDependencyModuleNames.AddRange(new[] { "Core", "CoreUObject", "Engine", "InputCore", "EnhancedInput", "ChaosVehicles", "PhysicsCore", "GameplayTags", "NetCore", "UMG" });
        PublicDependencyModuleNames.AddRange(new[] { "GameplayAbilities", "GameplayTasks" });
        PrivateDependencyModuleNames.AddRange(new[] { "Slate", "SlateCore", "AnimGraphRuntime", "EngineCameras" });
        PublicDependencyModuleNames.AddRange(new[] { "AIModule", "NavigationSystem" });
        PublicDependencyModuleNames.Add("PCG");
        if (Target.bBuildEditor) PrivateDependencyModuleNames.AddRange(new[] { "MeshDescription", "StaticMeshDescription", "UnrealEd", "AnimGraph", "BlueprintGraph", "KismetCompiler", "AssetRegistry", "Landscape" });
    }
}

