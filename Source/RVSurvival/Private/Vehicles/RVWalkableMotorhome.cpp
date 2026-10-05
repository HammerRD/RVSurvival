#include "Vehicles/RVWalkableMotorhome.h"
#include "Vehicles/RVVehicleSeatComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "UObject/ConstructorHelpers.h"
ARVWalkableMotorhome::ARVWalkableMotorhome(const FObjectInitializer& Init) : Super(Init)
{
    PrototypeBody->SetVisibility(false); PrototypeBody->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    PrototypeCab->SetVisibility(false); PrototypeCab->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    static ConstructorHelpers::FObjectFinder<UStaticMesh> Cube(TEXT("/Engine/BasicShapes/Cube.Cube"));
    auto Part = [this](const TCHAR* Name, FVector Position, FVector Scale)
    {
        auto* P = CreateDefaultSubobject<UStaticMeshComponent>(Name); P->SetupAttachment(GetMesh());
        P->SetStaticMesh(Cube.Object); P->SetRelativeLocation(Position); P->SetRelativeScale3D(Scale);
        P->SetMobility(EComponentMobility::Movable); P->SetCollisionProfileName(TEXT("BlockAll"));
        P->SetCollisionEnabled(ECollisionEnabled::QueryOnly); return P;
    };
    InteriorFloor = Part(TEXT("InteriorFloor"), FVector(-75,0,105), FVector(6.5,2.8,.2));
    InteriorFloor->ComponentTags.Add(TEXT("RVPassengerPlatform"));
    Part(TEXT("LeftWall"), FVector(-75,-145,235), FVector(6.5,.1,2.4));
    Part(TEXT("RightWall"), FVector(-75,145,235), FVector(6.5,.1,2.4));
    Part(TEXT("FrontWall"), FVector(255,0,235), FVector(.1,3,2.4));
    Part(TEXT("RearLeft"), FVector(-405,-105,235), FVector(.1,.8,2.4));
    Part(TEXT("RearRight"), FVector(-405,105,235), FVector(.1,.8,2.4));
    // Open rear doorway and broad three-step entry: normal CharacterMovement can walk in/out at rest.
    auto* S1 = Part(TEXT("EntryStepLow"), FVector(-540,0,15), FVector(.9,1.3,.3));
    auto* S2 = Part(TEXT("EntryStepMiddle"), FVector(-495,0,45), FVector(.9,1.3,.9));
    auto* S3 = Part(TEXT("EntryStepHigh"), FVector(-450,0,75), FVector(.9,1.3,1.5));
    S1->ComponentTags.Add(TEXT("RVPassengerPlatform")); S2->ComponentTags.Add(TEXT("RVPassengerPlatform")); S3->ComponentTags.Add(TEXT("RVPassengerPlatform"));
    DriverSeat->SetRelativeLocation(FVector(150,-70,205)); PassengerSeat->SetRelativeLocation(FVector(150,70,205));
}
