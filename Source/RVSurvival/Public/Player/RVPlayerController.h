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
    UFUNCTION(BlueprintCallable, Category="RV|Controls") void ToggleControls();
    UFUNCTION(BlueprintCallable) void ToggleMedical();
    UFUNCTION(Client,Reliable) void ClientOpenMedical();
    UPROPERTY(Replicated, BlueprintReadOnly) TObjectPtr<class ARVMedicalStation> MedicalStation;
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
    UFUNCTION(BlueprintCallable) void RequestRecoverRV();
    UFUNCTION(Server,Reliable) void ServerRecoverRV(class ARVMechanicalMotorhome* Target);
    UFUNCTION(Exec) void RVRecover();
    UPROPERTY(Replicated,BlueprintReadOnly) FString RecoveryFeedback;
    double SeatEntryTime = 0;
private:
    bool ValidateResourceAccess(bool FuelFill) const;
    void ToggleResource(FName Control);
    void LightsKey(); void GeneratorKey(); void FridgeKey(); void StationKey(); void IdleKey(); void CloseKey();
    void WakeKey(); void SleepKey();
    void PatchKey(); void RadiatorKey(); void EngineRepairKey();
    void HoodKey();
    void DriverKey(); void PassengerKey(); void NextSeatKey();
    void OrbitHold(const struct FInputActionValue& Value);
    void OrbitYaw(const struct FInputActionValue& Value); void OrbitPitch(const struct FInputActionValue& Value);
    bool bOrbitHeld=false;
    UPROPERTY(Transient) TObjectPtr<class URVControlsWidget> ControlsWidget;
    UPROPERTY(Transient) TObjectPtr<class URVMedicalWidget> MedicalWidget;
    UPROPERTY(Transient) TObjectPtr<class UInputMappingContext> ResourceMapping;
    UPROPERTY(Transient) TObjectPtr<class UInputMappingContext> DrivingControlsCatalog;
    UPROPERTY(Transient) TArray<TObjectPtr<class UInputAction>> ResourceActions;
    UPROPERTY(Transient) TObjectPtr<class UInputMappingContext> MechanicalMapping;
    UPROPERTY(Transient) TArray<TObjectPtr<class UInputAction>> MechanicalActions;
    bool bMechanicalMappingActive=false;
    TWeakObjectPtr<class ULocalPlayer> ResourceInputLocalPlayer;
    double LastResourceRequestTime=-1;
    double LastSeatSwitchTime = -1;
};
