#pragma once
#include "CoreMinimal.h"
#include "Vehicles/RVInteriorMotorhome.h"
#include "RVSystemsMotorhome.generated.h"
class URVFuelComponent;
class URVBatteryComponent;
class URVElectricalComponent;
/** Gate 6 composition, using the accepted art/seat/movement architecture. */
UCLASS(Blueprintable)
class RVSURVIVAL_API ARVSystemsMotorhome : public ARVInteriorMotorhome
{
    GENERATED_BODY()
public:
    ARVSystemsMotorhome(const FObjectInitializer& Init);
    virtual void BeginPlay() override;
    virtual void Tick(float Seconds) override;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<URVFuelComponent> PropulsionFuel;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<URVFuelComponent> GeneratorFuel;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<URVBatteryComponent> HouseBattery;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<URVBatteryComponent> ChassisBattery;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<URVElectricalComponent> Electrical;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<class UPointLightComponent> FrontLight;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<class UPointLightComponent> RearLight;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) FVector FuelFillLocation=FVector(-155,-134,125);
    UPROPERTY(EditAnywhere, BlueprintReadOnly) FVector PowerPanelLocation=FVector(-90,85,150);
private:
    double SimulationAccumulator=0;
    float ConfiguredEngineTorque=0;
    bool bTorqueEnabled=true;
};
