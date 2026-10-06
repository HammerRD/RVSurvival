#include "Vehicles/RVResourcePoint.h"
#include "Vehicles/RVSystemsMotorhome.h"
#include "Player/RVPlayerController.h"
#include "Components/StaticMeshComponent.h"
#include "Net/UnrealNetwork.h"
ARVResourcePoint::ARVResourcePoint()
{
    bAlwaysRelevant=true; SetReplicateMovement(true);
    Mesh->SetRelativeScale3D(FVector(.15,.05,.2));
    Mesh->SetCollisionEnabled(ECollisionEnabled::QueryOnly); Mesh->SetCollisionResponseToAllChannels(ECR_Ignore);
    Mesh->SetCollisionResponseToChannel(ECC_Visibility,ECR_Block);
}
void ARVResourcePoint::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{ Super::GetLifetimeReplicatedProps(OutLifetimeProps); DOREPLIFETIME(ARVResourcePoint,Vehicle); DOREPLIFETIME(ARVResourcePoint,bFuelFill); }
FText ARVResourcePoint::GetInteractionText_Implementation(APawn*) const
{ return FText::FromString(bFuelFill?TEXT("Hold E: fuel fill | select owned can, F to refuel"):TEXT("Hold E: RV electrical control panel")); }
void ARVResourcePoint::CompleteInteraction_Implementation(APawn* Pawn)
{
    if(!HasAuthority() || !CanInteract_Implementation(Pawn) || !Vehicle) return;
    if(auto* PC=Cast<ARVPlayerController>(Pawn->GetController()))
    { PC->ResourcePoint=this; PC->ResourceFeedback=TEXT("Panel ready"); PC->ForceNetUpdate(); }
}
