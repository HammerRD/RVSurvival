#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Mechanical/RVMechanicalProfile.h"
#include "RVCoolingComponent.generated.h"

USTRUCT(BlueprintType)
struct FRVCoolingState
{
    GENERATED_BODY()
    UPROPERTY(BlueprintReadOnly, SaveGame) float RadiatorCondition=1;
    UPROPERTY(BlueprintReadOnly, SaveGame) double CoolantLitres=12;
    UPROPERTY(BlueprintReadOnly, SaveGame) double TemperatureC=20;
    UPROPERTY(BlueprintReadOnly, SaveGame) double PatchLeakMultiplier=1;
    UPROPERTY(BlueprintReadOnly, SaveGame) bool bTemporaryPatch=false;
    UPROPERTY(BlueprintReadOnly) double LeakLitresPerSecond=0;
    UPROPERTY(BlueprintReadOnly) double CoolingEffectiveness=1;
    UPROPERTY(BlueprintReadOnly) ERVThermalStatus Status=ERVThermalStatus::Normal;
    UPROPERTY(BlueprintReadOnly) FGameplayTagContainer Faults;
};

USTRUCT(BlueprintType)
struct FRVEngineConditionState
{
    GENERATED_BODY()
    UPROPERTY(BlueprintReadOnly, SaveGame) float Condition=1;
    UPROPERTY(BlueprintReadOnly, SaveGame) bool bShutdown=false;
    UPROPERTY(BlueprintReadOnly) float OutputScale=1;
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE(FRVMechanicalChanged);

/** Machine-specific balances; engine transport/ticking/lifetime remain native. */
UCLASS(ClassGroup=(RV), meta=(BlueprintSpawnableComponent))
class RVSURVIVAL_API URVCoolingComponent : public UActorComponent
{
    GENERATED_BODY()
public:
    URVCoolingComponent();
    virtual void BeginPlay() override;
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& Out) const override;
    virtual void TickComponent(float DT,ELevelTick Type,FActorComponentTickFunction* Function) override;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) TObjectPtr<URVMechanicalProfile> Profile;
    UPROPERTY(EditAnywhere, Replicated, BlueprintReadOnly) FRVMechanicalTuning Tuning;
    UPROPERTY(ReplicatedUsing=OnRep_State, BlueprintReadOnly) FRVCoolingState Cooling;
    UPROPERTY(ReplicatedUsing=OnRep_State, BlueprintReadOnly) FRVEngineConditionState Engine;
    UPROPERTY(Replicated, BlueprintReadOnly) int32 ServiceRevision=0;
    UPROPERTY(BlueprintAssignable) FRVMechanicalChanged OnStateChanged;
    void AdvanceAuthority(double Seconds,bool Running,double Load,double SpeedCmS);
    double AddCoolantAuthority(double Litres);
    void ApplyRepairAuthority(const FRVRepairDefinition& Repair);
    UFUNCTION(BlueprintPure) bool CanService() const;
    UFUNCTION(BlueprintCallable) bool DebugSetState(float Radiator,double Coolant,double Temperature,float EngineCondition);
    UFUNCTION(BlueprintCallable) bool DebugAdvance(double Seconds,bool Running,double Load,double SpeedCmS);
    UFUNCTION(BlueprintCallable) bool DebugSetTimeScale(double Scale);
private:
    UFUNCTION() void OnRep_State();
    void DeriveState();
    double TimeScale=1;
};
