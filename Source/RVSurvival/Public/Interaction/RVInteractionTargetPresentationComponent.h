#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "RVInteractionTargetPresentationComponent.generated.h"
/** Hide debug target meshes on mobile bases, retaining query collision and optional local development visualization. */
UCLASS()
class RVSURVIVAL_API URVInteractionTargetPresentationComponent : public UActorComponent
{
    GENERATED_BODY()
public:
    URVInteractionTargetPresentationComponent();
    virtual void TickComponent(float Delta,ELevelTick Type,FActorComponentTickFunction* Function) override;
};
