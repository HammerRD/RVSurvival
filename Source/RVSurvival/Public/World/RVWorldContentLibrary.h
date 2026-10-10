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
    static TMap<FString,int32> GradeRegionSitePads(UObject* Context);
};
