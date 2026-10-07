#pragma once
#include "CoreMinimal.h"
#include "GameFramework/PlayerController.h"
#include "RVPlayerController.generated.h"
class ARVVehicleBase;
/** Gate 1 framework boundary; later gates add only the state owned by this role. */
UCLASS()
class RVSURVIVAL_API ARVPlayerController : public APlayerController
{
    GENERATED_BODY()
public:
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& Out) const override;
    virtual void PawnLeavingGame() override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
    virtual void PlayerTick(float DeltaTime) override;
    virtual void SetupInputComponent() override;
    UFUNCTION(Server, Unreliable) void ServerDrive(float Throttle, float Steering, bool Handbrake);
    UFUNCTION(Server, Reliable) void ServerExitVehicle();
    UFUNCTION(BlueprintCallable, Category="RV|Seats") void RequestSwitchSeat(FName TargetSeat);
    UFUNCTION(Server, Reliable) void ServerSwitchSeat(FName TargetSeat);
    UFUNCTION(BlueprintCallable, Category="RV|Seats") void RequestLivingArea();
    UFUNCTION(Server, Reliable) void ServerLivingArea();
    UPROPERTY(Replicated, BlueprintReadOnly, Category="RV|Seats") FString SeatFeedback;
    UPROPERTY(Replicated, BlueprintReadOnly, Category="RV|Seats") TObjectPtr<ARVVehicleBase> SeatedVehicle;
    UPROPERTY(Replicated, BlueprintReadOnly) TObjectPtr<class ARVResourcePoint> ResourcePoint;
    UPROPERTY(Replicated, BlueprintReadOnly) FString ResourceFeedback;
    UPROPERTY(Replicated, BlueprintReadOnly) TObjectPtr<class ARVServicePoint> MechanicalPoint;
    UPROPERTY(Replicated, BlueprintReadOnly) FString MechanicalFeedback;
    UFUNCTION(BlueprintCallable) void RequestService(FName Action,int32 ExpectedRevision,FGuid ItemId,int32 ItemRevision);
    UFUNCTION(Server,Reliable) void ServerService(FName Action,int32 ExpectedRevision,FGuid ItemId,int32 ItemRevision);
    UFUNCTION(BlueprintCallable) void RequestResourceControl(FName Control, bool Enabled, int32 ExpectedRevision);
    UFUNCTION(Server, Reliable) void ServerResourceControl(FName Control, bool Enabled, int32 ExpectedRevision);
    UFUNCTION(BlueprintCallable) void RequestRefuel(FGuid ItemId, int32 ExpectedRevision);
    UFUNCTION(Server, Reliable) void ServerRefuel(FGuid ItemId, int32 ExpectedRevision);
    UFUNCTION(BlueprintCallable) void RequestCloseResource();
    double SeatEntryTime = 0;
private:
    bool ValidateResourceAccess(bool FuelFill) const;
    void ToggleResource(FName Control);
    void LightsKey(); void GeneratorKey(); void FridgeKey(); void StationKey(); void IdleKey(); void CloseKey();
    void WakeKey(); void SleepKey();
    void PatchKey(); void RadiatorKey(); void EngineRepairKey();
    void HoodKey();
    UPROPERTY(Transient) TObjectPtr<class UInputMappingContext> ResourceMapping;
    UPROPERTY(Transient) TArray<TObjectPtr<class UInputAction>> ResourceActions;
    UPROPERTY(Transient) TObjectPtr<class UInputMappingContext> MechanicalMapping;
    UPROPERTY(Transient) TArray<TObjectPtr<class UInputAction>> MechanicalActions;
    bool bMechanicalMappingActive=false;
    TWeakObjectPtr<class ULocalPlayer> ResourceInputLocalPlayer;
    double LastResourceRequestTime=-1;
    double LastSeatSwitchTime = -1;
};
