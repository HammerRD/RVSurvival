#include "Survival/RVRestPoint.h"
#include "Interaction/RVInteractionTargetPresentationComponent.h"
#include "Vehicles/RVInteriorMotorhome.h"
#include "Components/CapsuleComponent.h"
#include "Components/BoxComponent.h"
#include "Engine/OverlapResult.h"
#include "Survival/RVNeedsComponent.h"
#include "Player/RVPlayerState.h"
#include "Player/RVSurvivorCharacter.h"
#include "Components/StaticMeshComponent.h"
#include "Net/UnrealNetwork.h"
ARVRestPoint::ARVRestPoint()
{
    CreateDefaultSubobject<URVInteractionTargetPresentationComponent>(TEXT("TargetPresentation"));
    bAlwaysRelevant=true; SetReplicateMovement(true);
    DisplayName=FText::FromString(TEXT("Rest location"));
    Mesh->SetWorldScale3D(FVector(.15)); Mesh->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
    Mesh->SetCollisionResponseToAllChannels(ECR_Ignore); Mesh->SetCollisionResponseToChannel(ECC_Visibility,ECR_Block);
    InteractionSurface=CreateDefaultSubobject<UBoxComponent>(TEXT("InteractionSurface"));
    InteractionSurface->SetupAttachment(RootComponent);
    InteractionSurface->SetAbsolute(false,false,true);
    InteractionSurface->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
    InteractionSurface->SetCollisionResponseToAllChannels(ECR_Ignore);
    InteractionSurface->SetCollisionResponseToChannel(ECC_Visibility,ECR_Block);
    InteractionSurface->SetGenerateOverlapEvents(false);
    InteractionSurface->SetBoxExtent(InteractionExtent);
}
void ARVRestPoint::OnRep_InteractionExtent()
{
    if (InteractionSurface && !InteractionExtent.ContainsNaN())
        InteractionSurface->SetBoxExtent(InteractionExtent.ComponentMax(FVector(1)));
}
void ARVRestPoint::OnConstruction(const FTransform& Transform)
{ Super::OnConstruction(Transform); OnRep_InteractionExtent(); }
void ARVRestPoint::BeginPlay()
{ Super::BeginPlay(); OnRep_InteractionExtent(); }
void ARVRestPoint::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{ Super::GetLifetimeReplicatedProps(OutLifetimeProps); DOREPLIFETIME(ARVRestPoint,InteractionExtent); DOREPLIFETIME(ARVRestPoint,DisplayName); DOREPLIFETIME(ARVRestPoint,MaximumPlatformSpeed); DOREPLIFETIME(ARVRestPoint,Occupant);
  DOREPLIFETIME(ARVRestPoint,bUseLyingPose); DOREPLIFETIME(ARVRestPoint,LyingOffset); DOREPLIFETIME(ARVRestPoint,LyingRotation); DOREPLIFETIME(ARVRestPoint,WakeAisleLocation); DOREPLIFETIME(ARVRestPoint,LyingCameraOffset); }
bool ARVRestPoint::FindWakePosition(ARVSurvivorCharacter* Character,FVector& Position,UPrimitiveComponent*& Floor) const
{
    if (auto* RV=Cast<ARVInteriorMotorhome>(GetAttachParentActor()))
    {
        if (RV->FindSafeInteriorPosition(Character,WakeAisleLocation,Position,Floor)) return true;
        // Another standing passenger must not lock the bed's short rear aisle.
        // The second candidate set is still supported interior floor, never an outside exit or overlap escape.
        return RV->FindSafeInteriorPosition(Character,RV->StandingEntryLocation,Position,Floor);
    }
    return false; // Other rest locations can supply a platform placement policy before enabling lying.
}
bool ARVRestPoint::ValidateLyingPosition(ARVSurvivorCharacter* Character) const
{
    if (!Character || LyingOffset.ContainsNaN() || LyingRotation.ContainsNaN() || LyingCameraOffset.ContainsNaN()) return false;
    const FVector Position=GetActorLocation()+GetActorQuat().RotateVector(LyingOffset);
    FCollisionQueryParams Params(SCENE_QUERY_STAT(RVBedClearance),false,Character);
    // Include the full horizontal prototype body/head and a small clearance margin.
    TArray<FOverlapResult> Overlaps;
    const bool Blocked=GetWorld()->OverlapMultiByChannel(Overlaps,Position,GetActorQuat()*LyingRotation.Quaternion(),ECC_Pawn,
        FCollisionShape::MakeBox(FVector(100,20,20)),Params);
#if !(UE_BUILD_SHIPPING || UE_BUILD_TEST)
    if (Blocked) for (const auto& Hit:Overlaps) if (Hit.bBlockingHit)
        UE_LOG(LogTemp,Warning,TEXT("RVBedClearance blocked by %s at %s"),*GetPathNameSafe(Hit.GetComponent()),*Position.ToString());
#endif
    return !Blocked;
}
bool ARVRestPoint::CanContinueRest(const ARVSurvivorCharacter* Character) const
{
    if(!IsValid(Character) || !Character->GetController() || Character->SeatedVehicle || FVector::DistSquared(Character->GetActorLocation(),GetActorLocation())>FMath::Square(250.f)) return false;
    const AActor* Platform=GetAttachParentActor();
    return !Platform || Platform->GetVelocity().Size()<=FMath::Max(0.f,MaximumPlatformSpeed);
}
bool ARVRestPoint::CanInteract_Implementation(APawn* Pawn) const
{ return !Occupant && CanContinueRest(Cast<ARVSurvivorCharacter>(Pawn)); }
FText ARVRestPoint::GetInteractionText_Implementation(APawn*) const
{ return FText::FromString(DisplayName.ToString()+(Occupant?TEXT(" (occupied)"):TEXT(" | Hold E to rest (parked)"))); }
void ARVRestPoint::CompleteInteraction_Implementation(APawn* Pawn)
{
    if(!HasAuthority() || !CanInteract_Implementation(Pawn)) return;
    if(auto* PS=Pawn->GetPlayerState<ARVPlayerState>()) PS->Needs->BeginRestAuthority(this,Cast<ARVSurvivorCharacter>(Pawn));
}
void ARVRestPoint::ReleaseAuthority(ARVPlayerState* Player)
{ if(HasAuthority() && Occupant==Player) { Occupant=nullptr; ForceNetUpdate(); } }
void ARVRestPoint::EndPlay(const EEndPlayReason::Type Reason)
{ if(HasAuthority() && IsValid(Occupant)) Occupant->Needs->EndRestAuthority(); Super::EndPlay(Reason); }
