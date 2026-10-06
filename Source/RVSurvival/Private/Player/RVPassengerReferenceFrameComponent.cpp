#include "Player/RVPassengerReferenceFrameComponent.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Components/PrimitiveComponent.h"
#include "Components/CapsuleComponent.h"
#include "HAL/IConsoleManager.h"
static TAutoConsoleVariable<int32> CVarPassengerDebug(TEXT("rv.Passenger.Debug"), 0, TEXT("Log moving-base entry/exit and client corrections."));
URVPassengerReferenceFrameComponent::URVPassengerReferenceFrameComponent()
{ PrimaryComponentTick.bCanEverTick = true; }
void URVPassengerReferenceFrameComponent::BeginPlay()
{
    Super::BeginPlay();
    if (auto* C = Cast<ACharacter>(GetOwner())) C->GetCharacterMovement()->AddTickPrerequisiteComponent(this);
}
void URVPassengerReferenceFrameComponent::RestoreWorldMovement()
{
    if (!ReferenceFrame) return;
    if (auto* C = Cast<ACharacter>(GetOwner()))
    {
        auto* M = C->GetCharacterMovement();
        M->bEnablePhysicsInteraction = bPreviousPhysicsInteraction;
        M->bBasedMovementIgnorePhysicsBase = bPreviousIgnorePhysicsBase;
        M->bBaseOnAttachmentRoot = bPreviousBaseOnAttachmentRoot;
        M->MaxWalkSpeed = PreviousWalkSpeed;
        C->GetCapsuleComponent()->SetCapsuleRadius(PreviousCapsuleRadius);
    }
    ReferenceFrame = nullptr;
}
void URVPassengerReferenceFrameComponent::EndPlay(const EEndPlayReason::Type Reason)
{
    RestoreWorldMovement();
    CurrentBase = nullptr;
    if (auto* C = Cast<ACharacter>(GetOwner())) C->GetCharacterMovement()->RemoveTickPrerequisiteComponent(this);
    Super::EndPlay(Reason);
}
void URVPassengerReferenceFrameComponent::TickComponent(float Dt, ELevelTick Type, FActorComponentTickFunction* Fn)
{
    Super::TickComponent(Dt, Type, Fn);
    auto* C = Cast<ACharacter>(GetOwner()); if (!C) return;
    auto* M = C->GetCharacterMovement(); auto* Base = Cast<UPrimitiveComponent>(C->GetMovementBaseObject());
    if (M->MovementMode==MOVE_None)
    { RestoreWorldMovement(); CurrentBase=nullptr; return; }
    if (CurrentBase != Base)
    {
        CurrentBase = Base; ++BaseChanges;
        if (CVarPassengerDebug.GetValueOnGameThread() > 1)
            UE_LOG(LogTemp, Log, TEXT("RVPassenger %s base=%s"), *C->GetName(), *GetNameSafe(Base));
    }
    // Floor collision remains modular, but native based movement uses one stable
    // attachment root across floor seams. Inspect the actual floor hit because
    // the movement base can now be the vehicle's chassis rather than that box.
    auto* Floor = M->CurrentFloor.HitResult.GetComponent();
    auto* Platform = Floor && M->CurrentFloor.IsWalkableFloor()
        && Floor->ComponentHasTag(TEXT("RVPassengerPlatform")) ? Floor : Base;
    AActor* Frame = Platform && Platform->ComponentHasTag(TEXT("RVPassengerPlatform")) ? Platform->GetOwner() : nullptr;
    if (ReferenceFrame != Frame)
    {
        RestoreWorldMovement();
        ReferenceFrame = Frame; ++FrameChanges;
        if (Frame)
        {
            bPreviousPhysicsInteraction = M->bEnablePhysicsInteraction;
            bPreviousIgnorePhysicsBase = M->bBasedMovementIgnorePhysicsBase;
            bPreviousBaseOnAttachmentRoot = M->bBaseOnAttachmentRoot;
            PreviousCapsuleRadius = C->GetCapsuleComponent()->GetUnscaledCapsuleRadius(); PreviousWalkSpeed = M->MaxWalkSpeed;
            C->GetCapsuleComponent()->SetCapsuleRadius(FMath::Min(PreviousCapsuleRadius, InteriorCapsuleRadius));
            M->MaxWalkSpeed = FMath::Min(PreviousWalkSpeed, InteriorWalkSpeed);
            M->bEnablePhysicsInteraction = false;
            // Native post-physics carry must not sweep into this vehicle's walls; walking still collides normally.
            M->bBasedMovementIgnorePhysicsBase = true;
            // Supported CMC option: avoid exchanging differently offset local
            // bases while traversing adjacent rigidly attached floor pieces.
            M->bBaseOnAttachmentRoot = true;
            LocalPosition = Frame->GetActorTransform().InverseTransformPosition(C->GetActorLocation());
        }
        if (CVarPassengerDebug.GetValueOnGameThread()) UE_LOG(LogTemp, Log, TEXT("RVPassenger %s frame=%s role=%d"), *C->GetName(), *GetNameSafe(Frame), int32(C->GetLocalRole()));
    }
    if (Frame)
    {
        const FVector NewLocal = Frame->GetActorTransform().InverseTransformPosition(C->GetActorLocation());
        MaxLocalStepCm = FMath::Max(MaxLocalStepCm, float(FVector::Distance(NewLocal, LocalPosition)));
        LocalPosition = NewLocal;
    }
}
void URVPassengerReferenceFrameComponent::RecordCorrection(float Distance)
{
#if !UE_BUILD_SHIPPING
    ++CorrectionCount; MaxCorrectionCm = FMath::Max(MaxCorrectionCm, Distance);
    if (CVarPassengerDebug.GetValueOnGameThread()) UE_LOG(LogTemp, Log, TEXT("RVPassenger %s correction=%.2fcm frame=%s"), *GetOwner()->GetName(), Distance, *GetNameSafe(ReferenceFrame));
#endif
}
void URVPassengerReferenceFrameComponent::ResetDiagnostics()
{ CorrectionCount = 0; MaxCorrectionCm = 0; MaxLocalStepCm = 0; FrameChanges = 0; BaseChanges = 0; }
