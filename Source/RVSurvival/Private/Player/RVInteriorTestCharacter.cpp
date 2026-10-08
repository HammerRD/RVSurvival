#include "Player/RVInteriorTestCharacter.h"
#include "Components/StaticMeshComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "UObject/ConstructorHelpers.h"

ARVInteriorTestCharacter::ARVInteriorTestCharacter(const FObjectInitializer& Init) : Super(Init)
{
    // Follow the native smoothed visual mesh rather than the correction capsule.
    GetMesh()->SetRelativeLocationAndRotation(FVector::ZeroVector, FRotator::ZeroRotator);
    static ConstructorHelpers::FObjectFinder<UStaticMesh> Cylinder(TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
    static ConstructorHelpers::FObjectFinder<UStaticMesh> Sphere(TEXT("/Engine/BasicShapes/Sphere.Sphere"));
    PrototypeTorso = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("PrototypeTorso"));
    PrototypeTorso->SetupAttachment(GetMesh()); PrototypeTorso->SetStaticMesh(Cylinder.Object);
    PrototypeTorso->SetRelativeLocation(FVector(0,0,-15)); PrototypeTorso->SetRelativeScale3D(FVector(.45,.45,1.4));
    PrototypeHead = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("PrototypeHead"));
    PrototypeHead->SetupAttachment(GetMesh()); PrototypeHead->SetStaticMesh(Sphere.Object);
    PrototypeHead->SetRelativeLocation(FVector(0,0,64)); PrototypeHead->SetRelativeScale3D(FVector(.35));
    for (auto* Part : {PrototypeTorso.Get(), PrototypeHead.Get()})
    {
        Part->ComponentTags.Add(TEXT("RVPrototypeCharacterVisual"));
        Part->SetCollisionEnabled(ECollisionEnabled::NoCollision);
        Part->SetOwnerNoSee(true);
    }
}
