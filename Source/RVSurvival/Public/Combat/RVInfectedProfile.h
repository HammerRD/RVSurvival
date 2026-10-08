#pragma once
#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "RVInfectedProfile.generated.h"
UCLASS(BlueprintType)
class RVSURVIVAL_API URVInfectedProfile : public UPrimaryDataAsset
{
    GENERATED_BODY()
public:
    UPROPERTY(EditAnywhere,BlueprintReadOnly) TObjectPtr<class USkeletalMesh> Body;
    UPROPERTY(EditAnywhere,BlueprintReadOnly) TSubclassOf<class UAnimInstance> AnimationClass;
    UPROPERTY(EditAnywhere,BlueprintReadOnly) TObjectPtr<class URVCharacterVisualProfile> BodyMapping;
    UPROPERTY(EditAnywhere,BlueprintReadOnly) float Vitality=65;
    UPROPERTY(EditAnywhere,BlueprintReadOnly) float SightRadius=1800;
    UPROPERTY(EditAnywhere,BlueprintReadOnly) float HearingRadius=5000;
    UPROPERTY(EditAnywhere,BlueprintReadOnly) float SightAngle=65;
    UPROPERTY(EditAnywhere,BlueprintReadOnly) float ChaseSpeed=320;
    UPROPERTY(EditAnywhere,BlueprintReadOnly) float WanderRadius=450;
    UPROPERTY(EditAnywhere,BlueprintReadOnly) float AttackRange=145;
    UPROPERTY(EditAnywhere,BlueprintReadOnly) float AttackWindup=.7f;
    UPROPERTY(EditAnywhere,BlueprintReadOnly) float AttackCooldown=1.7f;
    UPROPERTY(EditAnywhere,BlueprintReadOnly) float AttackDamage=15;
    UPROPERTY(EditAnywhere,BlueprintReadOnly) float InjurySeverity=2;
    UPROPERTY(EditAnywhere,BlueprintReadOnly) float Contamination=.55f;
    UPROPERTY(EditAnywhere,BlueprintReadOnly) float HeadMultiplier=3;
    UPROPERTY(EditAnywhere,BlueprintReadOnly) float LimbMultiplier=.65f;
};
