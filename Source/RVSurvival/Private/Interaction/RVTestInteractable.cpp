#include "Interaction/RVTestInteractable.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Components/TextRenderComponent.h"
#include "GameFramework/Pawn.h"
#include "Net/UnrealNetwork.h"
#include "UObject/ConstructorHelpers.h"
#include "Core/RVLog.h"
ARVTestInteractable::ARVTestInteractable()
{
    bReplicates = true;
    Mesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
    SetRootComponent(Mesh);
    static ConstructorHelpers::FObjectFinder<UStaticMesh> Cube(TEXT("/Engine/BasicShapes/Cube.Cube"));
    if (Cube.Succeeded()) Mesh->SetStaticMesh(Cube.Object);
    Mesh->SetCollisionProfileName(TEXT("BlockAll"));
    Label = CreateDefaultSubobject<UTextRenderComponent>(TEXT("Label"));
    Label->SetupAttachment(Mesh);
    Label->SetRelativeLocation(FVector(0, 0, 80));
    Label->SetWorldSize(24);
}
void ARVTestInteractable::BeginPlay() { Super::BeginPlay(); OnRep_InteractionCount(); }
bool ARVTestInteractable::CanInteract_Implementation(APawn* Interactor) const
{
    return IsValid(Interactor) && Interactor->GetController() && InteractionCount < MAX_int32;
}
FText ARVTestInteractable::GetInteractionText_Implementation(APawn* Interactor) const
{
    return NSLOCTEXT("RV", "TestInteraction", "Hold E to increment shared counter");
}
void ARVTestInteractable::CompleteInteraction_Implementation(APawn* Interactor)
{
    if (!HasAuthority() || !CanInteract_Implementation(Interactor)) return;
    ++InteractionCount;
    OnRep_InteractionCount();
    ForceNetUpdate();
    UE_LOG(LogRVNetworking, Log, TEXT("Shared counter %d; interactor %s"), InteractionCount, *GetNameSafe(Interactor));
}
void ARVTestInteractable::OnRep_InteractionCount()
{
    Label->SetText(FText::Format(NSLOCTEXT("RV", "Counter", "Shared count: {0}"), FText::AsNumber(InteractionCount)));
}
void ARVTestInteractable::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
    Super::GetLifetimeReplicatedProps(OutLifetimeProps);
    DOREPLIFETIME(ARVTestInteractable, InteractionCount);
}
