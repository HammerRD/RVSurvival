#pragma once
#include "CoreMinimal.h"
#include "Vehicles/RVMotorhome.h"
#include "RVWalkableMotorhome.generated.h"
/** Opt-in Gate 3 fixture. The Gate 2 asset/map retain their original configuration. */
UCLASS(Blueprintable)
class RVSURVIVAL_API ARVWalkableMotorhome : public ARVMotorhome
{
    GENERATED_BODY()
public:
    ARVWalkableMotorhome(const FObjectInitializer& Initializer);
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="RV|Interior") TObjectPtr<class UStaticMeshComponent> InteriorFloor;
};
