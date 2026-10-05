#include "Vehicles/RVInteriorMotorhome.h"
#include "Interaction/RVInteriorStation.h"
#include "Components/BoxComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "PhysicsEngine/PhysicsAsset.h"
#include "PhysicsEngine/SkeletalBodySetup.h"
#include "Engine/SkeletalMesh.h"
#if WITH_EDITOR
#include "StaticMeshAttributes.h"
#include "Engine/StaticMesh.h"
#endif
ARVInteriorMotorhome::ARVInteriorMotorhome(const FObjectInitializer& Init) : Super(Init)
{
    PrototypeBody->SetVisibility(false); PrototypeBody->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    PrototypeCab->SetVisibility(false); PrototypeCab->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    InteriorFloor = CreateDefaultSubobject<UBoxComponent>(TEXT("InteriorFloor")); InteriorFloor->SetupAttachment(GetMesh());
    InteriorFloor->SetMobility(EComponentMobility::Movable); InteriorFloor->SetCollisionProfileName(TEXT("BlockAll"));
    InteriorFloor->SetCollisionEnabled(ECollisionEnabled::QueryOnly); InteriorFloor->ComponentTags.Add(TEXT("RVPassengerPlatform"));
    // The rigid chassis supplies vehicle contacts; modular query collision supplies the cabin.
    GetMesh()->SetCollisionResponseToChannel(ECC_Pawn, ECR_Ignore);
    GetMesh()->SetCollisionResponseToChannel(ECC_Visibility, ECR_Ignore);
}
void ARVInteriorMotorhome::RefreshConfiguration() { OnConstruction(GetActorTransform()); }
TArray<FVector> ARVInteriorMotorhome::InspectArtSurfaces(UStaticMesh* Mesh)
{
    TArray<FVector> Points;
#if WITH_EDITOR
    if (!Mesh) return Points;
    auto* Description = Mesh->GetMeshDescription(0); if (!Description) return Points;
    FStaticMeshAttributes Attributes(*Description); const auto Positions = Attributes.GetVertexPositions();
    for (const auto Triangle : Description->Triangles().GetElementIDs())
    {
        const auto Corners = Description->GetTriangleVertexInstances(Triangle);
        const FVector A(Positions[Description->GetVertexInstanceVertex(Corners[0])]);
        const FVector B(Positions[Description->GetVertexInstanceVertex(Corners[1])]);
        const FVector C(Positions[Description->GetVertexInstanceVertex(Corners[2])]);
        const FVector N = FVector::CrossProduct(B-A,C-A).GetSafeNormal();
        if (FMath::Abs(N.Z) > .95) Points.Add((A+B+C)/3);
    }
#endif
    return Points;
}
void ARVInteriorMotorhome::OnConstruction(const FTransform& Transform)
{
    Super::OnConstruction(Transform);
    // Configuration can be edited on Blueprint defaults; templates have no world
    // and must not register presentation/collision components.
    if (IsTemplate() || !GetWorld()) return;
    for (const auto& Part : GeneratedParts) if (Part) Part->DestroyComponent(); GeneratedParts.Reset();
    GetMesh()->SetVisibility(false, false);
    for (const auto& Def : VisualParts)
    {
        if (!Def.Mesh) continue;
        auto* Part = NewObject<UStaticMeshComponent>(this, Def.Name);
        Part->SetMobility(EComponentMobility::Movable); Part->SetupAttachment(GetMesh());
        Part->SetStaticMesh(Def.Mesh); Part->SetRelativeTransform(Def.Transform);
        for (int32 Index = 0; Index < Def.Materials.Num(); ++Index)
            if (Def.Materials[Index]) Part->SetMaterial(Index, Def.Materials[Index]);
        Part->bDisallowNanite = Def.bDisallowNanite;
        Part->SetCollisionEnabled(ECollisionEnabled::NoCollision); Part->RegisterComponent(); GeneratedParts.Add(Part);
    }
    for (const auto& Def : InteriorCollision)
    {
        auto* Part = NewObject<UBoxComponent>(this, Def.Name);
        Part->SetMobility(EComponentMobility::Movable); Part->SetupAttachment(GetMesh());
        Part->SetRelativeLocation(Def.Center); Part->SetBoxExtent(Def.Extent);
        Part->SetCollisionProfileName(TEXT("BlockAll")); Part->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
        if (Def.bPassengerFloor) Part->ComponentTags.Add(TEXT("RVPassengerPlatform"));
        Part->SetNetAddressable(); Part->RegisterComponent(); GeneratedParts.Add(Part);
    }
}
void ARVInteriorMotorhome::BeginPlay()
{
    Super::BeginPlay();
    if (HasAuthority()) for (const auto& Def : Stations)
    {
        auto* Station = GetWorld()->SpawnActor<ARVInteriorStation>();
        if (!Station) continue;
        Station->StationName = Def.Name;
        Station->AttachToComponent(GetMesh(), FAttachmentTransformRules::SnapToTargetNotIncludingScale);
        Station->SetActorRelativeLocation(Def.Position); Station->ForceNetUpdate();
    }
}
void ARVInteriorMotorhome::ConfigureProjectChassisCollision(FVector Center, FVector Extent)
{
#if WITH_EDITOR
    auto* Asset = GetMesh()->GetPhysicsAsset();
    // Only an explicitly created project-side derivative is editable through this helper.
    if (!Asset || !Asset->GetPathName().StartsWith(TEXT("/Game/Vehicles/Gate3/")) || !GetMesh()->GetSkeletalMeshAsset()) return;
    Asset->Modify(); Asset->SkeletalBodySetups.Reset(); Asset->ConstraintSetup.Reset();
    auto* Body = NewObject<USkeletalBodySetup>(Asset);
    Body->BoneName = GetMesh()->GetSkeletalMeshAsset()->GetRefSkeleton().GetBoneName(0);
    Asset->SkeletalBodySetups.Add(Body);
    Body->AggGeom.EmptyElements(); FKBoxElem Box; Box.Center = Center; Box.X = Extent.X * 2; Box.Y = Extent.Y * 2; Box.Z = Extent.Z * 2;
    Body->AggGeom.BoxElems.Add(Box); Body->InvalidatePhysicsData(); Body->CreatePhysicsMeshes(); Asset->MarkPackageDirty();
    Asset->UpdateBodySetupIndexMap(); Asset->UpdateBoundsBodiesArray();
    Asset->RefreshPhysicsAssetChange();
#endif
}


