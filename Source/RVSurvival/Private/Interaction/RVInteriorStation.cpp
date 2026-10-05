#include "Interaction/RVInteriorStation.h"
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
{ Super::GetLifetimeReplicatedProps(OutLifetimeProps); DOREPLIFETIME(ARVInteriorStation, StationName); }
FText ARVInteriorStation::GetInteractionText_Implementation(APawn*) const
{ return FText::Format(NSLOCTEXT("RV", "StationPlaceholder", "Hold E: {0} (prototype checks: {1})"), FText::FromName(StationName), FText::AsNumber(InteractionCount)); }
