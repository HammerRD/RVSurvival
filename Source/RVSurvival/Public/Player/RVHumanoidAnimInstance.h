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
    UPROPERTY(BlueprintReadOnly,Category="Presentation") float AimPitch=0;
    UPROPERTY(BlueprintReadOnly,Category="Presentation") float NormalizedAimPitch=0;
private:
    bool bWasFalling=false;
    float LandingRemaining=0;
};

