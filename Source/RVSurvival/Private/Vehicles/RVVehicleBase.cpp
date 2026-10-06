#include "Vehicles/RVVehicleBase.h"
#include "Vehicles/RVVehicleMovementComponent.h"
#include "Vehicles/RVVehicleSeatComponent.h"
#include "Vehicles/RVVehicleEntryPoint.h"
#include "Player/RVSurvivorCharacter.h"
#include "Player/RVPlayerController.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/CapsuleComponent.h"
#include "EnhancedInputComponent.h"
#include "EnhancedPlayerInput.h"
#include "EnhancedInputSubsystems.h"
#include "Engine/LocalPlayer.h"
#include "InputAction.h"
#include "InputMappingContext.h"
#include "InputModifiers.h"
#include "InputActionValue.h"
#include "Engine/World.h"
#include "Player/RVPlayerState.h"
#include "Survival/RVNeedsComponent.h"
ARVVehicleBase::ARVVehicleBase(const FObjectInitializer& Init)
    : Super(Init.SetDefaultSubobjectClass<URVVehicleMovementComponent>(VehicleMovementComponentName))
{
    PrimaryActorTick.bCanEverTick = true; bReplicates = true; bAlwaysRelevant = true; SetReplicateMovement(true);
    SetNetUpdateFrequency(60); SetMinNetUpdateFrequency(30);
    GetMesh()->SetCollisionProfileName(TEXT("Vehicle")); GetMesh()->SetSimulatePhysics(true);
    GetMesh()->bReplicatePhysicsToAutonomousProxy = true;
}
TArray<URVVehicleSeatComponent*> ARVVehicleBase::GetSeats() const
{ TArray<URVVehicleSeatComponent*> Seats; GetComponents(Seats); return Seats; }
void ARVVehicleBase::BeginPlay()
{
    Super::BeginPlay();
    if (HasAuthority()) for (auto* Seat : GetSeats())
    {
        auto* Entry = GetWorld()->SpawnActorDeferred<ARVVehicleEntryPoint>(ARVVehicleEntryPoint::StaticClass(),
            FTransform(GetActorRotation(), GetActorTransform().TransformPosition(Seat->EntryOffset)), this);
        Entry->Seat = Seat; Entry->FinishSpawning(Entry->GetActorTransform());
        Entry->AttachToActor(this, FAttachmentTransformRules::KeepWorldTransform);
    }
}
bool ARVVehicleBase::CanEnter(URVVehicleSeatComponent* Seat, ARVSurvivorCharacter* Character) const
{
    if(Character) if(const auto* PS=Character->GetPlayerState<ARVPlayerState>(); PS && PS->Needs->State.RestMode!=ERVRestMode::Awake) return false;
    return Seat && Seat->GetOwner() == this && !Seat->Occupant && Character && !Character->SeatedVehicle
        && Cast<ARVPlayerController>(Character->GetController()) && GetVelocity().Size() <= MaxEntryExitSpeed;
}
bool ARVVehicleBase::TryEnter(URVVehicleSeatComponent* Seat, ARVSurvivorCharacter* Character)
{
    if (!HasAuthority() || !CanEnter(Seat, Character)) return false;
    auto* PC = CastChecked<ARVPlayerController>(Character->GetController());
    Seat->Occupant = Character; Seat->OccupantController = PC;
    PC->SeatedVehicle = this; PC->SeatEntryTime = GetWorld()->GetTimeSeconds();
    Character->SetVehicleSeat(this);
    Character->AttachToComponent(Seat, FAttachmentTransformRules::SnapToTargetNotIncludingScale);
    Character->SetActorRelativeLocation(FVector::ZeroVector);
    if (Seat->bDriverSeat) { PC->Possess(this); LastInputTime = GetWorld()->GetTimeSeconds(); }
    PC->ForceNetUpdate(); ForceNetUpdate(); return true;
}
bool ARVVehicleBase::IsDriver(const ARVPlayerController* PC) const
{
    for (auto* S : GetSeats()) if (S->bDriverSeat && S->Occupant && S->OccupantController.Get() == PC) return PC && PC->GetPawn() == this;
    return false;
}
void ARVVehicleBase::ReceiveDriveInput(ARVPlayerController* PC, float ThrottleValue, float SteeringValue, bool HB)
{
    if (!HasAuthority() || !IsDriver(PC) || !FMath::IsFinite(ThrottleValue) || !FMath::IsFinite(SteeringValue)) return;
    ServerThrottle = FMath::Clamp(ThrottleValue, -1.f, 1.f); ServerSteering = FMath::Clamp(SteeringValue, -1.f, 1.f);
    bServerHandbrake = HB; LastInputTime = GetWorld()->GetTimeSeconds();
}
void ARVVehicleBase::Tick(float DT)
{
    Super::Tick(DT);
    if (IsLocallyControlled())
    {
        // Entry and exit share E across two pawns. A held entry key must not
        // become an exit press when the new mapping context starts evaluating.
        if (!bExitInputArmed && GetWorld()->GetTimeSeconds() - LocalPossessionTime > .75)
            if (auto* PC = Cast<APlayerController>(Controller))
                if (auto* Input = Cast<UEnhancedPlayerInput>(PC->PlayerInput))
                    bExitInputArmed = !PC->IsInputKeyDown(EKeys::E)
                        && !Input->GetActionValue(ExitAction).Get<bool>();
        InputSendTime += DT;
        if (InputSendTime >= .05f)
        { InputSendTime = 0; if (auto* PC = Cast<ARVPlayerController>(Controller)) PC->ServerDrive(LocalThrottle, LocalSteering, bLocalHandbrake); }
    }
    if (HasAuthority())
    {
        for (auto* S : GetSeats()) if (S->Occupant && (!S->OccupantController.IsValid() || !IsValid(S->Occupant))) ReleaseSeat(S, true, FVector::ZeroVector);
        const bool Active = IsDriver(Cast<ARVPlayerController>(Controller)) && GetWorld()->GetTimeSeconds() - LastInputTime < .5;
        GetVehicleMovement()->SetThrottleInput(Active ? FMath::Max(ServerThrottle, 0.f) : 0);
        GetVehicleMovement()->SetBrakeInput(Active ? FMath::Max(-ServerThrottle, 0.f) : 0);
        GetVehicleMovement()->SetSteeringInput(Active ? ServerSteering : 0);
        GetVehicleMovement()->SetHandbrakeInput(!Active || bServerHandbrake);
    }
}
bool ARVVehicleBase::FindSafeExit(URVVehicleSeatComponent* Seat, ARVSurvivorCharacter* Character, FVector& Position) const
{
    FCollisionQueryParams Params(SCENE_QUERY_STAT(RVSeatExit), false, this); Params.AddIgnoredActor(Character);
    TArray<AActor*> Attached; GetAttachedActors(Attached); Params.AddIgnoredActors(Attached);
    const float Radius = Character->GetCapsuleComponent()->GetScaledCapsuleRadius();
    const float Half = Character->GetCapsuleComponent()->GetScaledCapsuleHalfHeight();
    const TArray<FVector> Candidates = {Seat->ExitOffset, Seat->ExitOffset + FVector(-100,0,0),
        Seat->ExitOffset + FVector(100,0,0), FVector(-450,0,0), FVector(0,-350,0), FVector(0,350,0)};
    for (const auto& Offset : Candidates)
    {
        const FVector Base = GetActorTransform().TransformPosition(Offset); FHitResult Ground;
        if (!GetWorld()->LineTraceSingleByChannel(Ground, Base + FVector(0,0,250), Base - FVector(0,0,400), ECC_Visibility, Params) || Ground.ImpactNormal.Z < .65) continue;
        // Reject obstacle roofs and drops; a clear capsule on a tall prop is not a
        // safe roadside exit. The vehicle root is close to the road surface.
        const float GroundHeight = Ground.ImpactPoint.Z - GetActorLocation().Z;
        if (GroundHeight > 50.f || GroundHeight < -150.f) continue;
        const FVector Target = Ground.ImpactPoint + FVector(0,0,Half + 4);
        // Include the RV and entry actors in the clearance query: a valid exit may not overlap them.
        FCollisionQueryParams Clearance(SCENE_QUERY_STAT(RVSeatClearance), false, Character);
        if (!GetWorld()->OverlapBlockingTestByChannel(Target, FQuat::Identity, ECC_Pawn, FCollisionShape::MakeCapsule(Radius, Half), Clearance))
        { Position = Target; return true; }
    }
    return false;
}
bool ARVVehicleBase::TryExit(ARVPlayerController* PC)
{
    if (!HasAuthority() || GetVelocity().Size() > MaxEntryExitSpeed) return false;
    for (auto* S : GetSeats()) if (S->Occupant && S->OccupantController.Get() == PC)
    { FVector Position; if (!FindSafeExit(S, S->Occupant, Position)) return false; ReleaseSeat(S, false, Position); return true; }
    return false;
}
void ARVVehicleBase::ReleaseSeat(URVVehicleSeatComponent* Seat, bool Disconnect, const FVector& Position)
{
    auto* PC = Seat->OccupantController.Get(); auto* Character = Seat->Occupant.Get();
    if (Seat->bDriverSeat)
    { ServerThrottle = ServerSteering = 0; bServerHandbrake = true; if (PC && PC->GetPawn() == this) PC->UnPossess(); }
    if (Character)
    {
        Character->DetachFromActor(FDetachmentTransformRules::KeepWorldTransform);
        Character->SetVehicleSeat(nullptr);
        if (Disconnect) Character->Destroy();
        else { Character->SetActorLocation(Position, false, nullptr, ETeleportType::TeleportPhysics); Character->SetActorRotation(FRotator(0, GetActorRotation().Yaw, 0)); if (PC) PC->Possess(Character); }
    }
    Seat->Occupant = nullptr; Seat->OccupantController.Reset();
    if (PC) { PC->SeatedVehicle = nullptr; PC->ForceNetUpdate(); }
    ForceNetUpdate();
}
void ARVVehicleBase::ReleaseDisconnected(ARVPlayerController* PC)
{ if (HasAuthority()) for (auto* S : GetSeats()) if (S->OccupantController.Get() == PC) ReleaseSeat(S, true, FVector::ZeroVector); }
void ARVVehicleBase::EndPlay(const EEndPlayReason::Type Reason)
{ RemoveInput(); if (HasAuthority()) for (auto* S : GetSeats()) if (S->Occupant) ReleaseSeat(S, true, FVector::ZeroVector); Super::EndPlay(Reason); }
void ARVVehicleBase::CreateInput()
{
    if (Mapping) return; Mapping = NewObject<UInputMappingContext>(this);
    auto Axis = [this](TObjectPtr<UInputAction>& A, FKey Positive, FKey Negative)
    { A = NewObject<UInputAction>(this); A->ValueType = EInputActionValueType::Axis1D; Mapping->MapKey(A, Positive); Mapping->MapKey(A, Negative).Modifiers.Add(NewObject<UInputModifierNegate>(Mapping)); };
    Axis(ThrottleAction, EKeys::W, EKeys::S); Axis(SteeringAction, EKeys::D, EKeys::A);
    HandbrakeAction = NewObject<UInputAction>(this); Mapping->MapKey(HandbrakeAction, EKeys::SpaceBar);
    ExitAction = NewObject<UInputAction>(this); Mapping->MapKey(ExitAction, EKeys::E);
}
void ARVVehicleBase::PawnClientRestart()
{
    Super::PawnClientRestart(); CreateInput(); LocalThrottle = LocalSteering = 0; bLocalHandbrake = false;
    bExitInputArmed = false; LocalPossessionTime = GetWorld()->GetTimeSeconds();
    if (auto* PC = Cast<APlayerController>(Controller)) if (auto* Local = PC->GetLocalPlayer())
        if (auto* Input = Local->GetSubsystem<UEnhancedInputLocalPlayerSubsystem>())
        { InputLocalPlayer = Local; Input->RemoveMappingContext(Mapping); Input->AddMappingContext(Mapping, 1); }
}
void ARVVehicleBase::RemoveInput()
{ if (auto* Local = InputLocalPlayer.Get()) if (auto* Input = Local->GetSubsystem<UEnhancedInputLocalPlayerSubsystem>()) if (Mapping) Input->RemoveMappingContext(Mapping); InputLocalPlayer.Reset(); }
void ARVVehicleBase::UnPossessed() { RemoveInput(); LocalThrottle = LocalSteering = 0; Super::UnPossessed(); }
void ARVVehicleBase::OnRep_Controller() { Super::OnRep_Controller(); if (!IsLocallyControlled()) RemoveInput(); }
void ARVVehicleBase::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
    Super::SetupPlayerInputComponent(PlayerInputComponent); CreateInput(); auto* Input = CastChecked<UEnhancedInputComponent>(PlayerInputComponent);
    for (auto Event : {ETriggerEvent::Triggered, ETriggerEvent::Completed, ETriggerEvent::Canceled})
    { Input->BindAction(ThrottleAction, Event, this, &ThisClass::Throttle); Input->BindAction(SteeringAction, Event, this, &ThisClass::Steering); Input->BindAction(HandbrakeAction, Event, this, &ThisClass::Handbrake); }
    Input->BindAction(ExitAction, ETriggerEvent::Started, this, &ThisClass::Exit);
}
void ARVVehicleBase::Throttle(const FInputActionValue& V) { LocalThrottle = V.Get<float>(); }
void ARVVehicleBase::Steering(const FInputActionValue& V) { LocalSteering = V.Get<float>(); }
void ARVVehicleBase::Handbrake(const FInputActionValue& V) { bLocalHandbrake = V.Get<bool>(); }
void ARVVehicleBase::Exit() { if (bExitInputArmed) if (auto* PC = Cast<ARVPlayerController>(Controller)) PC->ServerExitVehicle(); }
