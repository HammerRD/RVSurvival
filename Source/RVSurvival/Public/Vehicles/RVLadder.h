#pragma once
#include "CoreMinimal.h"
#include "Inventory/RVWorldItem.h"
#include "RVLadder.generated.h"
class ARVSurvivorCharacter;
/** Parked-RV ladder with validated ground and roof endpoints. */
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
    UPROPERTY(EditAnywhere,Replicated,BlueprintReadOnly) bool bRoofAccess=false;
    UPROPERTY(EditAnywhere,Replicated,BlueprintReadOnly) FVector RoofExitLocal=FVector(-315,75,410);
    UPROPERTY(EditAnywhere,Replicated,BlueprintReadOnly) float RoofSurfaceHeight=319.6f;
    UPROPERTY(VisibleAnywhere) TObjectPtr<class UBoxComponent> RoofInteraction;
    virtual void Tick(float Delta) override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& Out) const override;
    virtual bool CanInteract_Implementation(APawn* Pawn) const override;
    virtual FText GetInteractionText_Implementation(APawn* Pawn) const override;
    virtual void CompleteInteraction_Implementation(APawn* Pawn) override;
    bool FindGroundExit(ARVSurvivorCharacter* Character,FVector& Position) const;
    bool ValidateRail(ARVSurvivorCharacter* Character,FVector& Position) const;
    bool FindRoofExit(ARVSurvivorCharacter* Character,FVector& Position,class UPrimitiveComponent*& Floor) const;
    FVector BottomWorld() const;
};
