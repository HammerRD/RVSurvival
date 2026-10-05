#pragma once
#include "CoreMinimal.h"
#include "Interaction/RVTestInteractable.h"
#include "Inventory/RVInventoryComponent.h"
#include "RVWorldItem.generated.h"

UCLASS()
class RVSURVIVAL_API ARVWorldItem : public ARVTestInteractable
{
    GENERATED_BODY()
public:
    ARVWorldItem();
    UPROPERTY(EditAnywhere, Replicated, BlueprintReadOnly) FRVItemInstance Item;
    virtual void BeginPlay() override;
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& Out) const override;
    virtual bool CanInteract_Implementation(APawn* Pawn) const override;
    virtual FText GetInteractionText_Implementation(APawn* Pawn) const override;
    virtual void CompleteInteraction_Implementation(APawn* Pawn) override;
private:
    bool bClaimed = false;
};

UCLASS()
class RVSURVIVAL_API ARVStoragePoint : public ARVTestInteractable
{
    GENERATED_BODY()
public:
    ARVStoragePoint();
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<URVContainerComponent> Container;
    virtual FText GetInteractionText_Implementation(APawn* Pawn) const override;
    virtual void CompleteInteraction_Implementation(APawn* Pawn) override;
};
