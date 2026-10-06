#include "Survival/RVRestPoint.h"
#include "Survival/RVNeedsComponent.h"
#include "Player/RVPlayerState.h"
#include "Player/RVSurvivorCharacter.h"
#include "Components/StaticMeshComponent.h"
#include "Net/UnrealNetwork.h"
ARVRestPoint::ARVRestPoint()
{
    bAlwaysRelevant=true; SetReplicateMovement(true);
    DisplayName=FText::FromString(TEXT("Rest location"));
    Mesh->SetWorldScale3D(FVector(.15)); Mesh->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
    Mesh->SetCollisionResponseToAllChannels(ECR_Ignore); Mesh->SetCollisionResponseToChannel(ECC_Visibility,ECR_Block);
}
void ARVRestPoint::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{ Super::GetLifetimeReplicatedProps(OutLifetimeProps); DOREPLIFETIME(ARVRestPoint,DisplayName); DOREPLIFETIME(ARVRestPoint,MaximumPlatformSpeed); DOREPLIFETIME(ARVRestPoint,Occupant); }
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
