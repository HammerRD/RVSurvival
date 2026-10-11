#pragma once
#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "RVWorldContentLibrary.generated.h"

/** Native editor bridge; terrain construction is not available in shipping. */
UCLASS()
class RVSURVIVAL_API URVWorldContentLibrary : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable,meta=(DevelopmentOnly,WorldContext="Context"))
    static AActor* CreateRegionLandscape(UObject* Context,int32 Components,float VertexSpacingCm);
    UFUNCTION(BlueprintCallable,meta=(DevelopmentOnly,WorldContext="Context"))
    static TMap<FString,bool> ValidateLootLifecycle(UObject* Context,class URVLootProfile* Profile);
    /** Server PIE only: cooldown/quiet selection, dead and suspended member snapshots, and supply-cache conservation, using transient records it removes again. */
    UFUNCTION(BlueprintCallable,meta=(DevelopmentOnly,WorldContext="Context"))
    static TMap<FString,FString> ValidateEncounterBookkeeping(UObject* Context);
    UFUNCTION(BlueprintCallable,meta=(DevelopmentOnly))
    static class UPCGGraph* CreateBiomeGraph(const FString& AssetPath,const TArray<class UStaticMesh*>& Meshes,float PointsPerSquareMetre,bool Collision);
    UFUNCTION(BlueprintPure,meta=(DevelopmentOnly,WorldContext="Context"))
    static TMap<FString,int32> GetDressingStats(UObject* Context);
    UFUNCTION(BlueprintCallable,meta=(DevelopmentOnly,WorldContext="Context"))
    static bool ConfigureRegionStreaming(UObject* Context);
    UFUNCTION(BlueprintPure,meta=(DevelopmentOnly,WorldContext="Context"))
    static TMap<FString,FString> InspectRegion(UObject* Context);
    UFUNCTION(BlueprintCallable,meta=(DevelopmentOnly,WorldContext="Context"))
    static bool SetRegionAuthoringLoaded(UObject* Context,bool Loaded);
    /** Convert only the new WNY terrain through Unreal's native Landscape subsystem. */
    UFUNCTION(BlueprintCallable,meta=(DevelopmentOnly,WorldContext="Context"))
    static TMap<FString,int32> PartitionRegionLandscape(UObject* Context);
    /** Editor-only grading of the five prototype sites; never edits accepted maps. */
    UFUNCTION(BlueprintCallable,meta=(DevelopmentOnly,WorldContext="Context"))
    static TMap<FString,int32> GradeRegionSitePads(UObject* Context,bool bExtendGarage=false);
    /** Blend graded terrain up to road and parking-slab surfaces through the edit layer so pavement edges have no step. */
    UFUNCTION(BlueprintCallable,meta=(DevelopmentOnly,WorldContext="Context"))
    static TMap<FString,int32> BlendRegionTerrainToPavement(UObject* Context);
    UFUNCTION(BlueprintCallable,meta=(DevelopmentOnly,WorldContext="Context"))
    static TMap<FString,FString> AuditRegionTerrain(UObject* Context);
    /** Read-only: final heightmap, each edit layer, collision and rays at world XY samples, as JSON. */
    UFUNCTION(BlueprintCallable,meta=(DevelopmentOnly,WorldContext="Context"))
    static FString AuditRegionTerrainSamples(UObject* Context,const TArray<FVector2D>& Points);
};

