#pragma once
#include "CoreMinimal.h"
#include "Interaction/RVTestInteractable.h"
#include "RVInteriorStation.generated.h"
/** Placeholder interaction endpoint only. Future station systems can compose their own behavior. */
UCLASS()
class RVSURVIVAL_API ARVInteriorStation : public ARVTestInteractable
{
    GENERATED_BODY()
public:
    ARVInteriorStation();
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& Out) const override;
    virtual FText GetInteractionText_Implementation(APawn* Interactor) const override;
    UPROPERTY(Replicated, BlueprintReadOnly, Category="RV|Station") FName StationName;
};
