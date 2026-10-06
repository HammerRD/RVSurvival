#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "RVSeatPoseComponent.generated.h"
/** Replaceable rear-seat presentation driven by replicated native seat attachment. */
UCLASS()
class RVSURVIVAL_API URVSeatPoseComponent : public UActorComponent
{
    GENERATED_BODY()
public:
    URVSeatPoseComponent();
    virtual void BeginPlay() override;
    virtual void TickComponent(float Delta,ELevelTick Type,FActorComponentTickFunction* Function) override;
private:
    UPROPERTY(Transient) TArray<TObjectPtr<class UStaticMeshComponent>> Parts;
    TArray<TPair<TWeakObjectPtr<class UPrimitiveComponent>,bool>> PreviousVisibility;
    bool bActive=false;
};
