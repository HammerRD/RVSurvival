#pragma once
#include "CoreMinimal.h"
#include "Components/SphereComponent.h"
#include "Medical/RVMedicalProfile.h"
#include "RVBodyRegionHitComponent.generated.h"
/** Optional bone-attached query fallback; never participates in movement collision. */
UCLASS(ClassGroup=(RV),meta=(BlueprintSpawnableComponent))
class RVSURVIVAL_API URVBodyRegionHitComponent : public USphereComponent
{
    GENERATED_BODY()
public:
    UPROPERTY(BlueprintReadOnly) ERVBodyRegion Region=ERVBodyRegion::Head;
};
