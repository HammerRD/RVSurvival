#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "RVSurvivorCharacter.generated.h"
class UCameraComponent;
class URVInteractionComponent;
class UInputAction;
class UInputMappingContext;
class ULocalPlayer;
class ARVVehicleBase;
struct FInputActionValue;
/** Uses Unreal CharacterMovement prediction/replication; camera never dictates server position. */
UCLASS()
class RVSURVIVAL_API ARVSurvivorCharacter : public ACharacter
{
    GENERATED_BODY()
public:
    ARVSurvivorCharacter(const FObjectInitializer& Initializer = FObjectInitializer::Get());
    virtual void PawnClientRestart() override;
    virtual void Restart() override;
    virtual void UnPossessed() override;
    virtual void OnRep_Controller() override;
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& Out) const override;
    virtual void SetupPlayerInputComponent(UInputComponent* PlayerInputComponent) override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
    virtual void GetActorEyesViewPoint(FVector& OutLocation, FRotator& OutRotation) const override;
    URVInteractionComponent* GetInteraction() const { return Interaction; }
    void SetVehicleSeat(ARVVehicleBase* Vehicle);
    UFUNCTION(NetMulticast, Reliable) void MulticastRecoveryPlacement(FVector Position, FRotator Rotation);
    UPROPERTY(ReplicatedUsing=OnRep_VehicleSeat, BlueprintReadOnly, Category="RV|Seats") TObjectPtr<ARVVehicleBase> SeatedVehicle;
protected:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<class URVRestPoseComponent> RestPose;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<class URVInventoryComponent> Inventory;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<class URVPassengerReferenceFrameComponent> PassengerReferenceFrame;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<UCameraComponent> Camera;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<URVInteractionComponent> Interaction;
private:
    void CreateInput();
    void RemoveInput();
    UFUNCTION() void OnRep_VehicleSeat();
    bool bSeatMovementTickPaused=false;
    TWeakObjectPtr<ULocalPlayer> InputLocalPlayer;
    void MoveForward(const FInputActionValue& Value);
    void MoveRight(const FInputActionValue& Value);
    void LookYaw(const FInputActionValue& Value);
    void LookPitch(const FInputActionValue& Value);
    void StartJump();
    void StopJump();
    void StartInteract();
    void StopInteract();
    UPROPERTY(Transient) TObjectPtr<UInputMappingContext> Mapping;
    UPROPERTY(Transient) TObjectPtr<UInputAction> ForwardAction;
    UPROPERTY(Transient) TObjectPtr<UInputAction> RightAction;
    UPROPERTY(Transient) TObjectPtr<UInputAction> YawAction;
    UPROPERTY(Transient) TObjectPtr<UInputAction> PitchAction;
    UPROPERTY(Transient) TObjectPtr<UInputAction> JumpAction;
    UPROPERTY(Transient) TObjectPtr<UInputAction> InteractAction;
};
