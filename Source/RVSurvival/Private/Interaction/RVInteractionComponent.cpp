#include "Interaction/RVInteractionComponent.h"
#include "Interaction/RVInteractable.h"
#include "Core/RVLog.h"
#include "GameFramework/Pawn.h"
#include "Engine/World.h"
#include "TimerManager.h"
URVInteractionComponent::URVInteractionComponent()
{
    SetIsReplicatedByDefault(true);
    PrimaryComponentTick.bCanEverTick = true;
    PrimaryComponentTick.TickInterval = 0.1f;
}
AActor* URVInteractionComponent::TraceTarget() const
{
    const APawn* Pawn = Cast<APawn>(GetOwner());
    if (!Pawn || !Pawn->GetController() || !GetWorld()) return nullptr;
    FVector Origin; FRotator Rotation;
    Pawn->GetActorEyesViewPoint(Origin, Rotation);
    FHitResult Hit;
    FCollisionQueryParams Params(SCENE_QUERY_STAT(RVInteraction), false, Pawn);
    GetWorld()->LineTraceSingleByChannel(Hit, Origin, Origin + Rotation.Vector() * Range, ECC_Visibility, Params);
    AActor* Target = Hit.GetActor();
    return IsValid(Target) && Target->Implements<URVInteractable>() ? Target : nullptr;
}
bool URVInteractionComponent::IsAllowed(AActor* Target) const
{
    APawn* Pawn = Cast<APawn>(GetOwner());
    return IsValid(Target) && Pawn && Pawn->GetController() && Target->Implements<URVInteractable>()
        && IRVInteractable::Execute_CanInteract(Target, Pawn);
}
void URVInteractionComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
    const APawn* Pawn = Cast<APawn>(GetOwner());
    if (Pawn && Pawn->IsLocallyControlled()) FocusedTarget = TraceTarget();
    if (GetOwner()->HasAuthority() && ActiveTarget.IsValid()
        && (TraceTarget() != ActiveTarget.Get() || !IsAllowed(ActiveTarget.Get()))) CancelActive();
}
FText URVInteractionComponent::GetPrompt() const
{
    AActor* Target = FocusedTarget.Get();
    return IsAllowed(Target) ? IRVInteractable::Execute_GetInteractionText(Target, Cast<APawn>(GetOwner())) : FText::GetEmpty();
}
void URVInteractionComponent::BeginInteraction()
{
    APawn* Pawn = Cast<APawn>(GetOwner());
    if (Pawn && Pawn->IsLocallyControlled()) ServerBeginInteraction();
}
void URVInteractionComponent::EndInteraction()
{
    APawn* Pawn = Cast<APawn>(GetOwner());
    if (Pawn && Pawn->IsLocallyControlled()) ServerEndInteraction();
}
void URVInteractionComponent::ServerBeginInteraction_Implementation()
{
    const double Now = GetWorld()->GetTimeSeconds();
    if (Now - LastRequestTime < RequestInterval) return;
    LastRequestTime = Now;
    CancelActive();
    AActor* Target = TraceTarget();
    if (!IsAllowed(Target)) return;
    ActiveTarget = Target;
    APawn* Pawn = Cast<APawn>(GetOwner());
    const float Duration = IRVInteractable::Execute_GetInteractionDuration(Target, Pawn);
    if (!FMath::IsFinite(Duration) || Duration < 0.f || Duration > 60.f) { ActiveTarget.Reset(); return; }
    IRVInteractable::Execute_StartInteraction(Target, Pawn);
    if (!ActiveTarget.IsValid()) { CancelActive(); return; }
    if (Duration <= 0.f) FinishInteraction();
    else GetWorld()->GetTimerManager().SetTimer(CompletionTimer, this, &ThisClass::FinishInteraction, Duration, false);
}
void URVInteractionComponent::FinishInteraction()
{
    AActor* Target = ActiveTarget.Get();
    if (TraceTarget() != Target || !IsAllowed(Target)) { CancelActive(); return; }
    ActiveTarget.Reset();
    GetWorld()->GetTimerManager().ClearTimer(CompletionTimer);
    IRVInteractable::Execute_CompleteInteraction(Target, Cast<APawn>(GetOwner()));
    UE_LOG(LogRVInteraction, Verbose, TEXT("Authority completed interaction with %s"), *GetNameSafe(Target));
}
void URVInteractionComponent::CancelActive()
{
    GetWorld()->GetTimerManager().ClearTimer(CompletionTimer);
    AActor* Target = ActiveTarget.Get();
    ActiveTarget.Reset();
    if (IsValid(Target)) IRVInteractable::Execute_CancelInteraction(Target, Cast<APawn>(GetOwner()));
}
void URVInteractionComponent::ServerEndInteraction_Implementation() { CancelActive(); }
void URVInteractionComponent::EndPlay(const EEndPlayReason::Type Reason)
{
    if (GetOwner()->HasAuthority()) CancelActive();
    Super::EndPlay(Reason);
}
