#pragma once
#include "CoreMinimal.h"
#include "Inventory/RVWorldItem.h"
#include "RVInteriorAccessPoint.generated.h"
class ARVInteriorMotorhome;
/** Discrete door interaction, not a replacement for walking based movement. */
UCLASS()
class RVSURVIVAL_API ARVInteriorAccessPoint : public ARVInventoryInteractable
{
    GENERATED_BODY()
public:
    ARVInteriorAccessPoint();
    UPROPERTY(Replicated, BlueprintReadOnly) TObjectPtr<ARVInteriorMotorhome> Vehicle;
    UPROPERTY(Replicated, BlueprintReadOnly) bool bEnter = true;
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& Out) const override;
    virtual bool CanInteract_Implementation(APawn* Pawn) const override;
    virtual FText GetInteractionText_Implementation(APawn* Pawn) const override;
    virtual void CompleteInteraction_Implementation(APawn* Pawn) override;
};
