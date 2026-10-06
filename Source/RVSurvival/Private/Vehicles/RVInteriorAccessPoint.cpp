#include "Vehicles/RVInteriorAccessPoint.h"
#include "Interaction/RVInteractionTargetPresentationComponent.h"
#include "Vehicles/RVInteriorMotorhome.h"
#include "Vehicles/RVInteractiveDoor.h"
#include "Player/RVSurvivorCharacter.h"
#include "Player/RVPassengerReferenceFrameComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Net/UnrealNetwork.h"
ARVInteriorAccessPoint::ARVInteriorAccessPoint()
{
    CreateDefaultSubobject<URVInteractionTargetPresentationComponent>(TEXT("TargetPresentation"));
    bAlwaysRelevant=true; Mesh->SetRelativeScale3D(FVector(.15));
    Mesh->SetCollisionEnabled(ECollisionEnabled::QueryOnly); Mesh->SetCollisionResponseToAllChannels(ECR_Ignore);
    Mesh->SetCollisionResponseToChannel(ECC_Visibility,ECR_Block);
}
void ARVInteriorAccessPoint::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{ Super::GetLifetimeReplicatedProps(OutLifetimeProps); DOREPLIFETIME(ARVInteriorAccessPoint,Vehicle); DOREPLIFETIME(ARVInteriorAccessPoint,bEnter); }
bool ARVInteriorAccessPoint::CanInteract_Implementation(APawn* Pawn) const
{
    const auto* C=Cast<ARVSurvivorCharacter>(Pawn);
    if (Vehicle && Vehicle->HouseDoor && !Vehicle->HouseDoor->bOpen) return false;
    if (!Vehicle || !C || !C->GetController() || C->SeatedVehicle || Vehicle->GetVelocity().Size()>Vehicle->MaxEntryExitSpeed) return false;
    const auto* Frame=C->FindComponentByClass<URVPassengerReferenceFrameComponent>();
    const bool Inside=Frame && Frame->ReferenceFrame==Vehicle;
    return bEnter?!Inside:Inside;
}
FText ARVInteriorAccessPoint::GetInteractionText_Implementation(APawn*) const
{ return FText::FromString(bEnter?TEXT("Hold E: enter RV aisle"):TEXT("Hold E: leave RV through side door")); }
void ARVInteriorAccessPoint::CompleteInteraction_Implementation(APawn* Pawn)
{ if (HasAuthority() && CanInteract_Implementation(Pawn)) Vehicle->TryStandingDoor(Cast<ARVSurvivorCharacter>(Pawn),bEnter); }
