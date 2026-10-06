#pragma once
#include "CoreMinimal.h"
#include "Inventory/RVWorldItem.h"
#include "RVRestPoint.generated.h"
class ARVPlayerState;
class ARVSurvivorCharacter;
/** Exclusive reusable rest reservation; normal CharacterMovement remains in charge. */
UCLASS()
class RVSURVIVAL_API ARVRestPoint : public ARVInventoryInteractable
{
    GENERATED_BODY()
public:
    ARVRestPoint();
    UPROPERTY(EditAnywhere, Replicated, BlueprintReadOnly) FText DisplayName;
    UPROPERTY(EditAnywhere, Replicated, BlueprintReadOnly) float MaximumPlatformSpeed = 50;
    UPROPERTY(Replicated, BlueprintReadOnly) TObjectPtr<ARVPlayerState> Occupant;
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& Out) const override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
    virtual bool CanInteract_Implementation(APawn* Pawn) const override;
    virtual FText GetInteractionText_Implementation(APawn* Pawn) const override;
    virtual void CompleteInteraction_Implementation(APawn* Pawn) override;
    bool CanContinueRest(const ARVSurvivorCharacter* Character) const;
    void ReleaseAuthority(ARVPlayerState* Player);
};
