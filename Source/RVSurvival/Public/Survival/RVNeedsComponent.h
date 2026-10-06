#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Engine/DataAsset.h"
#include "GameplayTagContainer.h"
#include "RVNeedsComponent.generated.h"

class ARVRestPoint;
class ARVSurvivorCharacter;

UENUM(BlueprintType)
enum class ERVRestMode : uint8 { Awake, Resting, Sleeping };

/** Hours are simulation hours; acceleration never changes physics or RPC cooldowns. */
USTRUCT(BlueprintType)
struct FRVNeedsTuning
{
    GENERATED_BODY()
    UPROPERTY(EditAnywhere, BlueprintReadOnly) float Maximum = 100;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) float StartingNutrition = 90;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) float StartingHydration = 90;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) float StartingFatigue = 10;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) float NutritionPerHour = 6;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) float HydrationPerHour = 12;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) float FatiguePerHour = 4;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) float RestRecoveryPerHour = 10;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) float SleepRecoveryPerHour = 25;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) float WalkingMultiplier = 1.3f;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) float HeavyCarryMultiplier = 1.25f;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) float DrivingMultiplier = 1.05f;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) float PassengerMultiplier = .8f;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) float RestMetabolism = .65f;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) float SleepMetabolism = .5f;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) float NutritionWarning = 30;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) float HydrationWarning = 35;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) float FatigueWarning = 60;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) float NutritionCritical = 10;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) float HydrationCritical = 12;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) float FatigueCritical = 85;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) float HungrySpeedScale = .8f;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) float DehydratedSpeedScale = .6f;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) float ExhaustedSpeedScale = .65f;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) float HungerReserveLossPerHour = 1;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) float ThirstReserveLossPerHour = 5;
};

UCLASS(BlueprintType)
class RVSURVIVAL_API URVNeedsProfile : public UPrimaryDataAsset
{
    GENERATED_BODY()
public:
    UPROPERTY(EditAnywhere, BlueprintReadOnly) FRVNeedsTuning Values;
};

/** Plain serializable values. Rest reservations are deliberately not persistent identity. */
USTRUCT(BlueprintType)
struct FRVNeedsState
{
    GENERATED_BODY()
    UPROPERTY(SaveGame, BlueprintReadOnly) float Nutrition = 90;
    UPROPERTY(SaveGame, BlueprintReadOnly) float Hydration = 90;
    UPROPERTY(SaveGame, BlueprintReadOnly) float Fatigue = 10;
    UPROPERTY(SaveGame, BlueprintReadOnly) float SurvivalReserve = 100;
    UPROPERTY(SaveGame, BlueprintReadOnly) double SimulatedSeconds = 0;
    UPROPERTY(BlueprintReadOnly) ERVRestMode RestMode = ERVRestMode::Awake;
};
DECLARE_DYNAMIC_MULTICAST_DELEGATE(FRVNeedsChanged);

/** PlayerState-owned needs survive possession; mutations execute only on the server. */
UCLASS(ClassGroup=(RV), meta=(BlueprintSpawnableComponent))
class RVSURVIVAL_API URVNeedsComponent : public UActorComponent
{
    GENERATED_BODY()
public:
    URVNeedsComponent();
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
    virtual void TickComponent(float Delta, ELevelTick Type, FActorComponentTickFunction* Function) override;
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& Out) const override;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) TObjectPtr<URVNeedsProfile> TuningAsset;
    UPROPERTY(EditAnywhere, Replicated, BlueprintReadOnly) FRVNeedsTuning Tuning;
    UPROPERTY(ReplicatedUsing=OnRep_State, BlueprintReadOnly) FRVNeedsState State;
    UPROPERTY(BlueprintAssignable) FRVNeedsChanged OnNeedsChanged;
    UPROPERTY(Replicated, BlueprintReadOnly) TObjectPtr<ARVRestPoint> RestLocation;
    UPROPERTY(Replicated, BlueprintReadOnly) FString Feedback;
    UFUNCTION(BlueprintPure) float GetMovementScale() const;
    UFUNCTION(BlueprintPure) FString GetWarnings() const;
    UFUNCTION(BlueprintPure) FGameplayTagContainer GetStatusTags() const;
    UFUNCTION(BlueprintCallable) void RequestConsume(FGuid Id);
    UFUNCTION(BlueprintCallable) void RequestRestMode(ERVRestMode Mode);
    UFUNCTION(Server, Reliable) void ServerConsume(FGuid Id);
    UFUNCTION(Server, Reliable) void ServerRestMode(ERVRestMode Mode);
    bool BeginRestAuthority(ARVRestPoint* Point, ARVSurvivorCharacter* Character);
    void EndRestAuthority();
    ARVSurvivorCharacter* ResolveSurvivor() const;
    UFUNCTION(BlueprintCallable, meta=(DevelopmentOnly)) bool DebugSetValues(float Nutrition, float Hydration, float Fatigue);
    UFUNCTION(BlueprintCallable, meta=(DevelopmentOnly)) bool DebugSetTimeScale(float Scale);
    UFUNCTION(BlueprintCallable, meta=(DevelopmentOnly)) bool DebugAdvanceTime(float Seconds);
    void CopyPersistentValuesTo(URVNeedsComponent* Destination) const;
private:
    UFUNCTION() void OnRep_State();
    void Advance(double Seconds);
    float ActivityMultiplier() const;
    bool DebugAllowed() const;
    TWeakObjectPtr<ARVSurvivorCharacter> RestingCharacter;
    float DevelopmentTimeScale = 1;
    double NextConsumptionTime = 0;
};
