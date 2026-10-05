#include "Inventory/RVWorldItem.h"
#include "Components/StaticMeshComponent.h"
#include "Components/TextRenderComponent.h"
#include "GameFramework/Pawn.h"
#include "Net/UnrealNetwork.h"
ARVWorldItem::ARVWorldItem()
{
    SetReplicateMovement(true);
    Mesh->SetRelativeScale3D(FVector(.2));
    Mesh->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
    Mesh->SetCollisionResponseToAllChannels(ECR_Ignore);
    Mesh->SetCollisionResponseToChannel(ECC_Visibility,ECR_Block);
    Label->SetVisibility(false);
}
void ARVWorldItem::BeginPlay()
{
    Super::BeginPlay();
    if(HasAuthority() && !Item.Id.IsValid()) Item.Id=FGuid::NewGuid();
    if(Item.Definition && !Item.Definition->WorldMesh.IsNull()) Mesh->SetStaticMesh(Item.Definition->WorldMesh.LoadSynchronous());
}
void ARVWorldItem::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{ Super::GetLifetimeReplicatedProps(OutLifetimeProps); DOREPLIFETIME(ARVWorldItem,Item); }
bool ARVWorldItem::CanInteract_Implementation(APawn* Pawn) const
{ return !bClaimed && Item.Definition && IsValid(Pawn) && Pawn->GetController() && Pawn->FindComponentByClass<URVInventoryComponent>(); }
FText ARVWorldItem::GetInteractionText_Implementation(APawn* Pawn) const
{
    if(!Item.Definition) return FText::GetEmpty();
    const auto* Inventory=Pawn?Pawn->FindComponentByClass<URVInventoryComponent>():nullptr;
    const FString Error=Inventory?Inventory->CanAccept(Item):TEXT("No inventory");
    return FText::FromString(Error.IsEmpty()?FString::Printf(TEXT("Hold E: pick up %s (%d)"),*Item.Definition->DisplayName.ToString(),Item.Quantity):Error);
}
void ARVWorldItem::CompleteInteraction_Implementation(APawn* Pawn)
{
    if(!HasAuthority() || !CanInteract_Implementation(Pawn)) return;
    FString Error;
    if(Pawn->FindComponentByClass<URVInventoryComponent>()->AddAuthority(Item,Error)) { bClaimed=true; Destroy(); }
}
ARVStoragePoint::ARVStoragePoint()
{
    bAlwaysRelevant=true; SetReplicateMovement(true);
    Container=CreateDefaultSubobject<URVContainerComponent>(TEXT("Container"));
    Mesh->SetRelativeScale3D(FVector(.2));
    Mesh->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
    Mesh->SetCollisionResponseToAllChannels(ECR_Ignore);
    Mesh->SetCollisionResponseToChannel(ECC_Visibility,ECR_Block);
    Label->SetVisibility(false);
}
FText ARVStoragePoint::GetInteractionText_Implementation(APawn*) const
{ return FText::FromString(TEXT("Hold E: open ")+Container->DisplayName.ToString()); }
void ARVStoragePoint::CompleteInteraction_Implementation(APawn* Pawn)
{
    if(!HasAuthority() || !IsValid(Pawn)) return;
    if(auto* Inventory=Pawn->FindComponentByClass<URVInventoryComponent>()) Inventory->OpenContainerAuthority(Container);
}


