#pragma once
#include "CoreMinimal.h"
#include "Resources/RVEnergyProfile.h"
#include "RVElectricalComponent.generated.h"
USTRUCT(BlueprintType)
struct FRVPowerFlow
{
    GENERATED_BODY()
    UPROPERTY(BlueprintReadOnly) double RequestedWatts=0;
    UPROPERTY(BlueprintReadOnly) double SuppliedWatts=0;
    UPROPERTY(BlueprintReadOnly) double HouseBatteryWatts=0;
    UPROPERTY(BlueprintReadOnly) double ChassisChargeWatts=0;
    UPROPERTY(BlueprintReadOnly) double AvailableSourceWatts=0;
    UPROPERTY(BlueprintReadOnly) TArray<ERVPowerSource> ActiveSources;
};
UCLASS(ClassGroup=(RV),meta=(BlueprintSpawnableComponent))
class RVSURVIVAL_API URVElectricalComponent : public UActorComponent
{
    GENERATED_BODY()
public:
    URVElectricalComponent();
    virtual void BeginPlay() override;
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& Out) const override;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) TObjectPtr<URVEnergyProfile> Profile;
    UPROPERTY(EditAnywhere, Replicated, BlueprintReadOnly) FRVEnergyTuning Tuning;
    UPROPERTY(ReplicatedUsing=OnRep_Power, BlueprintReadOnly) TArray<FRVElectricalLoad> Loads;
    UPROPERTY(ReplicatedUsing=OnRep_Power, BlueprintReadOnly, SaveGame) bool bGeneratorRunning=false;
    UPROPERTY(Replicated, BlueprintReadOnly, SaveGame) bool bEngineIdleRequested=false;
    UPROPERTY(Replicated, BlueprintReadOnly, SaveGame) double SolarInput=0;
    UPROPERTY(Replicated, BlueprintReadOnly, SaveGame) bool bShoreConnected=false;
    UPROPERTY(Replicated, BlueprintReadOnly) bool bEngineRunning=false;
    UPROPERTY(Replicated, BlueprintReadOnly) FRVPowerFlow Flow;
    UPROPERTY(Replicated, BlueprintReadOnly) int32 ControlRevision=0;
    UPROPERTY(BlueprintAssignable) FRVResourceChanged OnPowerChanged;
    UPROPERTY(BlueprintAssignable) FRVResourceChanged OnGeneratorNoiseChanged;
    UFUNCTION(BlueprintPure) bool IsLoadPowered(FName Id) const;
    UFUNCTION(BlueprintPure) bool HasHousePower() const;
    UFUNCTION(BlueprintPure) double GetGeneratorNoiseStrength() const { return bGeneratorRunning?Tuning.GeneratorNoiseStrength:0; }
    bool SetControlAuthority(FName Control, bool Enabled, int32 ExpectedRevision, FString& Error);
    void AdvanceAuthority(double Seconds, bool EngineOperating, double Throttle, double SpeedCmS);
    UFUNCTION(BlueprintCallable) bool DebugAdvance(double Seconds, bool EngineOperating, double Throttle, double SpeedCmS);
    UFUNCTION(BlueprintCallable) bool DebugSetSolar(double Scalar);
    UFUNCTION(BlueprintCallable) bool DebugSetTimeScale(double Scalar);
private:
    UFUNCTION() void OnRep_Power();
    double TimeScale=1;
    friend class ARVSystemsMotorhome;
};
