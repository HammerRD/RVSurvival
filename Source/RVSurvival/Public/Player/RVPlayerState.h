#pragma once
#include "CoreMinimal.h"
#include "GameFramework/PlayerState.h"
#include "AbilitySystemInterface.h"
#include "RVPlayerState.generated.h"
class URVNeedsComponent;
/** Gate 1 framework boundary; later gates add only the state owned by this role. */
UCLASS()
class RVSURVIVAL_API ARVPlayerState : public APlayerState, public IAbilitySystemInterface
{
    GENERATED_BODY()
public:
    ARVPlayerState();
    virtual void BeginPlay() override;
    virtual UAbilitySystemComponent* GetAbilitySystemComponent() const override;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<class UAbilitySystemComponent> MedicalAbilitySystem;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<class URVMedicalAttributes> MedicalAttributes;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<class URVHealthComponent> Health;
    virtual void CopyProperties(APlayerState* Destination) override;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<URVNeedsComponent> Needs;
};
