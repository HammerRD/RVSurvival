#include "Inventory/RVWorldItem.h"
#include "Interaction/RVInteractionTargetPresentationComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "UObject/ConstructorHelpers.h"
#include "GameFramework/Pawn.h"
#include "Net/UnrealNetwork.h"
ARVInventoryInteractable::ARVInventoryInteractable()
{
    bReplicates=true;
    Mesh=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh")); SetRootComponent(Mesh);
    static ConstructorHelpers::FObjectFinder<UStaticMesh> Cube(TEXT("/Engine/BasicShapes/Cube.Cube"));
    if(Cube.Succeeded()) Mesh->SetStaticMesh(Cube.Object);
    Mesh->SetMobility(EComponentMobility::Movable);
}
bool ARVInventoryInteractable::CanInteract_Implementation(APawn* Pawn) const
{ return IsValid(Pawn) && Pawn->GetController(); }
ARVWorldItem::ARVWorldItem()
{
    SetReplicateMovement(true);
    Mesh->SetRelativeScale3D(FVector(.2));
    Mesh->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
    Mesh->SetCollisionResponseToAllChannels(ECR_Ignore);
    Mesh->SetCollisionResponseToChannel(ECC_Visibility,ECR_Block);
}
void ARVWorldItem::BeginPlay()
{
    Super::BeginPlay();
    if(HasAuthority() && !Item.Id.IsValid()) Item.Id=FGuid::NewGuid();
    if(HasAuthority() && Item.Definition && Item.Definition->Fuel.bFuelContainer && !Item.bFuelInitialized)
    { Item.bFuelInitialized=true; Item.FuelLitres=Item.Definition->Fuel.InitialLitres; }
    if(HasAuthority() && Item.Definition && Item.Definition->Combat.bMagazine && !Item.bMagazineInitialized)
    {Item.bMagazineInitialized=true;Item.MagazineRounds=Item.Definition->Combat.InitialRounds;}
    OnRep_Item();
}
bool ARVWorldItem::IsNetRelevantFor(const AActor* RealViewer, const AActor* ViewTarget, const FVector& SrcLocation) const
{
    // Cabin floors are query components, not skeletal meshes. Keep their cargo relevant
    // whenever the platform is relevant; unattached pickups retain normal distance culling.
    if(const AActor* Platform=GetAttachParentActor()) return Platform->IsNetRelevantFor(RealViewer,ViewTarget,SrcLocation);
    return Super::IsNetRelevantFor(RealViewer,ViewTarget,SrcLocation);
}
void ARVWorldItem::OnRep_Item()
{ if(Item.Definition && !Item.Definition->WorldMesh.IsNull()) {Mesh->SetStaticMesh(Item.Definition->WorldMesh.LoadSynchronous());Mesh->SetRelativeScale3D(Item.Definition->WorldVisualScale);} }
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
    auto* Inventory=Pawn->FindComponentByClass<URVInventoryComponent>();
    if(Inventory->AddAuthority(Item,Error)) { Inventory->Feedback.Empty(); bClaimed=true; Destroy(); }
    else Inventory->Feedback=Error;
    Pawn->ForceNetUpdate();
}
ARVStoragePoint::ARVStoragePoint()
{
    CreateDefaultSubobject<URVInteractionTargetPresentationComponent>(TEXT("TargetPresentation"));
    bAlwaysRelevant=true; SetReplicateMovement(true);
    Container=CreateDefaultSubobject<URVContainerComponent>(TEXT("Container"));
    Mesh->SetRelativeScale3D(FVector(.2));
    Mesh->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
    Mesh->SetCollisionResponseToAllChannels(ECR_Ignore);
    Mesh->SetCollisionResponseToChannel(ECC_Visibility,ECR_Block);
}
FText ARVStoragePoint::GetInteractionText_Implementation(APawn*) const
{ return FText::FromString(TEXT("Hold E: open ")+Container->DisplayName.ToString()); }
void ARVStoragePoint::CompleteInteraction_Implementation(APawn* Pawn)
{
    if(!HasAuthority() || !CanInteract_Implementation(Pawn)) return;
    if(auto* Inventory=Pawn->FindComponentByClass<URVInventoryComponent>()) Inventory->OpenContainerAuthority(Container);
}
ARVExteriorStoragePoint::ARVExteriorStoragePoint() { Mesh->SetVisibility(false); }
void ARVExteriorStoragePoint::ConfigureQueryExtent(FVector Extent) { Mesh->SetRelativeScale3D(Extent/50.f); }
void ARVExteriorStoragePoint::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{ Super::GetLifetimeReplicatedProps(OutLifetimeProps); DOREPLIFETIME(ARVExteriorStoragePoint,DoorPartName); }


