#pragma once
#include "CoreMinimal.h"
#include "Inventory/RVWorldItem.h"
#include "RVResourcePoint.generated.h"
class ARVSystemsMotorhome;
/** Held-interaction endpoint; opening grants no authority beyond revalidated range/LOS. */
UCLASS()
class RVSURVIVAL_API ARVResourcePoint : public ARVInventoryInteractable
{
    GENERATED_BODY()
public:
    ARVResourcePoint();
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& Out) const override;
    virtual FText GetInteractionText_Implementation(APawn*) const override;
    virtual void CompleteInteraction_Implementation(APawn*) override;
    UPROPERTY(Replicated, BlueprintReadOnly) TObjectPtr<ARVSystemsMotorhome> Vehicle;
    UPROPERTY(Replicated, BlueprintReadOnly) bool bFuelFill=false;
};
