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
};
