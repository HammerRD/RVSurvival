#include "Vehicles/RVLadder.h"
#include "Vehicles/RVVehicleBase.h"
#include "Player/RVSurvivorCharacter.h"
#include "Player/RVLadderClimbComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/BoxComponent.h"
#include "Player/RVPlayerState.h"
#include "Survival/RVNeedsComponent.h"
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
    RoofInteraction=CreateDefaultSubobject<UBoxComponent>(TEXT("RoofInteraction"));
    RoofInteraction->SetupAttachment(RootComponent);RoofInteraction->SetAbsolute(false,false,true);
    RoofInteraction->SetRelativeLocation(FVector(0,0,190));RoofInteraction->SetBoxExtent(FVector(24,24,20));
    RoofInteraction->SetCollisionEnabled(ECollisionEnabled::QueryOnly);RoofInteraction->SetCollisionResponseToAllChannels(ECR_Ignore);
    RoofInteraction->SetCollisionResponseToChannel(ECC_Visibility,ECR_Block);
}
void ARVLadder::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{ Super::GetLifetimeReplicatedProps(OutLifetimeProps); DOREPLIFETIME(ARVLadder,BottomLocal); DOREPLIFETIME(ARVLadder,ClimbHeight); DOREPLIFETIME(ARVLadder,Occupant); DOREPLIFETIME(ARVLadder,bRoofAccess);DOREPLIFETIME(ARVLadder,RoofExitLocal);DOREPLIFETIME(ARVLadder,RoofSurfaceHeight); }
FVector ARVLadder::BottomWorld() const
{ return GetAttachParentActor()?GetAttachParentActor()->GetActorTransform().TransformPosition(BottomLocal):GetActorLocation(); }
bool ARVLadder::CanInteract_Implementation(APawn* Pawn) const
{
    const auto* C=Cast<ARVSurvivorCharacter>(Pawn); const auto* RV=GetAttachParentActor();
    const auto* PS=C?C->GetPlayerState<ARVPlayerState>():nullptr;
    return C && !C->SeatedVehicle && !Occupant && RV && RV->GetVelocity().Size()<10
        && (!PS || PS->Needs->State.RestMode==ERVRestMode::Awake);
}
FText ARVLadder::GetInteractionText_Implementation(APawn*) const
{ return FText::FromString(Occupant?TEXT("Rear ladder occupied"):bRoofAccess?TEXT("Rear ladder | Hold interact to climb | up/down | interact to dismount (parked)"):TEXT("Rear ladder | Hold interact to climb (parked) | no roof access")); }
bool ARVLadder::FindRoofExit(ARVSurvivorCharacter* C,FVector& Position,UPrimitiveComponent*& Floor) const
{
    const auto* RV=GetAttachParentActor();if(!bRoofAccess || !C || !RV || RV->GetVelocity().Size()>=10)return false;
    if(FMath::Abs(RV->GetActorRotation().Roll)>5 || FMath::Abs(RV->GetActorRotation().Pitch)>5)return false;
    FCollisionQueryParams Params(SCENE_QUERY_STAT(RVRoofExit),false,C);FHitResult Hit;
    const FVector Aim=RV->GetActorTransform().TransformPosition(RoofExitLocal);
    if(!GetWorld()->LineTraceSingleByChannel(Hit,Aim+FVector(0,0,30),Aim-FVector(0,0,180),ECC_Pawn,Params)
        || Hit.GetActor()!=RV || !Hit.GetComponent() || !Hit.GetComponent()->ComponentHasTag(TEXT("RVRoofPlatform")) || Hit.ImpactNormal.Z<.7)return false;
    const auto* Capsule=C->GetCapsuleComponent();Position=Hit.ImpactPoint+FVector(0,0,Capsule->GetScaledCapsuleHalfHeight()+3);Floor=Hit.GetComponent();
    return !GetWorld()->OverlapBlockingTestByChannel(Position,FQuat::Identity,ECC_Pawn,
        FCollisionShape::MakeCapsule(Capsule->GetScaledCapsuleRadius(),Capsule->GetScaledCapsuleHalfHeight()),Params);
}
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
        if (auto* RV=Cast<ARVVehicleBase>(GetAttachParentActor())) RV->SetAuthorityDriveLock(Occupant,false);
        Occupant=nullptr; ForceNetUpdate();
    }
}
void ARVLadder::EndPlay(const EEndPlayReason::Type Reason)
{
    if (HasAuthority()) if (auto* RV=Cast<ARVVehicleBase>(GetAttachParentActor())) RV->SetAuthorityDriveLock(this,false);
    Super::EndPlay(Reason);
}
