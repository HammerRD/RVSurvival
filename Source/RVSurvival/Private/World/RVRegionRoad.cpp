#include "World/RVRegionRoad.h"
#include "Components/SplineComponent.h"
#include "Components/SplineMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "UObject/ConstructorHelpers.h"
ARVRegionRoad::ARVRegionRoad()
{
    Route=CreateDefaultSubobject<USplineComponent>(TEXT("Route"));SetRootComponent(Route);
    Route->SetMobility(EComponentMobility::Static);
    static ConstructorHelpers::FObjectFinder<UStaticMesh> Cube(TEXT("/Engine/BasicShapes/Cube.Cube"));
    if(Cube.Succeeded())RoadMesh=Cube.Object;
    Tags.Add(TEXT("RoadExclusion"));
}
void ARVRegionRoad::OnConstruction(const FTransform& Transform)
{Super::OnConstruction(Transform);RebuildRoad();}
void ARVRegionRoad::RebuildRoad()
{
#if WITH_EDITOR
    if(GetWorld() && GetWorld()->IsGameWorld())return;
    TArray<USplineMeshComponent*> Old;GetComponents(Old);
    for(auto* Component:Old)if(Component->ComponentTags.Contains(TEXT("AuthoredRoad")))Component->DestroyComponent();
    if(!RoadMesh || !FMath::IsFinite(WidthCm))return;
    const float CrossSection=FMath::Max(1.f,RoadMesh->GetBoundingBox().GetSize().Y);
    for(int32 Index=0;Index<Route->GetNumberOfSplinePoints()-1;++Index)
    {
        auto* Mesh=NewObject<USplineMeshComponent>(this);
        Mesh->CreationMethod=EComponentCreationMethod::Instance;AddInstanceComponent(Mesh);
        Mesh->ComponentTags.Add(TEXT("AuthoredRoad"));Mesh->SetupAttachment(Route);
        Mesh->SetMobility(EComponentMobility::Static);Mesh->SetStaticMesh(RoadMesh);
        Mesh->SetForwardAxis(ESplineMeshAxis::X,false);
        Mesh->SetStartAndEnd(Route->GetLocationAtSplinePoint(Index,ESplineCoordinateSpace::Local),
            Route->GetTangentAtSplinePoint(Index,ESplineCoordinateSpace::Local),
            Route->GetLocationAtSplinePoint(Index+1,ESplineCoordinateSpace::Local),
            Route->GetTangentAtSplinePoint(Index+1,ESplineCoordinateSpace::Local),false);
        Mesh->SetStartScale(FVector2D(FMath::Clamp(WidthCm,400.f,2400.f)/CrossSection,.12f),false);
        Mesh->SetEndScale(Mesh->GetStartScale(),false);
        Mesh->SetCollisionProfileName(TEXT("BlockAll"));
        if(Asphalt)Mesh->SetMaterial(0,Asphalt);
        Mesh->RegisterComponent();Mesh->UpdateMesh();
        if(CenterPaint)
        {
            auto* Paint=NewObject<USplineMeshComponent>(this);
            Paint->CreationMethod=EComponentCreationMethod::Instance;AddInstanceComponent(Paint);
            Paint->ComponentTags.Add(TEXT("AuthoredRoad"));Paint->SetupAttachment(Route);
            Paint->SetMobility(EComponentMobility::Static);Paint->SetStaticMesh(RoadMesh);
            Paint->SetForwardAxis(ESplineMeshAxis::X,false);
            Paint->SetStartAndEnd(Mesh->GetStartPosition()+FVector(0,0,6.5),Mesh->GetStartTangent(),
                Mesh->GetEndPosition()+FVector(0,0,6.5),Mesh->GetEndTangent(),false);
            Paint->SetStartScale(FVector2D(12.f/CrossSection,.002f),false);Paint->SetEndScale(Paint->GetStartScale(),false);
            Paint->SetCollisionEnabled(ECollisionEnabled::NoCollision);Paint->SetMaterial(0,CenterPaint);
            Paint->RegisterComponent();Paint->UpdateMesh();
        }
    }
    MarkPackageDirty();
#endif
}
