#pragma once
#include "CoreMinimal.h"
#include "UObject/Interface.h"
#include "RVInteractable.generated.h"
class APawn;
UINTERFACE(BlueprintType)
class RVSURVIVAL_API URVInteractable : public UInterface { GENERATED_BODY() };
/** Queries must be side-effect free. Lifecycle calls execute only on authority.
 * Complete must revalidate mutable object state; cancellation must be safe to repeat. */
class RVSURVIVAL_API IRVInteractable
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintNativeEvent, BlueprintCallable, Category="RV|Interaction")
    bool CanInteract(APawn* Interactor) const;
    UFUNCTION(BlueprintNativeEvent, BlueprintCallable, Category="RV|Interaction")
    FText GetInteractionText(APawn* Interactor) const;
    UFUNCTION(BlueprintNativeEvent, BlueprintCallable, Category="RV|Interaction")
    float GetInteractionDuration(APawn* Interactor) const;
    UFUNCTION(BlueprintNativeEvent, Category="RV|Interaction")
    void StartInteraction(APawn* Interactor);
    UFUNCTION(BlueprintNativeEvent, Category="RV|Interaction")
    void CompleteInteraction(APawn* Interactor);
    UFUNCTION(BlueprintNativeEvent, Category="RV|Interaction")
    void CancelInteraction(APawn* Interactor);
};
