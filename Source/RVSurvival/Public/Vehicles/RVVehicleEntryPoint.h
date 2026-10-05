#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Interaction/RVInteractable.h"
#include "RVVehicleEntryPoint.generated.h"
class URVVehicleSeatComponent;
UCLASS()
class RVSURVIVAL_API ARVVehicleEntryPoint : public AActor, public IRVInteractable
{
    GENERATED_BODY()
public:
    ARVVehicleEntryPoint();
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& Out) const override;
    virtual void BeginPlay() override;
    virtual bool CanInteract_Implementation(APawn* Pawn) const override;
    virtual FText GetInteractionText_Implementation(APawn* Pawn) const override;
    virtual float GetInteractionDuration_Implementation(APawn* Pawn) const override { return 0.5f; }
    virtual void StartInteraction_Implementation(APawn*) override {}
    virtual void CancelInteraction_Implementation(APawn*) override {}
    virtual void CompleteInteraction_Implementation(APawn* Pawn) override;
    UPROPERTY(ReplicatedUsing=OnRep_Seat, BlueprintReadOnly) TObjectPtr<URVVehicleSeatComponent> Seat;
private:
    UFUNCTION() void OnRep_Seat();
    UPROPERTY() TObjectPtr<class UTextRenderComponent> Label;
};
