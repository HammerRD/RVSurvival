#include "Player/RVPlayerState.h"
#include "Survival/RVNeedsComponent.h"
#include "AbilitySystemComponent.h"
#include "Medical/RVMedicalAttributes.h"
#include "Medical/RVHealthComponent.h"
ARVPlayerState::ARVPlayerState()
{
    Needs = CreateDefaultSubobject<URVNeedsComponent>(TEXT("Needs"));
    MedicalAbilitySystem = CreateDefaultSubobject<UAbilitySystemComponent>(TEXT("MedicalAbilitySystem"));
    MedicalAbilitySystem->SetIsReplicated(true);
    MedicalAbilitySystem->SetReplicationMode(EGameplayEffectReplicationMode::Mixed);
    MedicalAttributes = CreateDefaultSubobject<URVMedicalAttributes>(TEXT("MedicalAttributes"));
    Health = CreateDefaultSubobject<URVHealthComponent>(TEXT("Health"));
    SetNetUpdateFrequency(10);
}
void ARVPlayerState::BeginPlay()
{
    Super::BeginPlay();
    // Passive medical effects target persistent player state, never the possessed RV.
    MedicalAbilitySystem->InitAbilityActorInfo(this,this);
}
UAbilitySystemComponent* ARVPlayerState::GetAbilitySystemComponent() const { return MedicalAbilitySystem; }
void ARVPlayerState::CopyProperties(APlayerState* Destination)
{
    Super::CopyProperties(Destination);
    if (auto* Target = Cast<ARVPlayerState>(Destination)) Needs->CopyPersistentValuesTo(Target->Needs);
}
