#include "Interaction/RVInteractionTargetPresentationComponent.h"
#include "Vehicles/RVInteriorMotorhome.h"
#include "Components/StaticMeshComponent.h"
#include "Components/TextRenderComponent.h"
#include "HAL/IConsoleManager.h"
static TAutoConsoleVariable<int32> DebugTargets(TEXT("rv.Interaction.DebugTargets"),0,TEXT("Development-only visible RV interaction target geometry"));
URVInteractionTargetPresentationComponent::URVInteractionTargetPresentationComponent()
{ PrimaryComponentTick.bCanEverTick=true; PrimaryComponentTick.TickInterval=.2f; }
void URVInteractionTargetPresentationComponent::TickComponent(float Delta,ELevelTick Type,FActorComponentTickFunction* Function)
{
    Super::TickComponent(Delta,Type,Function);
    if (!Cast<ARVInteriorMotorhome>(GetOwner()->GetAttachParentActor()) && !Cast<ARVInteriorMotorhome>(GetOwner()->GetOwner())) return;
    bool Hide=true;
#if !(UE_BUILD_SHIPPING || UE_BUILD_TEST)
    Hide=DebugTargets.GetValueOnGameThread()==0;
#endif
    for (auto* Part:TInlineComponentArray<UStaticMeshComponent*>(GetOwner())) Part->SetHiddenInGame(Hide);
    for (auto* Part:TInlineComponentArray<UTextRenderComponent*>(GetOwner())) Part->SetHiddenInGame(Hide);
}
