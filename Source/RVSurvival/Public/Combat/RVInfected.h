#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "Medical/RVMedicalProfile.h"
#include "RVInfected.generated.h"
UENUM(BlueprintType)
enum class ERVInfectedState : uint8 { Idle,Wander,Investigate,Chase,Attack,Dead };
UCLASS()
class RVSURVIVAL_API ARVInfected : public ACharacter
{
    GENERATED_BODY()
public:
    ARVInfected();
    virtual void OnConstruction(const FTransform& Transform) override;
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& Out) const override;
    virtual float TakeDamage(float Amount,const FDamageEvent& Event,AController* Instigator,AActor* Causer) override;
    UPROPERTY(EditAnywhere,BlueprintReadOnly) TObjectPtr<class URVInfectedProfile> Profile;
    UPROPERTY(ReplicatedUsing=OnRep_State,BlueprintReadOnly) ERVInfectedState State=ERVInfectedState::Idle;
    UPROPERTY(Replicated,BlueprintReadOnly) float Vitality=65;
    UPROPERTY(Replicated,BlueprintReadOnly) bool bLegInjured=false;
    UPROPERTY(Replicated,BlueprintReadOnly) int32 AttackSequence=0;
    UPROPERTY(Replicated,BlueprintReadOnly) int32 DeathSequence=0;
    void BeginAttack(AActor* Victim);
    UFUNCTION() void OnRep_State();
    const URVInfectedProfile* Tuning() const;
private:
    void ConfigureVisual();
    void CompleteAttack();
    TWeakObjectPtr<AActor> AttackVictim;
    FTimerHandle AttackTimer;
    double NextAttack=0;
};
