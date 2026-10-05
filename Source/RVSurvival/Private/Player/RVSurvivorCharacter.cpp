#include "Player/RVSurvivorCharacter.h"
#include "Camera/CameraComponent.h"
#include "Interaction/RVInteractionComponent.h"
#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"
#include "InputAction.h"
#include "InputMappingContext.h"
#include "InputModifiers.h"
#include "InputActionValue.h"
#include "Engine/LocalPlayer.h"
#include "GameFramework/PlayerController.h"
ARVSurvivorCharacter::ARVSurvivorCharacter()
{
    bReplicates = true;
    bUseControllerRotationYaw = true;
    BaseEyeHeight = 64.f;
    Camera = CreateDefaultSubobject<UCameraComponent>(TEXT("FirstPersonCamera"));
    Camera->SetupAttachment(GetRootComponent());
    Camera->SetRelativeLocation(FVector(0, 0, BaseEyeHeight));
    Camera->bUsePawnControlRotation = true;
    Interaction = CreateDefaultSubobject<URVInteractionComponent>(TEXT("Interaction"));
}
void ARVSurvivorCharacter::CreateInput()
{
    if (Mapping) return;
    Mapping = NewObject<UInputMappingContext>(this);
    auto Axis = [this](TObjectPtr<UInputAction>& Action, FKey Positive, FKey Negative)
    {
        Action = NewObject<UInputAction>(this);
        Action->ValueType = EInputActionValueType::Axis1D;
        Mapping->MapKey(Action, Positive);
        Mapping->MapKey(Action, Negative).Modifiers.Add(NewObject<UInputModifierNegate>(Mapping));
    };
    Axis(ForwardAction, EKeys::W, EKeys::S);
    Axis(RightAction, EKeys::D, EKeys::A);
    YawAction = NewObject<UInputAction>(this);
    YawAction->ValueType = EInputActionValueType::Axis1D;
    Mapping->MapKey(YawAction, EKeys::MouseX);
    PitchAction = NewObject<UInputAction>(this);
    PitchAction->ValueType = EInputActionValueType::Axis1D;
    Mapping->MapKey(PitchAction, EKeys::MouseY).Modifiers.Add(NewObject<UInputModifierNegate>(Mapping));
    JumpAction = NewObject<UInputAction>(this);
    Mapping->MapKey(JumpAction, EKeys::SpaceBar);
    InteractAction = NewObject<UInputAction>(this);
    Mapping->MapKey(InteractAction, EKeys::E);
}
void ARVSurvivorCharacter::PawnClientRestart()
{
    Super::PawnClientRestart();
    CreateInput();
    if (APlayerController* PC = Cast<APlayerController>(Controller))
        if (ULocalPlayer* Local = PC->GetLocalPlayer())
            if (auto* Input = Local->GetSubsystem<UEnhancedInputLocalPlayerSubsystem>())
            { Input->RemoveMappingContext(Mapping); Input->AddMappingContext(Mapping, 0); }
}
void ARVSurvivorCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
    Super::SetupPlayerInputComponent(PlayerInputComponent);
    CreateInput();
    UEnhancedInputComponent* Input = CastChecked<UEnhancedInputComponent>(PlayerInputComponent);
    Input->BindAction(ForwardAction, ETriggerEvent::Triggered, this, &ThisClass::MoveForward);
    Input->BindAction(RightAction, ETriggerEvent::Triggered, this, &ThisClass::MoveRight);
    Input->BindAction(YawAction, ETriggerEvent::Triggered, this, &ThisClass::LookYaw);
    Input->BindAction(PitchAction, ETriggerEvent::Triggered, this, &ThisClass::LookPitch);
    Input->BindAction(JumpAction, ETriggerEvent::Started, this, &ThisClass::StartJump);
    Input->BindAction(JumpAction, ETriggerEvent::Completed, this, &ThisClass::StopJump);
    Input->BindAction(JumpAction, ETriggerEvent::Canceled, this, &ThisClass::StopJump);
    Input->BindAction(InteractAction, ETriggerEvent::Started, this, &ThisClass::StartInteract);
    Input->BindAction(InteractAction, ETriggerEvent::Completed, this, &ThisClass::StopInteract);
    Input->BindAction(InteractAction, ETriggerEvent::Canceled, this, &ThisClass::StopInteract);
}
void ARVSurvivorCharacter::MoveForward(const FInputActionValue& V) { AddMovementInput(FRotationMatrix(FRotator(0, GetControlRotation().Yaw, 0)).GetUnitAxis(EAxis::X), V.Get<float>()); }
void ARVSurvivorCharacter::MoveRight(const FInputActionValue& V) { AddMovementInput(FRotationMatrix(FRotator(0, GetControlRotation().Yaw, 0)).GetUnitAxis(EAxis::Y), V.Get<float>()); }
void ARVSurvivorCharacter::LookYaw(const FInputActionValue& V) { AddControllerYawInput(V.Get<float>()); }
void ARVSurvivorCharacter::LookPitch(const FInputActionValue& V) { AddControllerPitchInput(V.Get<float>()); }
void ARVSurvivorCharacter::StartJump() { Jump(); }
void ARVSurvivorCharacter::StopJump() { StopJumping(); }
void ARVSurvivorCharacter::StartInteract() { Interaction->BeginInteraction(); }
void ARVSurvivorCharacter::StopInteract() { Interaction->EndInteraction(); }
void ARVSurvivorCharacter::GetActorEyesViewPoint(FVector& Location, FRotator& Rotation) const
{
    // Same capsule-relative eye origin on authority and client; no client-supplied trace.
    Location = GetActorLocation() + FVector(0, 0, BaseEyeHeight);
    Rotation = GetViewRotation();
}
void ARVSurvivorCharacter::EndPlay(const EEndPlayReason::Type Reason)
{
    if (APlayerController* PC = Cast<APlayerController>(Controller))
        if (ULocalPlayer* Local = PC->GetLocalPlayer())
            if (auto* Input = Local->GetSubsystem<UEnhancedInputLocalPlayerSubsystem>())
                if (Mapping) Input->RemoveMappingContext(Mapping);
    Super::EndPlay(Reason);
}
