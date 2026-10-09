#include "Player/RVSurvivorCharacter.h"
#include "Core/RVDifficultyProfile.h"

#include "Combat/RVCombatComponent.h"
#include "Combat/RVBodyRegionHitComponent.h"
#include "Combat/RVInfected.h"
#include "Combat/RVInfectedProfile.h"
#include "Engine/DamageEvents.h"
#include "Player/RVInputMappings.h"
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
#include "Inventory/RVInventoryComponent.h"
#include "Player/RVPlayerState.h"
#include "Survival/RVNeedsComponent.h"
#include "Medical/RVHealthComponent.h"
#include "Survival/RVRestPoseComponent.h"
#include "Vehicles/RVSeatPoseComponent.h"
#include "Player/RVCharacterPresentationComponent.h"
#include "Player/RVCharacterVisualProfile.h"
void ARVSurvivorCharacter::MulticastRecoveryPlacement_Implementation(FVector Position, FRotator Rotation)
{
    DetachFromActor(FDetachmentTransformRules::KeepWorldTransform);
    SetBase(static_cast<FMovementBaseInterfaceData*>(nullptr));
    PassengerReferenceFrame->ResetForRecovery();
    auto* Movement=GetCharacterMovement();
    Movement->StopMovementImmediately();
    Movement->CurrentFloor.Clear();
    Movement->Activate(true);
    if(IsLocallyControlled())
    {
        // Discard moves from the old base without restarting the RPC clock.
        // A zero timestamp otherwise produces many seconds of expired moves.
        const float Timestamp=Movement->GetPredictionData_Client_Character()->CurrentTimeStamp;
        Movement->ResetPredictionData_Client();
        Movement->GetPredictionData_Client_Character()->CurrentTimeStamp=Timestamp;
    }
    GetCapsuleComponent()->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
    SetActorLocationAndRotation(Position,Rotation,false,nullptr,ETeleportType::TeleportPhysics);
    Movement->SetMovementMode(MOVE_Walking);
    ConsumeMovementInputVector();
    if(HasAuthority()) ForceNetUpdate();
}
#include "Player/RVLadderClimbComponent.h"
#include "Survival/RVRestPoint.h"
static bool CanMoveWhileAwake(const ARVSurvivorCharacter* Character)
{
    const auto* PS=Character->GetPlayerState<ARVPlayerState>();
    return !PS || (PS->Needs->State.RestMode==ERVRestMode::Awake && PS->Health->CanAct());
}
float ARVSurvivorCharacter::TakeDamage(float Amount,const FDamageEvent& Event,AController* EventInstigator,AActor* DamageCauser)
{
    if(!HasAuthority() || !FMath::IsFinite(Amount) || Amount<=0)return 0;
    auto* PS=GetPlayerState<ARVPlayerState>();if(!PS && SeatedVehicle)PS=SeatedVehicle->GetPlayerState<ARVPlayerState>();
    if(!PS)return 0;ERVBodyRegion Region=ERVBodyRegion::Torso;
    if(Event.IsOfType(FPointDamageEvent::ClassID))
    {const auto& Hit=static_cast<const FPointDamageEvent&>(Event).HitInfo;
     if(const auto* Q=Cast<URVBodyRegionHitComponent>(Hit.GetComponent()))Region=Q->Region;
     else if(CharacterPresentation)CharacterPresentation->ResolveBodyRegion(Hit.BoneName,Region);}
    float Severity=2,Contamination=.2f,Applied=Amount;
    if(const auto* Infected=Cast<ARVInfected>(DamageCauser))
    {Severity=Infected->Tuning()->InjurySeverity;Contamination=Infected->Tuning()->Contamination;}
    else if(DamageCauser)if(const auto* Source=DamageCauser->FindComponentByClass<URVCombatComponent>())
    {FRVItemInstance W;if(Source->IsApplyingMeleeDamage())Severity=1;
     if(Source->GetWeapon(W) && (!Source->IsApplyingMeleeDamage() || W.Definition->Combat.bMelee))
     {const auto& M=W.Definition->Combat;Severity=M.WoundSeverity;
      const bool Limb=Region==ERVBodyRegion::LeftArm || Region==ERVBodyRegion::RightArm || Region==ERVBodyRegion::LeftLeg || Region==ERVBodyRegion::RightLeg;
      Applied*=Region==ERVBodyRegion::Head?M.HeadDamageMultiplier:Limb?M.LimbDamageMultiplier:1.f;}}
    if(!PS->Health->ApplyWoundAuthority(Region,Severity,Applied,Contamination))return 0;
    return Super::TakeDamage(Applied,Event,EventInstigator,DamageCauser);
}
ARVSurvivorCharacter::ARVSurvivorCharacter(const FObjectInitializer& Init)
    : Super(Init.SetDefaultSubobjectClass<URVCharacterMovementComponent>(ACharacter::CharacterMovementComponentName))
{
    bReplicates = true;
    Inventory = CreateDefaultSubobject<URVInventoryComponent>(TEXT("Inventory"));
    Combat=CreateDefaultSubobject<URVCombatComponent>(TEXT("Combat"));
    RestPose = CreateDefaultSubobject<URVRestPoseComponent>(TEXT("RestPose"));
    CreateDefaultSubobject<URVSeatPoseComponent>(TEXT("SeatPose"));
    CreateDefaultSubobject<URVLadderClimbComponent>(TEXT("LadderClimb"));
    CharacterPresentation=CreateDefaultSubobject<URVCharacterPresentationComponent>(TEXT("CharacterPresentation"));
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
    auto Axis = [this](TObjectPtr<UInputAction>& Action, FKey Positive, FKey Negative,FName PositiveName,FName NegativeName,const TCHAR* PositiveLabel,const TCHAR* NegativeLabel)
    {
        Action = NewObject<UInputAction>(this);
        Action->ValueType = EInputActionValueType::Axis1D;
        RVInputMappings::Map(Mapping,Action,Positive,PositiveName,PositiveLabel);
        RVInputMappings::Map(Mapping,Action,Negative,NegativeName,NegativeLabel);
        Mapping->GetMapping(Mapping->GetMappings().Num()-1).Modifiers.Add(NewObject<UInputModifierNegate>(Mapping));
    };
    Axis(ForwardAction,EKeys::W,EKeys::S,TEXT("Forward"),TEXT("Backward"),TEXT("Walk / climb up"),TEXT("Walk back / climb down"));
    Axis(RightAction,EKeys::D,EKeys::A,TEXT("Right"),TEXT("Left"),TEXT("Walk right"),TEXT("Walk left"));
    YawAction = NewObject<UInputAction>(this);
    YawAction->ValueType = EInputActionValueType::Axis1D;
    RVInputMappings::Map(Mapping,YawAction,EKeys::MouseX,TEXT("LookYaw"),TEXT("Look horizontal"));
    PitchAction = NewObject<UInputAction>(this);
    PitchAction->ValueType = EInputActionValueType::Axis1D;
    RVInputMappings::Map(Mapping,PitchAction,EKeys::MouseY,TEXT("LookPitch"),TEXT("Look vertical"));
    Mapping->GetMapping(Mapping->GetMappings().Num()-1).Modifiers.Add(NewObject<UInputModifierNegate>(Mapping));
    JumpAction = NewObject<UInputAction>(this);
    RVInputMappings::Map(Mapping,JumpAction,EKeys::SpaceBar,TEXT("Jump"),TEXT("Jump"));
    InteractAction = NewObject<UInputAction>(this);
    RVInputMappings::Map(Mapping,InteractAction,EKeys::E,TEXT("Interact"),TEXT("Interact / stand / ladder dismount"));
}
void ARVSurvivorCharacter::PawnClientRestart()
{
    Super::PawnClientRestart();
    CreateInput();
    if (APlayerController* PC = Cast<APlayerController>(Controller))
        if (ULocalPlayer* Local = PC->GetLocalPlayer())
            if (auto* Input = Local->GetSubsystem<UEnhancedInputLocalPlayerSubsystem>())
            { InputLocalPlayer = Local; RVInputMappings::Register(PC,Mapping); Input->RemoveMappingContext(Mapping); Input->AddMappingContext(Mapping, 0); }
}
void ARVSurvivorCharacter::Restart()
{
    Super::Restart();
    // Possession restarts native walking even when the replicated seat did not
    // change. Reapply the seated policy on authority AND the owning client.
    if (SeatedVehicle) OnRep_VehicleSeat();
    else if (RestPose && RestPose->RestPoint) GetCharacterMovement()->DisableMovement();
}
void ARVSurvivorCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
    Super::SetupPlayerInputComponent(PlayerInputComponent);
    CreateInput();
    UEnhancedInputComponent* Input = CastChecked<UEnhancedInputComponent>(PlayerInputComponent);
    FindComponentByClass<URVCombatComponent>()->BindInput(Input);
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
void ARVSurvivorCharacter::MoveForward(const FInputActionValue& V) { if(SeatedVehicle)return; if(auto* Climb=FindComponentByClass<URVLadderClimbComponent>();Climb && Climb->Ladder) { Climb->ClimbInput(V.Get<float>()); return; } if(CanMoveWhileAwake(this)) AddMovementInput(FRotationMatrix(FRotator(0, GetControlRotation().Yaw, 0)).GetUnitAxis(EAxis::X), V.Get<float>()); }
void ARVSurvivorCharacter::MoveRight(const FInputActionValue& V) { if(SeatedVehicle)return; if(auto* Climb=FindComponentByClass<URVLadderClimbComponent>();Climb && Climb->Ladder) return; if(CanMoveWhileAwake(this)) AddMovementInput(FRotationMatrix(FRotator(0, GetControlRotation().Yaw, 0)).GetUnitAxis(EAxis::Y), V.Get<float>()); }
void ARVSurvivorCharacter::LookYaw(const FInputActionValue& V) { AddControllerYawInput(V.Get<float>()*GetDefault<URVPersonalSettings>()->LookSensitivity*(Combat?Combat->GetLookScale():1.f)); }
void ARVSurvivorCharacter::LookPitch(const FInputActionValue& V) { const auto* S=GetDefault<URVPersonalSettings>();AddControllerPitchInput(V.Get<float>()*S->LookSensitivity*(S->bInvertLook?-1.f:1.f)*(Combat?Combat->GetLookScale():1.f)); }
void ARVSurvivorCharacter::StartJump() { if (!SeatedVehicle && CanMoveWhileAwake(this)) Jump(); }
void ARVSurvivorCharacter::StopJump() { StopJumping(); }
void ARVSurvivorCharacter::StartInteract()
{
    if(auto* Climb=FindComponentByClass<URVLadderClimbComponent>();Climb && Climb->Ladder) { Climb->ServerExit(); return; }
    if (const auto* PS=GetPlayerState<ARVPlayerState>(); PS && PS->Needs->State.RestMode!=ERVRestMode::Awake)
    { PS->Needs->RequestRestMode(ERVRestMode::Awake); return; }
    if (SeatedVehicle) { if (auto* PC = Cast<ARVPlayerController>(Controller)) PC->ServerExitVehicle(); }
    else Interaction->BeginInteraction();
}
void ARVSurvivorCharacter::StopInteract() { Interaction->EndInteraction(); }
void ARVSurvivorCharacter::GetActorEyesViewPoint(FVector& Location, FRotator& Rotation) const
{
    // Same capsule-relative eye origin on authority and client; no client-supplied trace.
    Location = GetActorLocation() + FVector(0, 0, BaseEyeHeight);
    if(CharacterPresentation && CharacterPresentation->HasConfiguredVisuals())
        Location+=GetActorQuat().RotateVector(CharacterPresentation->Profile->OwnerCameraOffset);
    if (RestPose && RestPose->RestPoint) Location=GetActorTransform().TransformPosition(RestPose->RestPoint->LyingCameraOffset);
    Rotation = GetViewRotation();
}
void ARVSurvivorCharacter::EndPlay(const EEndPlayReason::Type Reason)
{
    RemoveInput();
    Super::EndPlay(Reason);
}
void ARVSurvivorCharacter::RemoveInput()
{
    if(Combat)Combat->RemoveInput();
    RVInputMappings::Unregister(InputLocalPlayer.Get(),Mapping);
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
    auto* Movement=GetCharacterMovement();
    ConsumeMovementInputVector();
    if (SeatedVehicle)
    {
        StopJumping();Movement->StopMovementImmediately();Movement->DisableMovement();
        // The authoritative seat attachment owns the seated transform. MOVE_None
        // alone still sends autonomous character moves against a moving seat.
        // Native inactivity also rejects stale character-move/adjustment RPCs
        // (tick disabling alone does not). Seat attachment remains authoritative;
        // world/interior prediction and correction rules are never bypassed.
        bSeatMovementTickPaused=true;
        Movement->Deactivate();
    }
    else
    {
        if(bSeatMovementTickPaused)
        {
            // Native activation registers required simulation ticks. A cached
            // possession-time tick flag can be false on a remote driver proxy.
            Movement->Activate(true);bSeatMovementTickPaused=false;
        }
        Movement->SetMovementMode(MOVE_Walking);
    }
}
