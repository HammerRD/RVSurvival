#include "Player/RVLadderClimbComponent.h"
#include "Vehicles/RVLadder.h"
#include "Vehicles/RVVehicleBase.h"
#include "Player/RVSurvivorCharacter.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Net/UnrealNetwork.h"
URVLadderClimbComponent::URVLadderClimbComponent()
{ SetIsReplicatedByDefault(true); PrimaryComponentTick.bCanEverTick=true; }
void URVLadderClimbComponent::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{ Super::GetLifetimeReplicatedProps(OutLifetimeProps); DOREPLIFETIME(URVLadderClimbComponent,Ladder); }
bool URVLadderClimbComponent::BeginAuthority(ARVLadder* Target)
{
    auto* C=Cast<ARVSurvivorCharacter>(GetOwner()); FVector Position,Exit;
    if (!C || !C->HasAuthority() || Ladder || !Target || !Target->CanInteract_Implementation(C)
        || !Target->ValidateRail(C,Position) || !Target->FindGroundExit(C,Exit)) return false;
    C->GetCharacterMovement()->StopMovementImmediately();
    C->GetCharacterMovement()->CurrentFloor.Clear();
    C->SetBase(static_cast<FMovementBaseInterfaceData*>(nullptr));
    C->SetActorLocation(Position,false,nullptr,ETeleportType::TeleportPhysics);
    Ladder=Target; Target->Occupant=C;
    if (auto* RV=Cast<ARVVehicleBase>(Target->GetAttachParentActor())) RV->SetAuthorityDriveLock(Target,true);
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
    FVector Exit;
    // No unvalidated roof dismount: descend to the bottom before standing.
    if (C->GetActorLocation().Z-Ladder->BottomWorld().Z>30 || !Ladder->FindGroundExit(C,Exit)) return false;
    auto* Old=Ladder.Get(); Ladder=nullptr; Old->Occupant=nullptr;
    if (auto* RV=Cast<ARVVehicleBase>(Old->GetAttachParentActor())) RV->SetAuthorityDriveLock(Old,false);
    C->SetActorLocation(Exit,false,nullptr,ETeleportType::TeleportPhysics);
    OnRep_Ladder(); C->ForceNetUpdate(); Old->ForceNetUpdate(); return true;
}
void URVLadderClimbComponent::ServerExit_Implementation() { EndAuthority(); }
void URVLadderClimbComponent::TickComponent(float Delta,ELevelTick Type,FActorComponentTickFunction* Function)
{
    Super::TickComponent(Delta,Type,Function); if (!Ladder) return;
    auto* C=Cast<ARVSurvivorCharacter>(GetOwner()); if (!C) return;
    auto* M=C->GetCharacterMovement(); const float Height=C->GetActorLocation().Z-Ladder->BottomWorld().Z;
    if ((Height>=Ladder->ClimbHeight-2 && M->Velocity.Z>0) || (Height<=2 && M->Velocity.Z<0)) M->Velocity.Z=0;
    if (C->HasAuthority() && FVector::DistSquared2D(C->GetActorLocation(),Ladder->BottomWorld())>FMath::Square(20.f))
    { M->StopMovementImmediately(); }
}
void URVLadderClimbComponent::EndPlay(const EEndPlayReason::Type Reason)
{
    if (GetOwner()->HasAuthority() && Ladder)
    { if (auto* RV=Cast<ARVVehicleBase>(Ladder->GetAttachParentActor())) RV->SetAuthorityDriveLock(Ladder,false); Ladder->Occupant=nullptr; Ladder->ForceNetUpdate(); }
    Super::EndPlay(Reason);
}
