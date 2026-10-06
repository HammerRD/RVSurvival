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
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="RV|Interaction") TObjectPtr<class UBoxComponent> InteractionSurface;
    UPROPERTY(EditAnywhere, ReplicatedUsing=OnRep_InteractionExtent, BlueprintReadOnly, Category="RV|Interaction") FVector InteractionExtent=FVector(7.5);
    UFUNCTION() void OnRep_InteractionExtent();
    virtual void OnConstruction(const FTransform& Transform) override;
    virtual void BeginPlay() override;
    UPROPERTY(EditAnywhere, Replicated, BlueprintReadOnly) FText DisplayName;
    UPROPERTY(EditAnywhere, Replicated, BlueprintReadOnly) float MaximumPlatformSpeed = 50;
    UPROPERTY(Replicated, BlueprintReadOnly) TObjectPtr<ARVPlayerState> Occupant;
    UPROPERTY(EditAnywhere, Replicated, BlueprintReadOnly, Category="RV|Bed") bool bUseLyingPose=false;
    UPROPERTY(EditAnywhere, Replicated, BlueprintReadOnly, Category="RV|Bed") FVector LyingOffset=FVector(-70,15,40);
    UPROPERTY(EditAnywhere, Replicated, BlueprintReadOnly, Category="RV|Bed") FRotator LyingRotation=FRotator(0,90,0);
    UPROPERTY(EditAnywhere, Replicated, BlueprintReadOnly, Category="RV|Bed") FVector WakeAisleLocation=FVector(-185,0,185);
    UPROPERTY(EditAnywhere, Replicated, BlueprintReadOnly, Category="RV|Bed") FVector LyingCameraOffset=FVector(80,0,25);
    UPROPERTY(EditAnywhere, Replicated, BlueprintReadOnly, Category="RV|Bed") FName LyingSupportCollisionName;
    bool FindWakePosition(ARVSurvivorCharacter* Character,FVector& Position,class UPrimitiveComponent*& Floor) const;
    bool ValidateLyingPosition(ARVSurvivorCharacter* Character) const;
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& Out) const override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
    virtual bool CanInteract_Implementation(APawn* Pawn) const override;
    virtual FText GetInteractionText_Implementation(APawn* Pawn) const override;
    virtual void CompleteInteraction_Implementation(APawn* Pawn) override;
    bool CanContinueRest(const ARVSurvivorCharacter* Character) const;
    void ReleaseAuthority(ARVPlayerState* Player);
};
