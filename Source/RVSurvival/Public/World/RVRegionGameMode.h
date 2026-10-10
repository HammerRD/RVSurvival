#pragma once
#include "CoreMinimal.h"
#include "Core/RVGameMode.h"
#include "RVRegionGameMode.generated.h"

/** Region-only arrival policy; accepted game modes and respawn rules are unchanged. */
UCLASS()
class RVSURVIVAL_API ARVRegionGameMode : public ARVGameMode
{
    GENERATED_BODY()
public:
    virtual void BeginPlay() override;
    virtual void RestartPlayer(AController* NewPlayer) override;
    UPROPERTY(EditAnywhere,BlueprintReadOnly) bool bArriveAtMobileBase=true;
    UPROPERTY(EditAnywhere,BlueprintReadOnly) FName MobileBaseTag=TEXT("PlayerMobileBase");
    /** Native source keeps a parked base's terrain available while survivors explore. */
    UPROPERTY(EditAnywhere,BlueprintReadOnly,meta=(ClampMin="5000",ClampMax="30000")) float MobileBaseLoadingRadiusCm=12000;
private:
    void PlaceAtMobileBase(AController* Controller);
};
