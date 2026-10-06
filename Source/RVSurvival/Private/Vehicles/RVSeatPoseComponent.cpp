#include "Vehicles/RVSeatPoseComponent.h"
#include "Vehicles/RVVehicleSeatComponent.h"
#include "Player/RVSurvivorCharacter.h"
#include "Components/StaticMeshComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "GameFramework/PlayerController.h"
URVSeatPoseComponent::URVSeatPoseComponent()
{ PrimaryComponentTick.bCanEverTick=true; PrimaryComponentTick.TickInterval=.05f; }
void URVSeatPoseComponent::BeginPlay()
{
    Super::BeginPlay(); auto* C=Cast<ARVSurvivorCharacter>(GetOwner()); if (!C) return;
    auto Add=[this,C](FVector Location,FVector Scale)
    {
        auto* Part=NewObject<UStaticMeshComponent>(C);
        Part->SetupAttachment(C->GetRootComponent());
        Part->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Cube.Cube")));
        Part->SetRelativeLocation(Location); Part->SetRelativeScale3D(Scale);
        Part->SetCollisionEnabled(ECollisionEnabled::NoCollision); Part->SetHiddenInGame(true);
        Part->SetOwnerNoSee(true); Part->RegisterComponent(); Parts.Add(Part);
    };
    Add(FVector(0,0,28),FVector(.28,.42,.56));
    Add(FVector(0,0,68),FVector(.27));
    for (float Y : {-12.f,12.f})
    { Add(FVector(25,Y,-6),FVector(.50,.16,.16)); Add(FVector(43,Y,-30),FVector(.16,.16,.48)); }
}
void URVSeatPoseComponent::TickComponent(float Delta,ELevelTick Type,FActorComponentTickFunction* Function)
{
    Super::TickComponent(Delta,Type,Function);
    auto* C=Cast<ARVSurvivorCharacter>(GetOwner()); if (!C) return;
    const auto* Seat=Cast<URVVehicleSeatComponent>(C->GetRootComponent()->GetAttachParent());
    const bool Active=C->SeatedVehicle && Seat && Seat->bUsePrototypeSittingPose;
    if (Active==bActive) return;
    bActive=Active;
    if (Active)
    {
        if (auto* PC=Cast<APlayerController>(C->GetController());PC && PC->IsLocalController())
            PC->SetControlRotation(FRotator(0,Seat->GetComponentRotation().Yaw,0));
        TArray<USceneComponent*> Children; C->GetMesh()->GetChildrenComponents(true,Children); Children.Add(C->GetMesh());
        for (auto* Child:Children) if (auto* Part=Cast<UPrimitiveComponent>(Child))
        { PreviousVisibility.Emplace(TWeakObjectPtr<UPrimitiveComponent>(Part),bool(Part->bHiddenInGame)); Part->SetHiddenInGame(true); }
    }
    else
    { for (auto& State:PreviousVisibility) if (auto* Part=State.Key.Get()) Part->SetHiddenInGame(State.Value); PreviousVisibility.Reset(); }
    for (const auto& Part:Parts) if (Part) Part->SetHiddenInGame(!Active);
}
