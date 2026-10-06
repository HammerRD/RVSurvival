#pragma once
#include "CoreMinimal.h"
#include "Resources/RVFuelComponent.h"
#include "RVBatteryComponent.generated.h"
UENUM(BlueprintType)
enum class ERVPowerDomain : uint8 { House, Chassis };
/** Watt-hours; charge/discharge ceilings expressed in watts. */
UCLASS(ClassGroup=(RV),meta=(BlueprintSpawnableComponent))
class RVSURVIVAL_API URVBatteryComponent : public UActorComponent
{
    GENERATED_BODY()
public:
    URVBatteryComponent();
    virtual void BeginPlay() override;
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& Out) const override;
    UPROPERTY(EditAnywhere, Replicated, BlueprintReadOnly) ERVPowerDomain Domain=ERVPowerDomain::House;
    UPROPERTY(EditAnywhere, Replicated, BlueprintReadOnly) double CapacityWh=2400;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) double InitialWh=1800;
    UPROPERTY(EditAnywhere, Replicated, BlueprintReadOnly) double MaxChargeWatts=800;
    UPROPERTY(EditAnywhere, Replicated, BlueprintReadOnly) double MaxDischargeWatts=1500;
    UPROPERTY(ReplicatedUsing=OnRep_Energy, BlueprintReadOnly, SaveGame) double EnergyWh=0;
    UPROPERTY(BlueprintAssignable) FRVResourceChanged OnEnergyChanged;
    UFUNCTION(BlueprintPure) double GetStateOfCharge() const { return CapacityWh>0?EnergyWh/CapacityWh:0; }
    double ChargeAuthority(double Wh, double Hours);
    double DischargeAuthority(double Wh, double Hours);
    UFUNCTION(BlueprintCallable) bool DebugSetEnergy(double Wh);
private:
    UFUNCTION() void OnRep_Energy();
};
