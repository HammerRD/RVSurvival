#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "RVBiomePatch.generated.h"
/** Bounds and native PCG configuration only, not a custom foliage generator. */
UCLASS()
class RVSURVIVAL_API ARVBiomePatch : public AActor
{
    GENERATED_BODY()
public:
    ARVBiomePatch();
    UPROPERTY(VisibleAnywhere,BlueprintReadOnly) TObjectPtr<class UBoxComponent> Bounds;
    UPROPERTY(VisibleAnywhere,BlueprintReadOnly) TObjectPtr<class UPCGComponent> Dressing;
};
