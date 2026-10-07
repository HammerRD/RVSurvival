#include "Player/RVLadderClimbComponent.h"
#include "Vehicles/RVLadder.h"
#include "Vehicles/RVVehicleBase.h"
#include "Components/CapsuleComponent.h"
#include "Player/RVPassengerReferenceFrameComponent.h"
#include "Player/RVSurvivorCharacter.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Net/UnrealNetwork.h"
URVLadderClimbComponent::URVLadderClimbComponent()
{ SetIsReplicatedByDefault(true); PrimaryComponentTick.bCanEverTick=true; }
void URVLadderClimbComponent::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{ Super::GetLifetimeReplicatedProps(OutLifetimeProps); DOREPLIFETIME(URVLadderClimbComponent,Ladder);DOREPLIFETIME(URVLadderClimbComponent,RoofLadder); }
bool URVLadderClimbComponent::BeginAuthority(ARVLadder* Target)
{
    auto* C=Cast<ARVSurvivorCharacter>(GetOwner()); FVector Position,Exit;
    if (!C || !C->HasAuthority() || Ladder || !Target || !Target->CanInteract_Implementation(C)
        || !Target->ValidateRail(C,Position) || !Target->FindGroundExit(C,Exit)) return false;
    auto* RV=Target->GetAttachParentActor();
    const bool FromRoof=RV->GetActorTransform().InverseTransformPosition(C->GetActorLocation()).Z>Target->RoofSurfaceHeight;
    if(FromRoof)
    {
        UPrimitiveComponent* Roof=nullptr;FVector Supported;
        if(!Target->FindRoofExit(C,Supported,Roof) || FVector::DistSquared(C->GetActorLocation(),Supported)>FMath::Square(180.f))return false;
        Position+=FVector(0,0,Target->ClimbHeight);
        FHitResult Hit;FCollisionQueryParams Params(SCENE_QUERY_STAT(RVRoofReturn),false,C);
        const auto* Capsule=C->GetCapsuleComponent();
        if(GetWorld()->SweepSingleByChannel(Hit,C->GetActorLocation(),Position,FQuat::Identity,ECC_Pawn,
            FCollisionShape::MakeCapsule(Capsule->GetScaledCapsuleRadius(),Capsule->GetScaledCapsuleHalfHeight()),Params))return false;
    }
    C->GetCharacterMovement()->StopMovementImmediately();
    C->GetCharacterMovement()->CurrentFloor.Clear();
    C->SetBase(static_cast<FMovementBaseInterfaceData*>(nullptr));
    C->SetActorLocation(Position,false,nullptr,ETeleportType::TeleportPhysics);
    Ladder=Target; Target->Occupant=C;
    if (auto* Vehicle=Cast<ARVVehicleBase>(Target->GetAttachParentActor())) Vehicle->SetAuthorityDriveLock(C,true);
    OnRep_Ladder(); C->ForceNetUpdate(); Target->ForceNetUpdate(); return true;
}
void URVLadderClimbComponent::OnRep_Ladder()
{
    auto* C=Cast<ARVSurvivorCharacter>(GetOwner()); if (!C) return;
    auto* M=C->GetCharacterMovement();
    if (Ladder && !bApplied)
    {
        PreviousFlySpeed=M->MaxFlySpeed; bPreviousPlaneConstraint=M->bConstrainToPlane;
        PreviousPlaneNormal=M->GetPlaneConstraintNormal(); PreviousPlaneOrigin=M->GetPlaneConstraintOrigin();
        bPreviousPhysicsInteraction=M->bEnablePhysicsInteraction; M->bEnablePhysicsInteraction=false;
        const auto* Platform=Ladder->GetAttachParentActor();
        M->SetPlaneConstraintNormal(Platform?Platform->GetActorForwardVector():FVector::ForwardVector);
        M->SetPlaneConstraintOrigin(Ladder->BottomWorld()); M->SetPlaneConstraintEnabled(true);
        M->MaxFlySpeed=100; M->StopMovementImmediately(); M->SetMovementMode(MOVE_Flying); bApplied=true;
    }
    else if (!Ladder && bApplied)
    {
        M->SetPlaneConstraintEnabled(false); M->SetPlaneConstraintNormal(PreviousPlaneNormal);
        M->SetPlaneConstraintOrigin(PreviousPlaneOrigin); M->SetPlaneConstraintEnabled(bPreviousPlaneConstraint);
        M->bEnablePhysicsInteraction=bPreviousPhysicsInteraction;
        M->MaxFlySpeed=PreviousFlySpeed; M->StopMovementImmediately(); M->SetMovementMode(MOVE_Walking); bApplied=false;
    }
}
void URVLadderClimbComponent::ClimbInput(float Value)
{
    auto* C=Cast<ARVSurvivorCharacter>(GetOwner()); if (!C || !Ladder) return;
    const float Height=C->GetActorLocation().Z-Ladder->BottomWorld().Z;
    if ((Value>0 && Height<Ladder->ClimbHeight-2) || (Value<0 && Height>2)) C->AddMovementInput(FVector::UpVector,Value);
}
bool URVLadderClimbComponent::EndAuthority()
{
    auto* C=Cast<ARVSurvivorCharacter>(GetOwner()); if (!C || !C->HasAuthority() || !Ladder) return false;
    FVector Exit;UPrimitiveComponent* Floor=nullptr;
    const float Height=C->GetActorLocation().Z-Ladder->BottomWorld().Z;
    const bool Top=Height>=Ladder->ClimbHeight-30;
    if(Top)
    {
        if(!Ladder->FindRoofExit(C,Exit,Floor))return false;
        FHitResult Hit;FCollisionQueryParams Params(SCENE_QUERY_STAT(RVRoofDismount),false,C);
        const auto* Capsule=C->GetCapsuleComponent();
        if(GetWorld()->SweepSingleByChannel(Hit,C->GetActorLocation(),Exit,FQuat::Identity,ECC_Pawn,
            FCollisionShape::MakeCapsule(Capsule->GetScaledCapsuleRadius(),Capsule->GetScaledCapsuleHalfHeight()),Params))return false;
    }
    else if(Height>30 || !Ladder->FindGroundExit(C,Exit))return false;
    auto* Old=Ladder.Get(); Ladder=nullptr; Old->Occupant=nullptr;
    RoofLadder=Top?Old:nullptr;
    if (!Top)if(auto* RV=Cast<ARVVehicleBase>(Old->GetAttachParentActor()))RV->SetAuthorityDriveLock(C,false);
    C->SetActorLocation(Exit,false,nullptr,ETeleportType::TeleportPhysics);
    OnRep_Ladder();
    if(Floor)
    {
        auto* M=C->GetCharacterMovement();M->FindFloor(Exit,M->CurrentFloor,false);
        auto BaseData=MovementBaseUtility::GetMovementBaseDataFromPhysicsOwner(Floor);C->SetBase(&BaseData);
        if(auto* Frame=C->FindComponentByClass<URVPassengerReferenceFrameComponent>())Frame->TickComponent(0,LEVELTICK_All,nullptr);
        C->SetBase(&BaseData);
    }
    C->ForceNetUpdate(); Old->ForceNetUpdate(); return true;
}
void URVLadderClimbComponent::ServerExit_Implementation() { EndAuthority(); }
void URVLadderClimbComponent::TickComponent(float Delta,ELevelTick Type,FActorComponentTickFunction* Function)
{
    Super::TickComponent(Delta,Type,Function);
    if(RoofLadder && !Ladder && GetOwner()->HasAuthority())
    {
        auto* RV=Cast<ARVVehicleBase>(RoofLadder->GetAttachParentActor());
        if(!RV || RV->GetActorTransform().InverseTransformPosition(GetOwner()->GetActorLocation()).Z<RoofLadder->RoofSurfaceHeight-40)
        {if(RV)RV->SetAuthorityDriveLock(GetOwner(),false);RoofLadder=nullptr;GetOwner()->ForceNetUpdate();}
    }
    if (!Ladder) return;
    auto* C=Cast<ARVSurvivorCharacter>(GetOwner()); if (!C) return;
    auto* M=C->GetCharacterMovement(); const float Height=C->GetActorLocation().Z-Ladder->BottomWorld().Z;
    if ((Height>=Ladder->ClimbHeight-2 && M->Velocity.Z>0) || (Height<=2 && M->Velocity.Z<0)) M->Velocity.Z=0;
    if (C->HasAuthority() && FVector::DistSquared2D(C->GetActorLocation(),Ladder->BottomWorld())>FMath::Square(20.f))
    { M->StopMovementImmediately(); }
}
void URVLadderClimbComponent::EndPlay(const EEndPlayReason::Type Reason)
{
    if (GetOwner()->HasAuthority())
    {
        if(Ladder){if(auto* RV=Cast<ARVVehicleBase>(Ladder->GetAttachParentActor()))RV->SetAuthorityDriveLock(GetOwner(),false);Ladder->Occupant=nullptr;Ladder->ForceNetUpdate();}
        if(RoofLadder)if(auto* RV=Cast<ARVVehicleBase>(RoofLadder->GetAttachParentActor()))RV->SetAuthorityDriveLock(GetOwner(),false);
    }
    Super::EndPlay(Reason);
}
