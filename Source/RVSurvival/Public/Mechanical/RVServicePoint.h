#pragma once
#include "CoreMinimal.h"
#include "Inventory/RVWorldItem.h"
#include "RVServicePoint.generated.h"
class ARVMechanicalMotorhome;
class ARVPlayerController;
UCLASS()
class RVSURVIVAL_API ARVServicePoint : public ARVInventoryInteractable
{
    GENERATED_BODY()
public:
    ARVServicePoint();
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& Out)const override;
    virtual void Tick(float DT)override;
    virtual void EndPlay(EEndPlayReason::Type Reason)override;
    virtual FText GetInteractionText_Implementation(APawn* Pawn)const override;
    virtual void CompleteInteraction_Implementation(APawn* Pawn)override;
    UPROPERTY(Replicated,BlueprintReadOnly) TObjectPtr<ARVMechanicalMotorhome> Vehicle;
    UPROPERTY(Replicated,BlueprintReadOnly) TObjectPtr<APlayerState> RepairPlayer;
    UPROPERTY(Replicated,BlueprintReadOnly) FName ActiveRepair;
    UPROPERTY(Replicated,BlueprintReadOnly) double RepairStart=0;
    UPROPERTY(Replicated,BlueprintReadOnly) float RepairDuration=0;
    UPROPERTY(Replicated,BlueprintReadOnly) int32 Revision=0;
    bool HasAccess(const ARVPlayerController* PC)const;
    void RequestAuthority(ARVPlayerController* PC,FName Action,int32 Expected,FGuid Item,int32 ItemRevision);
    void CancelAuthority(const FString& Reason);
private:
    void FinishRepair();
    FTimerHandle Completion;
    TWeakObjectPtr<ARVPlayerController> RepairController;
    int32 ExpectedMechanicalRevision=-1;
};
