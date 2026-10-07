#pragma once
#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "GameplayTagContainer.h"
#include "RVMechanicalProfile.generated.h"

UENUM(BlueprintType)
enum class ERVThermalStatus : uint8 { Normal, Warm, Hot, Overheating, Critical };

USTRUCT(BlueprintType)
struct FRVRepairRequirement
{
    GENERATED_BODY()
    UPROPERTY(EditAnywhere, BlueprintReadOnly) FGameplayTag Tag;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) FText DisplayName;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) int32 Quantity=1;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) bool bConsume=true;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) float MinimumCondition=.1f;
};

USTRUCT(BlueprintType)
struct FRVRepairDefinition
{
    GENERATED_BODY()
    UPROPERTY(EditAnywhere, BlueprintReadOnly) FName Id;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) FText DisplayName;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) float DurationSeconds=8;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) TArray<FRVRepairRequirement> Requirements;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) float RadiatorConditionTarget=.65f;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) float EngineConditionTarget=0;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) double LeakMultiplier=.15;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) bool bTemporary=true;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) bool bAffectsCooling=true;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) bool bAffectsEngine=false;
};

USTRUCT(BlueprintType)
struct FRVMechanicalTuning
{
    GENERATED_BODY()
    UPROPERTY(EditAnywhere, BlueprintReadOnly) double CoolantCapacityLitres=12;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) double LowCoolantFraction=.25;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) double AmbientC=20;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) double MaximumTemperatureC=200;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) double IdleHeatCPerSecond=.25;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) double LoadHeatCPerSecond=1.0;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) double PassiveCoolingPerSecond=.0015;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) double RadiatorCoolingPerSecond=.009;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) double AirflowBonus=1.0;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) double MinorLeakLitresPerSecond=.001;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) double MajorLeakLitresPerSecond=.015;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) float MinorDamageThreshold=.85f;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) float MajorDamageThreshold=.35f;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) double WarmC=95;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) double HotC=105;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) double OverheatC=115;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) double CriticalC=130;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) double SafeServiceC=60;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) float EngineDamagePerSecond=.0004f;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) float ShutdownCondition=.1f;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) float LimpOutput=.35f;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) float RestartCondition=.3f;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) double RestartTemperatureC=105;
};

UCLASS(BlueprintType)
class RVSURVIVAL_API URVMechanicalProfile : public UPrimaryDataAsset
{
    GENERATED_BODY()
public:
    UPROPERTY(EditAnywhere, BlueprintReadOnly) FRVMechanicalTuning Tuning;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) TArray<FRVRepairDefinition> Repairs;
};
