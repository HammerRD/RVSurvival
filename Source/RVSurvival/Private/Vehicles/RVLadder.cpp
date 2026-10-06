#include "Vehicles/RVLadder.h"
#include "Vehicles/RVVehicleBase.h"
#include "Player/RVSurvivorCharacter.h"
#include "Player/RVLadderClimbComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/CapsuleComponent.h"
#include "Interaction/RVInteractionTargetPresentationComponent.h"
#include "Net/UnrealNetwork.h"
ARVLadder::ARVLadder()
{
    PrimaryActorTick.bCanEverTick=true; PrimaryActorTick.TickInterval=.1f;
    bAlwaysRelevant=true; SetReplicateMovement(true);
    CreateDefaultSubobject<URVInteractionTargetPresentationComponent>(TEXT("TargetPresentation"));
    Mesh->SetRelativeScale3D(FVector(.15,.4,1.2));
    Mesh->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
    Mesh->SetCollisionResponseToAllChannels(ECR_Ignore);
    Mesh->SetCollisionResponseToChannel(ECC_Visibility,ECR_Block);
}
void ARVLadder::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{ Super::GetLifetimeReplicatedProps(OutLifetimeProps); DOREPLIFETIME(ARVLadder,BottomLocal); DOREPLIFETIME(ARVLadder,ClimbHeight); DOREPLIFETIME(ARVLadder,Occupant); }
FVector ARVLadder::BottomWorld() const
{ return GetAttachParentActor()?GetAttachParentActor()->GetActorTransform().TransformPosition(BottomLocal):GetActorLocation(); }
bool ARVLadder::CanInteract_Implementation(APawn* Pawn) const
{
    const auto* C=Cast<ARVSurvivorCharacter>(Pawn); const auto* RV=GetAttachParentActor();
    return C && !C->SeatedVehicle && !Occupant && RV && RV->GetVelocity().Size()<10;
}
FText ARVLadder::GetInteractionText_Implementation(APawn*) const
{ return FText::FromString(Occupant?TEXT("Rear ladder occupied"):TEXT("Rear ladder | Hold E to climb (parked) | roof access unavailable")); }
bool ARVLadder::ValidateRail(ARVSurvivorCharacter* C,FVector& Position) const
{
    if (!C || !GetAttachParentActor() || !FMath::IsFinite(ClimbHeight) || ClimbHeight<=0 || BottomLocal.ContainsNaN()) return false;
    Position=BottomWorld(); const auto* Capsule=C->GetCapsuleComponent();
    FCollisionQueryParams Params(SCENE_QUERY_STAT(RVLadderRail),false,C);
    FHitResult Hit;
    return !GetWorld()->SweepSingleByChannel(Hit,Position,Position+FVector(0,0,ClimbHeight),FQuat::Identity,ECC_Pawn,
        FCollisionShape::MakeCapsule(Capsule->GetScaledCapsuleRadius(),Capsule->GetScaledCapsuleHalfHeight()),Params);
}
bool ARVLadder::FindGroundExit(ARVSurvivorCharacter* C,FVector& Position) const
{
    const auto* RV=GetAttachParentActor(); if (!C || !RV) return false;
    const auto* Capsule=C->GetCapsuleComponent();
    const FVector Aim=RV->GetActorTransform().TransformPosition(GroundExitLocal);
    FCollisionQueryParams Params(SCENE_QUERY_STAT(RVLadderExit),false,C); FHitResult Hit;
    if (!GetWorld()->LineTraceSingleByChannel(Hit,Aim+FVector(0,0,100),Aim-FVector(0,0,350),ECC_Pawn,Params) || Hit.ImpactNormal.Z<.7) return false;
    Position=Hit.ImpactPoint+FVector(0,0,Capsule->GetScaledCapsuleHalfHeight()+2);
    return !GetWorld()->OverlapBlockingTestByChannel(Position,FQuat::Identity,ECC_Pawn,
        FCollisionShape::MakeCapsule(Capsule->GetScaledCapsuleRadius(),Capsule->GetScaledCapsuleHalfHeight()),Params);
}
void ARVLadder::CompleteInteraction_Implementation(APawn* Pawn)
{
    if (!HasAuthority() || !CanInteract_Implementation(Pawn)) return;
    if (auto* C=Cast<ARVSurvivorCharacter>(Pawn))
        if (auto* Climb=C->FindComponentByClass<URVLadderClimbComponent>()) Climb->BeginAuthority(this);
}
void ARVLadder::Tick(float Delta)
{
    Super::Tick(Delta);
    if (HasAuthority() && Occupant && (!IsValid(Occupant) || !Occupant->GetController()))
    {
        if (auto* RV=Cast<ARVVehicleBase>(GetAttachParentActor())) RV->SetAuthorityDriveLock(this,false);
        Occupant=nullptr; ForceNetUpdate();
    }
}
void ARVLadder::EndPlay(const EEndPlayReason::Type Reason)
{
    if (HasAuthority()) if (auto* RV=Cast<ARVVehicleBase>(GetAttachParentActor())) RV->SetAuthorityDriveLock(this,false);
    Super::EndPlay(Reason);
}
