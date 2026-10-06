#pragma once
#include "CoreMinimal.h"
#include "WheeledVehiclePawn.h"
#include "RVVehicleBase.generated.h"
class URVVehicleSeatComponent;
class ARVPlayerController;
class ARVSurvivorCharacter;
class UInputMappingContext;
class UInputAction;
class ULocalPlayer;
struct FInputActionValue;
/** Shared seat lifecycle and authoritative controls; art/rig configured by content. */
UCLASS(Abstract, Blueprintable)
class RVSURVIVAL_API ARVVehicleBase : public AWheeledVehiclePawn
{
    GENERATED_BODY()
public:
    ARVVehicleBase(const FObjectInitializer& Initializer);
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
    virtual void PawnClientRestart() override;
    virtual void UnPossessed() override;
    virtual void OnRep_Controller() override;
    virtual void SetupPlayerInputComponent(UInputComponent* Input) override;
    UFUNCTION(BlueprintPure, Category="RV|Seats") TArray<URVVehicleSeatComponent*> GetSeats() const;
    bool CanEnter(URVVehicleSeatComponent* Seat, ARVSurvivorCharacter* Character) const;
    bool TryEnter(URVVehicleSeatComponent* Seat, ARVSurvivorCharacter* Character);
    virtual bool TryExit(ARVPlayerController* Controller);
    bool TrySwitchSeat(ARVPlayerController* Controller, FName TargetSeat);
    void ReleaseDisconnected(ARVPlayerController* Controller);
    void ReceiveDriveInput(ARVPlayerController* Controller, float Throttle, float Steering, bool Handbrake);
    UFUNCTION(BlueprintPure, Category="RV|Seats") bool IsDriver(const ARVPlayerController* PlayerController) const;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="RV|Seats") float MaxEntryExitSpeed = 150.f;
protected:
    virtual bool ValidateSeatDestination(const URVVehicleSeatComponent* Seat, const ARVSurvivorCharacter* Character) const;
    void ReleaseSeat(URVVehicleSeatComponent* Seat, bool Disconnect, const FVector& Position);
    bool FindSafeExit(URVVehicleSeatComponent* Seat, ARVSurvivorCharacter* Character, FVector& Position) const;
    bool FindSafeExitAtOffset(FVector PreferredOffset, ARVSurvivorCharacter* Character, FVector& Position) const;
private:
    void CreateInput();
    void RemoveInput();
    void Throttle(const FInputActionValue& Value);
    void Steering(const FInputActionValue& Value);
    void Handbrake(const FInputActionValue& Value);
    void Exit();
    float LocalThrottle = 0, LocalSteering = 0, InputSendTime = 0;
    bool bLocalHandbrake = false;
    bool bExitInputArmed = false;
    double LocalPossessionTime = 0;
    float ServerThrottle = 0, ServerSteering = 0;
    bool bServerHandbrake = true;
    double LastInputTime = 0;
    UPROPERTY(Transient) TObjectPtr<UInputMappingContext> Mapping;
    UPROPERTY(Transient) TObjectPtr<UInputAction> ThrottleAction;
    UPROPERTY(Transient) TObjectPtr<UInputAction> SteeringAction;
    UPROPERTY(Transient) TObjectPtr<UInputAction> HandbrakeAction;
    UPROPERTY(Transient) TObjectPtr<UInputAction> ExitAction;
    TWeakObjectPtr<ULocalPlayer> InputLocalPlayer;
};
