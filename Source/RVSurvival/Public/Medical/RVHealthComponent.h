#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Medical/RVMedicalProfile.h"
#include "RVHealthComponent.generated.h"

/** Persistent player-owned injury rules. GAS handles vital attributes and medication. */
UCLASS(ClassGroup=(RV), meta=(BlueprintSpawnableComponent))
class RVSURVIVAL_API URVHealthComponent : public UActorComponent
{
    GENERATED_BODY()
public:
    URVHealthComponent();
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
    virtual void TickComponent(float Delta, ELevelTick Type, FActorComponentTickFunction* Function) override;
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& Out) const override;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) TObjectPtr<URVMedicalProfile> Profile;
    UPROPERTY(Replicated, BlueprintReadOnly, SaveGame) TArray<FRVInjuryInstance> Injuries;
    UPROPERTY(Replicated, BlueprintReadOnly, SaveGame) ERVMedicalLifeState LifeState=ERVMedicalLifeState::Active;
    UPROPERTY(Replicated, BlueprintReadOnly) FString Feedback;
    UPROPERTY(Replicated, BlueprintReadOnly) FGuid ActiveTreatment;
    UPROPERTY(Replicated, BlueprintReadOnly) double TreatmentEndTime=0;
    UFUNCTION(BlueprintPure) float GetMovementScale() const;
    UFUNCTION(BlueprintPure) float GetPain() const;
    UFUNCTION(BlueprintPure) bool CanAct() const { return LifeState==ERVMedicalLifeState::Active; }
    UFUNCTION(BlueprintCallable, meta=(DevelopmentOnly)) bool DebugApplyInjury(ERVInjuryKind Kind, ERVBodyRegion Region, float Severity);
    UFUNCTION(BlueprintCallable, meta=(DevelopmentOnly)) bool DebugSetVitals(float Blood, float Vitality);
    UFUNCTION(BlueprintCallable, meta=(DevelopmentOnly)) bool DebugSetTimeScale(float Scale);
    UFUNCTION(BlueprintCallable, meta=(DevelopmentOnly)) bool DebugClearInjuries();
    UFUNCTION(BlueprintCallable) void RequestTreatment(class ARVPlayerState* Patient, FGuid Injury, FGuid Supply, int32 ExpectedRevision);
    UFUNCTION(BlueprintCallable) void RequestCancelTreatment();
    UFUNCTION(Server, Reliable) void ServerBeginTreatment(class ARVPlayerState* Patient, FGuid Injury, FGuid Supply, int32 ExpectedRevision);
    UFUNCTION(Server, Reliable) void ServerCancelTreatment();
private:
    bool DebugAllowed() const;
    bool ValidateTreatment(FString& Error) const;
    void CompleteTreatment();
    void CancelTreatment(const FString& Reason);
    void UpdateLifeState(float Delta);
    const URVMedicalProfile* Tuning() const;
    TWeakObjectPtr<class ARVPlayerState> TreatmentPatient;
    TWeakObjectPtr<class URVHealthComponent> ReservedBy;
    FGuid SupplyId;
    int32 InjuryRevision=0;
    FTimerHandle TreatmentTimer;
    float TimeScale=1;
    float DownedSeconds=0;
};
