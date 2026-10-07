#include "Vehicles/RVVehicleBase.h"
#include "Player/RVInputMappings.h"
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
#include "Player/RVPassengerReferenceFrameComponent.h"
ARVVehicleBase::ARVVehicleBase(const FObjectInitializer& Init)
    : Super(Init.SetDefaultSubobjectClass<URVVehicleMovementComponent>(VehicleMovementComponentName))
{
    PrimaryActorTick.bCanEverTick = true; bReplicates = true; bAlwaysRelevant = true; SetReplicateMovement(true);
    SetNetUpdateFrequency(60); SetMinNetUpdateFrequency(30);
    GetMesh()->SetCollisionProfileName(TEXT("Vehicle")); GetMesh()->SetSimulatePhysics(true);
    GetMesh()->bReplicatePhysicsToAutonomousProxy = true;
}
TArray<URVVehicleSeatComponent*> ARVVehicleBase::GetSeats() const
{
    TArray<URVVehicleSeatComponent*> Seats; GetComponents(Seats);
    Seats.RemoveAll([](const auto* Seat){return !Seat->bEnabled;});
    Seats.Sort([](const URVVehicleSeatComponent& A,const URVVehicleSeatComponent& B)
    {
        const int32 ARank=A.bDriverSeat?0:A.bInteriorOnly?2:1;
        const int32 BRank=B.bDriverSeat?0:B.bInteriorOnly?2:1;
        return ARank!=BRank?ARank<BRank:A.GetFName().LexicalLess(B.GetFName());
    });
    return Seats;
}
void ARVVehicleBase::BeginPlay()
{
    Super::BeginPlay();
    if (HasAuthority()) for (auto* Seat : GetSeats())
    {
        if (Seat->bInteriorOnly) continue;
        auto* Entry = GetWorld()->SpawnActorDeferred<ARVVehicleEntryPoint>(ARVVehicleEntryPoint::StaticClass(),
            FTransform(GetActorRotation(), GetActorTransform().TransformPosition(Seat->EntryOffset)), this);
        Entry->Seat = Seat; Entry->FinishSpawning(Entry->GetActorTransform());
        Entry->AttachToActor(this, FAttachmentTransformRules::KeepWorldTransform);
    }
}
bool ARVVehicleBase::CanEnter(URVVehicleSeatComponent* Seat, ARVSurvivorCharacter* Character) const
{
    if(Character) if(const auto* PS=Character->GetPlayerState<ARVPlayerState>(); PS && PS->Needs->State.RestMode!=ERVRestMode::Awake) return false;
    const auto* Frame=Character?Character->FindComponentByClass<URVPassengerReferenceFrameComponent>():nullptr;
    const bool Inside=Frame && Frame->ReferenceFrame==this;
    return Seat && Seat->bEnabled && Seat->GetOwner() == this && !Seat->Occupant && Character && !Character->SeatedVehicle
        && Cast<ARVPlayerController>(Character->GetController())
        && (GetVelocity().Size() <= MaxEntryExitSpeed || Inside);
}
bool ARVVehicleBase::TryEnter(URVVehicleSeatComponent* Seat, ARVSurvivorCharacter* Character)
{
    if (!HasAuthority() || !CanEnter(Seat, Character)) return false;
    if (!ValidateSeatDestination(Seat, Character))
    {
        CastChecked<ARVPlayerController>(Character->GetController())->SeatFeedback=TEXT("Seat destination obstructed or unsupported; remain standing.");
        Character->GetController()->ForceNetUpdate();
        return false;
    }
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
void ARVVehicleBase::SetAuthorityDriveLock(AActor* Requester,bool bLocked)
{
    if (!HasAuthority() || !Requester) return;
    if (bLocked) DriveLocks.Add(Requester); else DriveLocks.Remove(Requester);
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
                    bExitInputArmed = !Input->GetActionValue(ExitAction).Get<bool>();
        InputSendTime += DT;
        if (InputSendTime >= .05f)
        { InputSendTime = 0; if (auto* PC = Cast<ARVPlayerController>(Controller)) PC->ServerDrive(LocalThrottle, LocalSteering, bLocalHandbrake); }
    }
    if (HasAuthority())
    {
        for (auto* S : GetSeats()) if (S->Occupant && (!S->OccupantController.IsValid() || !IsValid(S->Occupant))) ReleaseSeat(S, true, FVector::ZeroVector);
        for (auto It=DriveLocks.CreateIterator();It;++It) if (!It->IsValid()) It.RemoveCurrent();
        const bool Active = DriveLocks.IsEmpty() && IsDriver(Cast<ARVPlayerController>(Controller)) && GetWorld()->GetTimeSeconds() - LastInputTime < .5;
        GetVehicleMovement()->SetThrottleInput(Active ? FMath::Max(ServerThrottle, 0.f) : 0);
        GetVehicleMovement()->SetBrakeInput(Active ? FMath::Max(-ServerThrottle, 0.f) : 0);
        GetVehicleMovement()->SetSteeringInput(Active ? ServerSteering : 0);
        GetVehicleMovement()->SetHandbrakeInput(!Active || bServerHandbrake);
    }
}
bool ARVVehicleBase::FindSafeExit(URVVehicleSeatComponent* Seat, ARVSurvivorCharacter* Character, FVector& Position) const
{ return FindSafeExitAtOffset(Seat->ExitOffset,Character,Position); }
bool ARVVehicleBase::FindSafeExitAtOffset(FVector PreferredOffset, ARVSurvivorCharacter* Character, FVector& Position) const
{
    FCollisionQueryParams Params(SCENE_QUERY_STAT(RVSeatExit), false, this); Params.AddIgnoredActor(Character);
    TArray<AActor*> Attached; GetAttachedActors(Attached); Params.AddIgnoredActors(Attached);
    float Radius = Character->GetCapsuleComponent()->GetScaledCapsuleRadius();
    if (const auto* Frame=Character->FindComponentByClass<URVPassengerReferenceFrameComponent>())
        Radius=FMath::Max(Radius,Frame->GetOutsideCapsuleRadius()*Radius/Character->GetCapsuleComponent()->GetUnscaledCapsuleRadius());
    const float Half = Character->GetCapsuleComponent()->GetScaledCapsuleHalfHeight();
    const TArray<FVector> Candidates = {PreferredOffset, PreferredOffset + FVector(-100,0,0),
        PreferredOffset + FVector(100,0,0), FVector(-450,0,0), FVector(0,-350,0), FVector(0,350,0)};
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
bool ARVVehicleBase::TrySwitchSeat(ARVPlayerController* PC, FName TargetSeat)
{
    if (!HasAuthority() || !PC || PC->SeatedVehicle != this) return false;
    if (GetVelocity().Size() > MaxEntryExitSpeed)
    { PC->SeatFeedback = TEXT("Stop the RV before switching seats."); return false; }
    URVVehicleSeatComponent* Source = nullptr;
    URVVehicleSeatComponent* Target = nullptr;
    for (auto* Seat : GetSeats())
    {
        if (Seat->Occupant && Seat->OccupantController.Get() == PC) Source = Seat;
        if (Seat->GetFName() == TargetSeat) Target = Seat;
    }
    if (!Source || !Target || Source == Target)
    { PC->SeatFeedback = TEXT("Choose another seat."); return false; }
    if (Target->Occupant || (Target->bDriverSeat && GetController()))
    { PC->SeatFeedback = TEXT("That seat is occupied."); return false; }
    auto* Character = Source->Occupant.Get();
    if (!IsValid(Character) || Character->SeatedVehicle != this
        || PC->GetPawn() != (Source->bDriverSeat ? static_cast<APawn*>(this) : Character)) return false;
    if (!ValidateSeatDestination(Target,Character))
    { PC->SeatFeedback=TEXT("Seat destination obstructed or unsupported; staying in current seat."); return false; }
    // Validate first, then transfer serially on the server. Never use the outside-exit path.
    if (Source->bDriverSeat)
    { ServerThrottle = ServerSteering = 0; bServerHandbrake = true; PC->Possess(Character); }
    Target->Occupant = Character; Target->OccupantController = PC;
    Source->Occupant = nullptr; Source->OccupantController.Reset();
    Character->AttachToComponent(Target, FAttachmentTransformRules::SnapToTargetNotIncludingScale);
    Character->SetActorRelativeLocation(FVector::ZeroVector);
    if (Target->bDriverSeat) { PC->Possess(this); LastInputTime = GetWorld()->GetTimeSeconds(); }
    Character->SetVehicleSeat(this); // Possession may have restored walking; this remains an anchored seat.
    PC->SeatEntryTime = GetWorld()->GetTimeSeconds();
    PC->SeatFeedback = FString::Printf(TEXT("Now seated: %s"), *Target->SeatLabel.ToString());
    Character->ForceNetUpdate(); PC->ForceNetUpdate(); ForceNetUpdate(); return true;
}
bool ARVVehicleBase::ValidateSeatDestination(const URVVehicleSeatComponent* Seat,const ARVSurvivorCharacter* Character) const
{
    if (!Seat || !Character || Seat->GetOwner()!=this || Seat->GetComponentTransform().ContainsNaN()
        || !Seat->IsAttachedTo(GetMesh())) return false;
    FCollisionQueryParams Params(SCENE_QUERY_STAT(RVSeatDestination),false,this); Params.AddIgnoredActor(Character);
    FHitResult Floor;
    return GetWorld()->LineTraceSingleByChannel(Floor,Seat->GetComponentLocation()+FVector(0,0,25),
        Seat->GetComponentLocation()-FVector(0,0,250),ECC_Pawn,Params) && Floor.ImpactNormal.Z>.65;
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
    auto Axis = [this](TObjectPtr<UInputAction>& A, FKey Positive, FKey Negative,FName PositiveName,FName NegativeName,const TCHAR* PositiveLabel,const TCHAR* NegativeLabel)
    { A = NewObject<UInputAction>(this); A->ValueType = EInputActionValueType::Axis1D; RVInputMappings::Map(Mapping,A,Positive,PositiveName,PositiveLabel); RVInputMappings::Map(Mapping,A,Negative,NegativeName,NegativeLabel); Mapping->GetMapping(Mapping->GetMappings().Num()-1).Modifiers.Add(NewObject<UInputModifierNegate>(Mapping)); };
    Axis(ThrottleAction,EKeys::W,EKeys::S,TEXT("Accelerate"),TEXT("BrakeReverse"),TEXT("Accelerate"),TEXT("Brake / reverse")); Axis(SteeringAction,EKeys::D,EKeys::A,TEXT("SteerRight"),TEXT("SteerLeft"),TEXT("Steer right"),TEXT("Steer left"));
    HandbrakeAction = NewObject<UInputAction>(this); RVInputMappings::Map(Mapping,HandbrakeAction,EKeys::SpaceBar,TEXT("Handbrake"),TEXT("Handbrake"));
    ExitAction = NewObject<UInputAction>(this); RVInputMappings::Map(Mapping,ExitAction,EKeys::E,TEXT("VehicleExit"),TEXT("Exit vehicle"));
}
void ARVVehicleBase::PawnClientRestart()
{
    Super::PawnClientRestart(); CreateInput(); LocalThrottle = LocalSteering = 0; bLocalHandbrake = false;
    bExitInputArmed = false; LocalPossessionTime = GetWorld()->GetTimeSeconds();
    if (auto* PC = Cast<APlayerController>(Controller)) if (auto* Local = PC->GetLocalPlayer())
        if (auto* Input = Local->GetSubsystem<UEnhancedInputLocalPlayerSubsystem>())
        { InputLocalPlayer = Local; RVInputMappings::Register(PC,Mapping); Input->RemoveMappingContext(Mapping); Input->AddMappingContext(Mapping, 1); }
}
void ARVVehicleBase::RemoveInput()
{ RVInputMappings::Unregister(InputLocalPlayer.Get(),Mapping); if (auto* Local = InputLocalPlayer.Get()) if (auto* Input = Local->GetSubsystem<UEnhancedInputLocalPlayerSubsystem>()) if (Mapping) Input->RemoveMappingContext(Mapping); InputLocalPlayer.Reset(); }
void ARVVehicleBase::UnPossessed() { RemoveInput(); LocalThrottle = LocalSteering = 0; Super::UnPossessed(); }
void ARVVehicleBase::OnRep_Controller() { Super::OnRep_Controller(); if (!IsLocallyControlled()) RemoveInput(); }
void ARVVehicleBase::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
    Super::SetupPlayerInputComponent(PlayerInputComponent); CreateInput(); auto* Input = CastChecked<UEnhancedInputComponent>(PlayerInputComponent);
    for (auto Event : {ETriggerEvent::Triggered, ETriggerEvent::Completed, ETriggerEvent::Canceled})
    { Input->BindAction(ThrottleAction, Event, this, &ThisClass::Throttle); Input->BindAction(SteeringAction, Event, this, &ThisClass::Steering); Input->BindAction(HandbrakeAction, Event, this, &ThisClass::Handbrake); }
    Input->BindAction(ExitAction, ETriggerEvent::Started, this, &ThisClass::Exit);
}
void ARVVehicleBase::Throttle(const FInputActionValue& V)
{ if(FMath::IsNearlyZero(V.Get<float>())) bRecoveryThrottleLatch=false; LocalThrottle=bRecoveryThrottleLatch?0:V.Get<float>(); }
void ARVVehicleBase::Steering(const FInputActionValue& V)
{ if(FMath::IsNearlyZero(V.Get<float>())) bRecoverySteeringLatch=false; LocalSteering=bRecoverySteeringLatch?0:V.Get<float>(); }
void ARVVehicleBase::MulticastClearRecoveryDrive_Implementation()
{
    bRecoveryThrottleLatch=bRecoveryThrottleLatch || !FMath::IsNearlyZero(LocalThrottle);
    bRecoverySteeringLatch=bRecoverySteeringLatch || !FMath::IsNearlyZero(LocalSteering);
    LocalThrottle=LocalSteering=ServerThrottle=ServerSteering=0;
    bLocalHandbrake=false;bServerHandbrake=true;LastInputTime=0;
    GetVehicleMovement()->SetThrottleInput(0);GetVehicleMovement()->SetBrakeInput(0);
    GetVehicleMovement()->SetSteeringInput(0);GetVehicleMovement()->SetHandbrakeInput(true);
}
void ARVVehicleBase::Handbrake(const FInputActionValue& V) { bLocalHandbrake = V.Get<bool>(); }
void ARVVehicleBase::Exit() { if (bExitInputArmed) if (auto* PC = Cast<ARVPlayerController>(Controller)) PC->ServerExitVehicle(); }
