#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Interaction/RVInteractable.h"
#include "RVTestInteractable.generated.h"
class UStaticMeshComponent;
class UTextRenderComponent;
/** Shared authoritative counter: each completed hold increments it exactly once. */
UCLASS()
class RVSURVIVAL_API ARVTestInteractable : public AActor, public IRVInteractable
{
    GENERATED_BODY()
public:
    ARVTestInteractable();
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;
    virtual bool CanInteract_Implementation(APawn* Interactor) const override;
    virtual FText GetInteractionText_Implementation(APawn* Interactor) const override;
    virtual float GetInteractionDuration_Implementation(APawn* Interactor) const override { return 0.5f; }
    virtual void StartInteraction_Implementation(APawn* Interactor) override {}
    virtual void CancelInteraction_Implementation(APawn* Interactor) override {}
    virtual void CompleteInteraction_Implementation(APawn* Interactor) override;
protected:
    virtual void BeginPlay() override;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UStaticMeshComponent> Mesh;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UTextRenderComponent> Label;
    UPROPERTY(ReplicatedUsing=OnRep_InteractionCount, BlueprintReadOnly, Category="RV|Test") int32 InteractionCount = 0;
    UFUNCTION() void OnRep_InteractionCount();
};
