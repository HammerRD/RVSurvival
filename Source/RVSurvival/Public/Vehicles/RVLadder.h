#pragma once
#include "CoreMinimal.h"
#include "Inventory/RVWorldItem.h"
#include "RVLadder.generated.h"
class ARVSurvivorCharacter;
/** Parked-RV ladder with a controlled top endpoint; roof traversal is intentionally unavailable. */
UCLASS()
class RVSURVIVAL_API ARVLadder : public ARVInventoryInteractable
{
    GENERATED_BODY()
public:
    ARVLadder();
    UPROPERTY(EditAnywhere,Replicated,BlueprintReadOnly) FVector BottomLocal=FVector(-395,75,110);
    UPROPERTY(EditAnywhere,Replicated,BlueprintReadOnly) float ClimbHeight=180;
    UPROPERTY(Replicated,BlueprintReadOnly) TObjectPtr<ARVSurvivorCharacter> Occupant;
    UPROPERTY(EditAnywhere,BlueprintReadOnly) FVector GroundExitLocal=FVector(-445,75,110);
    virtual void Tick(float Delta) override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& Out) const override;
    virtual bool CanInteract_Implementation(APawn* Pawn) const override;
    virtual FText GetInteractionText_Implementation(APawn* Pawn) const override;
    virtual void CompleteInteraction_Implementation(APawn* Pawn) override;
    bool FindGroundExit(ARVSurvivorCharacter* Character,FVector& Position) const;
    bool ValidateRail(ARVSurvivorCharacter* Character,FVector& Position) const;
    FVector BottomWorld() const;
};
