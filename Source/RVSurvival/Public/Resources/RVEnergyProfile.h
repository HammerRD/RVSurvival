#pragma once
#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "Resources/RVBatteryComponent.h"
#include "RVEnergyProfile.generated.h"
UENUM(BlueprintType)
enum class ERVPowerSource : uint8 { Shore, Generator, Alternator, Solar, Battery };
USTRUCT(BlueprintType)
struct FRVElectricalLoad
{
    GENERATED_BODY()
    UPROPERTY(EditAnywhere, BlueprintReadOnly, SaveGame) FName Id;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) FText DisplayName;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) double Watts=20;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) ERVPowerDomain Domain=ERVPowerDomain::House;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) int32 Priority=10;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, SaveGame) bool bEnabled=false;
    UPROPERTY(BlueprintReadOnly) bool bPowered=false;
};
USTRUCT(BlueprintType)
struct FRVEnergyTuning
{
    GENERATED_BODY()
    UPROPERTY(EditAnywhere, BlueprintReadOnly) double IdleLitresPerHour=1.5;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) double ThrottleLitresPerHour=14;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) double RoadLitresPerHour=4;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) double GeneratorLitresPerHour=1.2;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) double GeneratorWatts=1800;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) bool bSharedGeneratorFuel=true;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) double GeneratorReserveLitres=20;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) double AlternatorHouseWatts=500;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) double AlternatorChassisWatts=250;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) double SolarPeakWatts=300;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) double ShoreWatts=2000;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) double GeneratorNoiseStrength=1;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) TArray<ERVPowerSource> SourcePriority={ERVPowerSource::Shore,ERVPowerSource::Generator,ERVPowerSource::Alternator,ERVPowerSource::Solar,ERVPowerSource::Battery};
    UPROPERTY(EditAnywhere, BlueprintReadOnly) TArray<FRVElectricalLoad> Loads;
};
UCLASS(BlueprintType)
class RVSURVIVAL_API URVEnergyProfile : public UPrimaryDataAsset
{
    GENERATED_BODY()
public:
    UPROPERTY(EditAnywhere, BlueprintReadOnly) FRVEnergyTuning Values;
};
