#pragma once
#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "RVWeaponPresentationProfile.generated.h"

UENUM(BlueprintType)
enum class ERVWeaponFamily : uint8 { Handgun, OneHandedMelee, LongGun, TwoHandedMelee };

/** Render-only family defaults. Item definitions retain individual mesh/sight/grip overrides. */
UCLASS(BlueprintType)
class RVSURVIVAL_API URVWeaponPresentationProfile : public UPrimaryDataAsset
{
    GENERATED_BODY()
public:
    UPROPERTY(EditDefaultsOnly,BlueprintReadOnly) ERVWeaponFamily Family=ERVWeaponFamily::Handgun;
    UPROPERTY(EditDefaultsOnly,BlueprintReadOnly) bool bSupportHand=true;
    UPROPERTY(EditDefaultsOnly,BlueprintReadOnly) bool bOwnerReadyIK=true;
    UPROPERTY(EditDefaultsOnly,BlueprintReadOnly) float UpperBodyPitchScale=1;
    UPROPERTY(EditDefaultsOnly,BlueprintReadOnly,meta=(ClampMin="0",ClampMax="1")) float OwnerTorsoPitchScale=.25f;
    // Character-local reference; animation evaluates targets in mesh component space.
    UPROPERTY(EditDefaultsOnly,BlueprintReadOnly) FTransform ReadyHand=FTransform(FRotator(0,180,0),FVector(45,8,65));
    UPROPERTY(EditDefaultsOnly,BlueprintReadOnly) FVector AimPivot=FVector(0,0,60);
    UPROPERTY(EditDefaultsOnly,BlueprintReadOnly) FTransform FirstPersonOffset;
    UPROPERTY(EditDefaultsOnly,BlueprintReadOnly) FTransform ThirdPersonOffset;
    UPROPERTY(EditDefaultsOnly,BlueprintReadOnly) FTransform HolsterOffset;
    UPROPERTY(EditDefaultsOnly,BlueprintReadOnly) TObjectPtr<class UAnimSequence> ReadyPose;
    UPROPERTY(EditDefaultsOnly,BlueprintReadOnly) TObjectPtr<class UBlendSpace> AimOffset;
    UPROPERTY(EditDefaultsOnly,BlueprintReadOnly) TObjectPtr<class UBlendSpace> LocomotionOverlay;
    UPROPERTY(EditDefaultsOnly,BlueprintReadOnly) TArray<TObjectPtr<class UAnimMontage>> LightAttacks;
    UPROPERTY(EditDefaultsOnly,BlueprintReadOnly,meta=(ClampMin="0",ClampMax=".5")) float LightAttackHitSeconds=.18f;
};
