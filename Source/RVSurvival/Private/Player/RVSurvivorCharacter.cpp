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
#include "Player/RVPlayerController.h"
#include "Vehicles/RVVehicleBase.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Components/CapsuleComponent.h"
#include "Net/UnrealNetwork.h"
#include "Player/RVCharacterMovementComponent.h"
#include "Player/RVPassengerReferenceFrameComponent.h"
ARVSurvivorCharacter::ARVSurvivorCharacter(const FObjectInitializer& Init)
    : Super(Init.SetDefaultSubobjectClass<URVCharacterMovementComponent>(ACharacter::CharacterMovementComponentName))
{
    bReplicates = true;
    bUseControllerRotationYaw = true;
    BaseEyeHeight = 64.f;
    Camera = CreateDefaultSubobject<UCameraComponent>(TEXT("FirstPersonCamera"));
    Camera->SetupAttachment(GetRootComponent());
    Camera->SetRelativeLocation(FVector(0, 0, BaseEyeHeight));
    Camera->bUsePawnControlRotation = true;
    Interaction = CreateDefaultSubobject<URVInteractionComponent>(TEXT("Interaction"));
    PassengerReferenceFrame = CreateDefaultSubobject<URVPassengerReferenceFrameComponent>(TEXT("PassengerReferenceFrame"));
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
            { InputLocalPlayer = Local; Input->RemoveMappingContext(Mapping); Input->AddMappingContext(Mapping, 0); }
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
void ARVSurvivorCharacter::StartJump() { if (!SeatedVehicle) Jump(); }
void ARVSurvivorCharacter::StopJump() { StopJumping(); }
void ARVSurvivorCharacter::StartInteract()
{
    if (SeatedVehicle) { if (auto* PC = Cast<ARVPlayerController>(Controller)) PC->ServerExitVehicle(); }
    else Interaction->BeginInteraction();
}
void ARVSurvivorCharacter::StopInteract() { Interaction->EndInteraction(); }
void ARVSurvivorCharacter::GetActorEyesViewPoint(FVector& Location, FRotator& Rotation) const
{
    // Same capsule-relative eye origin on authority and client; no client-supplied trace.
    Location = GetActorLocation() + FVector(0, 0, BaseEyeHeight);
    Rotation = GetViewRotation();
}
void ARVSurvivorCharacter::EndPlay(const EEndPlayReason::Type Reason)
{
    RemoveInput();
    Super::EndPlay(Reason);
}
void ARVSurvivorCharacter::RemoveInput()
{
    if (auto* Local = InputLocalPlayer.Get())
        if (auto* Input = Local->GetSubsystem<UEnhancedInputLocalPlayerSubsystem>())
            if (Mapping) Input->RemoveMappingContext(Mapping);
    InputLocalPlayer.Reset();
}
void ARVSurvivorCharacter::UnPossessed() { RemoveInput(); Super::UnPossessed(); }
void ARVSurvivorCharacter::OnRep_Controller() { Super::OnRep_Controller(); if (!IsLocallyControlled()) RemoveInput(); }
void ARVSurvivorCharacter::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{ Super::GetLifetimeReplicatedProps(OutLifetimeProps); DOREPLIFETIME(ARVSurvivorCharacter, SeatedVehicle); }
void ARVSurvivorCharacter::SetVehicleSeat(ARVVehicleBase* Vehicle)
{ check(HasAuthority()); SeatedVehicle = Vehicle; OnRep_VehicleSeat(); ForceNetUpdate(); }
void ARVSurvivorCharacter::OnRep_VehicleSeat()
{
    bUseControllerRotationYaw = !SeatedVehicle;
    GetCapsuleComponent()->SetCollisionEnabled(SeatedVehicle ? ECollisionEnabled::NoCollision : ECollisionEnabled::QueryAndPhysics);
    if (SeatedVehicle) { StopJumping(); GetCharacterMovement()->StopMovementImmediately(); GetCharacterMovement()->DisableMovement(); }
    else GetCharacterMovement()->SetMovementMode(MOVE_Walking);
}
