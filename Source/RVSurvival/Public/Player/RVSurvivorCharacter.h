#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "RVSurvivorCharacter.generated.h"
class UCameraComponent;
class URVInteractionComponent;
class UInputAction;
class UInputMappingContext;
struct FInputActionValue;
/** Uses Unreal CharacterMovement prediction/replication; camera never dictates server position. */
UCLASS()
class RVSURVIVAL_API ARVSurvivorCharacter : public ACharacter
{
    GENERATED_BODY()
public:
    ARVSurvivorCharacter();
    virtual void PawnClientRestart() override;
    virtual void SetupPlayerInputComponent(UInputComponent* PlayerInputComponent) override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
    virtual void GetActorEyesViewPoint(FVector& OutLocation, FRotator& OutRotation) const override;
    URVInteractionComponent* GetInteraction() const { return Interaction; }
protected:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<UCameraComponent> Camera;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<URVInteractionComponent> Interaction;
private:
    void CreateInput();
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
