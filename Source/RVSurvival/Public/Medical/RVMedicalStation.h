#pragma once
#include "CoreMinimal.h"
#include "Interaction/RVInteriorStation.h"
#include "RVMedicalStation.generated.h"
UCLASS()
class RVSURVIVAL_API ARVMedicalStation : public ARVInteriorStation
{
    GENERATED_BODY()
public:
    ARVMedicalStation();
    UPROPERTY(EditAnywhere, Replicated, BlueprintReadOnly) TObjectPtr<class URVContainerComponent> LinkedStorage;
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;
    virtual void CompleteInteraction_Implementation(APawn* Pawn) override;
    virtual FText GetInteractionText_Implementation(APawn* Pawn) const override;
    bool IsReachable(const class ARVSurvivorCharacter* Character) const;
};
