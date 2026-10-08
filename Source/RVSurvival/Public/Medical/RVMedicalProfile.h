#pragma once
#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "GameplayTagContainer.h"
#include "RVMedicalProfile.generated.h"

UENUM(BlueprintType)
enum class ERVBodyRegion : uint8 { Head, Torso, LeftArm, RightArm, LeftLeg, RightLeg };
UENUM(BlueprintType)
enum class ERVInjuryKind : uint8 { Wound, Fracture, Burn, Concussion };
UENUM(BlueprintType)
enum class ERVMedicalLifeState : uint8 { Active, Downed, Terminal };
UENUM(BlueprintType)
enum class ERVTreatmentKind : uint8 { Bandage, PressureDressing, Antiseptic, Splint, BurnDressing, Analgesic, Revive };

USTRUCT(BlueprintType)
struct FRVInjuryInstance
{
    GENERATED_BODY()
    UPROPERTY(BlueprintReadOnly, SaveGame) FGuid Id;
    UPROPERTY(BlueprintReadOnly, SaveGame) ERVInjuryKind Kind=ERVInjuryKind::Wound;
    UPROPERTY(BlueprintReadOnly, SaveGame) FGameplayTag InjuryTag;
    UPROPERTY(BlueprintReadOnly, SaveGame) ERVBodyRegion Region=ERVBodyRegion::Torso;
    UPROPERTY(BlueprintReadOnly, SaveGame) float Severity=1;
    UPROPERTY(BlueprintReadOnly, SaveGame) float BleedingPerMinute=0;
    UPROPERTY(BlueprintReadOnly, SaveGame) float Pain=0;
    UPROPERTY(BlueprintReadOnly, SaveGame) float InfectionRisk=0;
    UPROPERTY(BlueprintReadOnly, SaveGame) float AgeSeconds=0;
    UPROPERTY(BlueprintReadOnly, SaveGame) float Healing=0;
    UPROPERTY(BlueprintReadOnly, SaveGame) bool bStabilized=false;
    UPROPERTY(BlueprintReadOnly, SaveGame) bool bCleaned=false;
    UPROPERTY(BlueprintReadOnly, SaveGame) bool bTreated=false;
    UPROPERTY(BlueprintReadOnly, SaveGame) int32 Revision=0;
};

/** Item capability metadata; no dispatch by item display name. */
USTRUCT(BlueprintType)
struct FRVMedicalSupplyMetadata
{
    GENERATED_BODY()
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) bool bMedicalSupply=false;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) ERVTreatmentKind Treatment=ERVTreatmentKind::Bandage;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, meta=(ClampMin="0.1")) float DurationSeconds=4;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, meta=(ClampMin="0",ClampMax="1")) float MinimumCondition=.25f;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) bool bRequiresStation=false;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) bool bRequiresParked=false;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, meta=(ClampMin="1",ClampMax="3")) float MaximumSeverity=2;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, meta=(ClampMin="0",ClampMax="1")) float BleedingReduction=1;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, meta=(ClampMin="0")) float MedicationSeconds=300;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, meta=(ClampMin="0",ClampMax="100")) float PainRelief=25;
};

UCLASS(BlueprintType)
class RVSURVIVAL_API URVMedicalProfile : public UPrimaryDataAsset
{
    GENERATED_BODY()
public:
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) float MinorBleedPerMinute=.5f;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) float ModerateBleedPerMinute=3;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) float SevereBleedPerMinute=10;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) float DownedBlood=25;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) float CriticalBlood=40;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) float BloodRecoveryPerMinute=.15f;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) float HealingPerHour=.05f;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) float DownedTimeoutSeconds=600;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) float TreatmentRangeCm=200;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) float UntreatedLegSpeedScale=.35f;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) float SplintedLegSpeedScale=.65f;
};
