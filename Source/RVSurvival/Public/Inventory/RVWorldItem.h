#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Interaction/RVInteractable.h"
#include "Inventory/RVInventoryComponent.h"
#include "RVWorldItem.generated.h"

/** Inventory interaction presentation, independent of the Gate 1 test counter. */
UCLASS(Abstract)
class RVSURVIVAL_API ARVInventoryInteractable : public AActor, public IRVInteractable
{
    GENERATED_BODY()
public:
    ARVInventoryInteractable();
    virtual bool CanInteract_Implementation(APawn* Pawn) const override;
    virtual float GetInteractionDuration_Implementation(APawn*) const override { return .5f; }
    virtual void StartInteraction_Implementation(APawn*) override {}
    virtual void CancelInteraction_Implementation(APawn*) override {}
protected:
    UPROPERTY(VisibleAnywhere) TObjectPtr<class UStaticMeshComponent> Mesh;
};

UCLASS()
class RVSURVIVAL_API ARVWorldItem : public ARVInventoryInteractable
{
    GENERATED_BODY()
public:
    ARVWorldItem();
    UPROPERTY(EditAnywhere, ReplicatedUsing=OnRep_Item, BlueprintReadOnly) FRVItemInstance Item;
    virtual void BeginPlay() override;
    virtual bool IsNetRelevantFor(const AActor* RealViewer, const AActor* ViewTarget, const FVector& SrcLocation) const override;
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& Out) const override;
    virtual bool CanInteract_Implementation(APawn* Pawn) const override;
    virtual FText GetInteractionText_Implementation(APawn* Pawn) const override;
    virtual void CompleteInteraction_Implementation(APawn* Pawn) override;
private:
    UFUNCTION() void OnRep_Item();
    bool bClaimed = false;
};

UCLASS()
class RVSURVIVAL_API ARVStoragePoint : public ARVInventoryInteractable
{
    GENERATED_BODY()
public:
    ARVStoragePoint();
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<URVContainerComponent> Container;
    virtual FText GetInteractionText_Implementation(APawn* Pawn) const override;
    virtual void CompleteInteraction_Implementation(APawn* Pawn) override;
};
