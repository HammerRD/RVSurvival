#pragma once
#include "CoreMinimal.h"
#include "Animation/AnimInstance.h"
#include "RVHumanoidAnimInstance.generated.h"
/** Game-thread inputs for a normal Animation Blueprint with built-in animation nodes. */
UCLASS(Blueprintable,BlueprintType)
class RVSURVIVAL_API URVHumanoidAnimInstance : public UAnimInstance
{
    GENERATED_BODY()
public:
    virtual void NativeUpdateAnimation(float Delta) override;
    UPROPERTY(BlueprintReadOnly,Category="Presentation") float GroundSpeed=0;
    UPROPERTY(BlueprintReadOnly,Category="Presentation") float Direction=0;
    UPROPERTY(BlueprintReadOnly,Category="Presentation") int32 PoseIndex=0;
    UPROPERTY(BlueprintReadOnly,Category="Presentation") float ClimbPlayRate=1;
    UPROPERTY(BlueprintReadOnly,Category="Presentation") bool bWeaponReady=false;
    UPROPERTY(BlueprintReadOnly,Category="Presentation") bool bOneHandedMelee=false;
    UPROPERTY(BlueprintReadOnly,Category="Presentation") float WeaponSupportIKAlpha=0;
    UPROPERTY(EditDefaultsOnly,BlueprintReadOnly,Category="Presentation") TObjectPtr<class UBlendSpace> DefaultWeaponLocomotion;
    UPROPERTY(EditDefaultsOnly,BlueprintReadOnly,Category="Presentation") TObjectPtr<class UBlendSpace> DefaultWeaponAim;
    UPROPERTY(EditDefaultsOnly,BlueprintReadOnly,Category="Presentation") TObjectPtr<class UAnimSequence> DefaultToolReady;
    UPROPERTY(BlueprintReadOnly,Category="Presentation") TObjectPtr<class UBlendSpace> WeaponLocomotion;
    UPROPERTY(BlueprintReadOnly,Category="Presentation") TObjectPtr<class UBlendSpace> WeaponAim;
    UPROPERTY(BlueprintReadOnly,Category="Presentation") TObjectPtr<class UAnimSequence> WeaponReadyPose;
    UPROPERTY(BlueprintReadOnly,Category="Presentation") float AimPitch=0;
    UPROPERTY(BlueprintReadOnly,Category="Presentation") float NormalizedAimPitch=0;
    UPROPERTY(BlueprintReadOnly,Category="Presentation") float WeaponGripIKAlpha=0;
    UPROPERTY(BlueprintReadOnly,Category="Presentation") FVector WeaponRightHandTarget=FVector::ZeroVector;
    UPROPERTY(BlueprintReadOnly,Category="Presentation") FVector WeaponLeftHandTarget=FVector::ZeroVector;
    UPROPERTY(BlueprintReadOnly,Category="Presentation") FRotator WeaponRightHandRotation=FRotator::ZeroRotator;
private:
    bool bWasFalling=false;
    float LandingRemaining=0;
};

