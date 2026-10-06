#include "Survival/RVRestPoint.h"
#include "Interaction/RVInteractionTargetPresentationComponent.h"
#include "Vehicles/RVInteriorMotorhome.h"
#include "Components/CapsuleComponent.h"
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
}
void ARVRestPoint::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{ Super::GetLifetimeReplicatedProps(OutLifetimeProps); DOREPLIFETIME(ARVRestPoint,DisplayName); DOREPLIFETIME(ARVRestPoint,MaximumPlatformSpeed); DOREPLIFETIME(ARVRestPoint,Occupant);
  DOREPLIFETIME(ARVRestPoint,bUseLyingPose); DOREPLIFETIME(ARVRestPoint,LyingOffset); DOREPLIFETIME(ARVRestPoint,LyingRotation); DOREPLIFETIME(ARVRestPoint,WakeAisleLocation); }
bool ARVRestPoint::FindWakePosition(ARVSurvivorCharacter* Character,FVector& Position,UPrimitiveComponent*& Floor) const
{
    if (auto* RV=Cast<ARVInteriorMotorhome>(GetAttachParentActor()))
        return RV->FindSafeInteriorPosition(Character,WakeAisleLocation,Position,Floor);
    return false; // Other rest locations can supply a platform placement policy before enabling lying.
}
bool ARVRestPoint::ValidateLyingPosition(ARVSurvivorCharacter* Character) const
{
    if (!Character) return false;
    const FVector Position=GetActorLocation()+GetActorQuat().RotateVector(LyingOffset);
    FCollisionQueryParams Params(SCENE_QUERY_STAT(RVBedClearance),false,Character);
    // The horizontal prototype body is 168 x 32 x 32 cm. Include furniture and other players.
    return !GetWorld()->OverlapBlockingTestByChannel(Position,GetActorQuat()*LyingRotation.Quaternion(),ECC_Pawn,
        FCollisionShape::MakeBox(FVector(85,18,18)),Params);
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
