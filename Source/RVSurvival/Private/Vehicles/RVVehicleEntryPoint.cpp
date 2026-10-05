#include "Vehicles/RVVehicleEntryPoint.h"
#include "Vehicles/RVVehicleSeatComponent.h"
#include "Vehicles/RVVehicleBase.h"
#include "Player/RVSurvivorCharacter.h"
#include "Components/BoxComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/TextRenderComponent.h"
#include "UObject/ConstructorHelpers.h"
#include "Net/UnrealNetwork.h"
ARVVehicleEntryPoint::ARVVehicleEntryPoint()
{
    bReplicates = true; bAlwaysRelevant = true;
    auto* Box = CreateDefaultSubobject<UBoxComponent>(TEXT("EntryTrace")); SetRootComponent(Box);
    Box->SetBoxExtent(FVector(35, 12, 45)); Box->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
    Box->SetCollisionResponseToAllChannels(ECR_Ignore); Box->SetCollisionResponseToChannel(ECC_Visibility, ECR_Block);
    auto* Panel = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("PrototypeEntryPanel")); Panel->SetupAttachment(Box);
    static ConstructorHelpers::FObjectFinder<UStaticMesh> Cube(TEXT("/Engine/BasicShapes/Cube.Cube"));
    Panel->SetStaticMesh(Cube.Object); Panel->SetRelativeScale3D(FVector(.7, .24, .9)); Panel->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Label = CreateDefaultSubobject<UTextRenderComponent>(TEXT("SeatLabel")); Label->SetupAttachment(Box);
    Label->SetRelativeLocation(FVector(0, -15, 55)); Label->SetRelativeRotation(FRotator(0, -90, 0)); Label->SetWorldSize(18);
}
void ARVVehicleEntryPoint::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{ Super::GetLifetimeReplicatedProps(OutLifetimeProps); DOREPLIFETIME(ARVVehicleEntryPoint, Seat); }
void ARVVehicleEntryPoint::BeginPlay() { Super::BeginPlay(); OnRep_Seat(); }
void ARVVehicleEntryPoint::OnRep_Seat()
{
    if (!Seat) return;
    Label->SetText(Seat->SeatLabel);
    Label->SetRelativeRotation(FRotator(0, Seat->bDriverSeat ? -90 : 90, 0));
    Label->SetRelativeLocation(FVector(0, Seat->bDriverSeat ? -15 : 15, 55));
}
bool ARVVehicleEntryPoint::CanInteract_Implementation(APawn* Pawn) const
{
    const auto* Vehicle = Seat ? Cast<ARVVehicleBase>(Seat->GetOwner()) : nullptr;
    return Vehicle && Vehicle->CanEnter(Seat, Cast<ARVSurvivorCharacter>(Pawn));
}
FText ARVVehicleEntryPoint::GetInteractionText_Implementation(APawn*) const
{ return FText::Format(NSLOCTEXT("RV", "EnterSeat", "Hold E: Enter {0}"), Seat ? Seat->SeatLabel : FText::GetEmpty()); }
void ARVVehicleEntryPoint::CompleteInteraction_Implementation(APawn* Pawn)
{ if (HasAuthority() && Seat) if (auto* V = Cast<ARVVehicleBase>(Seat->GetOwner())) V->TryEnter(Seat, Cast<ARVSurvivorCharacter>(Pawn)); }
