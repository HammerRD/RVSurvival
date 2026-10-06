#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "GameplayTagContainer.h"
#include "RVFuelComponent.generated.h"
DECLARE_DYNAMIC_MULTICAST_DELEGATE(FRVResourceChanged);
/** Litres. All transfers/burns are serialized on the server game thread. */
UCLASS(ClassGroup=(RV),meta=(BlueprintSpawnableComponent))
class RVSURVIVAL_API URVFuelComponent : public UActorComponent
{
    GENERATED_BODY()
public:
    URVFuelComponent();
    virtual void BeginPlay() override;
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& Out) const override;
    UPROPERTY(EditAnywhere, Replicated, BlueprintReadOnly) double CapacityLitres=200;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) double InitialLitres=150;
    UPROPERTY(EditAnywhere, Replicated, BlueprintReadOnly) FGameplayTag FuelType;
    UPROPERTY(ReplicatedUsing=OnRep_Fuel, BlueprintReadOnly, SaveGame) double Litres=0;
    UPROPERTY(BlueprintAssignable) FRVResourceChanged OnFuelChanged;
    UFUNCTION(BlueprintPure) double GetPercentage() const { return CapacityLitres>0?Litres/CapacityLitres:0; }
    double AddAuthority(double Amount);
    double BurnAuthority(double Amount);
    UFUNCTION(BlueprintCallable) bool DebugSetFuel(double Amount);
    static bool DebugAllowed();
private:
    UFUNCTION() void OnRep_Fuel();
};
