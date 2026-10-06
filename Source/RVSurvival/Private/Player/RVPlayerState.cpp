#include "Player/RVPlayerState.h"
#include "Survival/RVNeedsComponent.h"
ARVPlayerState::ARVPlayerState()
{
    Needs = CreateDefaultSubobject<URVNeedsComponent>(TEXT("Needs"));
    SetNetUpdateFrequency(10);
}
void ARVPlayerState::CopyProperties(APlayerState* Destination)
{
    Super::CopyProperties(Destination);
    if (auto* Target = Cast<ARVPlayerState>(Destination)) Needs->CopyPersistentValuesTo(Target->Needs);
}
