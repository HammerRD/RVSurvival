#include "Interaction/RVInteriorStation.h"
#include "Vehicles/RVSystemsMotorhome.h"
#include "Resources/RVElectricalComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/TextRenderComponent.h"
#include "Net/UnrealNetwork.h"
ARVInteriorStation::ARVInteriorStation()
{
    bAlwaysRelevant = true; Mesh->SetMobility(EComponentMobility::Movable);
    Mesh->SetRelativeScale3D(FVector(.2,.2,.2)); Mesh->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
    Mesh->SetCollisionResponseToAllChannels(ECR_Ignore); Mesh->SetCollisionResponseToChannel(ECC_Visibility,ECR_Block);
    // The temporary HUD supplies station identity/count without backwards text in the narrow aisle.
    Label->SetVisibility(false);
}
void ARVInteriorStation::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{ Super::GetLifetimeReplicatedProps(OutLifetimeProps); DOREPLIFETIME(ARVInteriorStation, StationName); DOREPLIFETIME(ARVInteriorStation,RequiredPowerLoad); }
FText ARVInteriorStation::GetInteractionText_Implementation(APawn*) const
{ return FText::Format(NSLOCTEXT("RV", "StationPlaceholder", "Hold E: {0} (prototype checks: {1})"), FText::FromName(StationName), FText::AsNumber(InteractionCount)); }

bool ARVInteriorStation::CanInteract_Implementation(APawn* Pawn) const
{
    if(!Super::CanInteract_Implementation(Pawn)) return false;
    if(RequiredPowerLoad.IsNone()) return true;
    const auto* V=Cast<ARVSystemsMotorhome>(GetAttachParentActor());
    return V && V->Electrical->IsLoadPowered(RequiredPowerLoad);
}
