#include "Vehicles/RVInteriorMotorhome.h"
#include "Vehicles/RVInteractiveDoor.h"
#include "Net/UnrealNetwork.h"
#include "Interaction/RVInteriorStation.h"
#include "Components/BoxComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "PhysicsEngine/PhysicsAsset.h"
#include "PhysicsEngine/SkeletalBodySetup.h"
#include "Engine/SkeletalMesh.h"
#include "Vehicles/RVInteriorAccessPoint.h"
#include "Vehicles/RVVehicleEntryPoint.h"
#include "Vehicles/RVVehicleSeatComponent.h"
#include "Inventory/RVWorldItem.h"
#include "Player/RVSurvivorCharacter.h"
#include "Player/RVPlayerController.h"
#include "Player/RVPassengerReferenceFrameComponent.h"
#include "Player/RVPlayerState.h"
#include "Survival/RVNeedsComponent.h"
#include "Components/CapsuleComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Engine/StaticMesh.h"
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
        if (bInteractiveHouseDoor && (Def.Name==TEXT("Art_RV_Van_Door_Back") || Def.Name==TEXT("Art_RV_Glass_Door_Back")))
        { Part->SetVisibility(!GetWorld()->IsGameWorld()); Part->SetRelativeRotation(FRotator::ZeroRotator); }
        Part->SetCollisionEnabled(ECollisionEnabled::NoCollision); Part->RegisterComponent(); GeneratedParts.Add(Part);
    }
    for (const auto& Def : InteriorCollision)
    {
        if (bInteractiveHouseDoor && Def.Name==TEXT("OpenHouseDoor")) continue;
        auto* Part = NewObject<UBoxComponent>(this, Def.Name);
        Part->SetMobility(EComponentMobility::Movable); Part->SetupAttachment(GetMesh());
        Part->SetRelativeLocation(Def.Center); Part->SetBoxExtent(Def.Extent);
        Part->SetCollisionProfileName(TEXT("BlockAll")); Part->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
        if (Def.bPassengerFloor) Part->ComponentTags.Add(TEXT("RVPassengerPlatform"));
        Part->SetNetAddressable(); Part->RegisterComponent(); GeneratedParts.Add(Part);
        if (Def.bVisiblePrototype)
        {
            auto* Tread = NewObject<UStaticMeshComponent>(this, FName(*(Def.Name.ToString()+TEXT("_VisibleStep"))));
            Tread->SetMobility(EComponentMobility::Movable); Tread->SetupAttachment(GetMesh());
            Tread->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Cube.Cube")));
            Tread->SetRelativeLocation(Def.Center); Tread->SetRelativeScale3D(Def.Extent/50.f);
            Tread->SetCollisionEnabled(ECollisionEnabled::NoCollision); Tread->RegisterComponent(); GeneratedParts.Add(Tread);
        }
    }
}
void ARVInteriorMotorhome::BeginPlay()
{
    Super::BeginPlay();
    if (bInteractiveHouseDoor) for (const FName Name : {FName(TEXT("Art_RV_Van_Door_Back")),FName(TEXT("Art_RV_Glass_Door_Back"))})
        if (auto* Part=FindVisualPart(Name)) Part->SetVisibility(false);
    if (HasAuthority() && bInteractiveHouseDoor)
    {
        const auto* Door=VisualParts.FindByPredicate([](const FRVVisualPart& P){return P.Name==TEXT("Art_RV_Van_Door_Back");});
        const auto* Glass=VisualParts.FindByPredicate([](const FRVVisualPart& P){return P.Name==TEXT("Art_RV_Glass_Door_Back");});
        if (Door && Door->Mesh)
        {
            HouseDoor=GetWorld()->SpawnActorDeferred<ARVInteractiveDoor>(ARVInteractiveDoor::StaticClass(),GetActorTransform(),this);
            if (HouseDoor)
            {
                HouseDoor->DoorMesh=Door->Mesh; HouseDoor->GlassMesh=Glass?Glass->Mesh:nullptr;
                if (Glass) HouseDoor->GlassOffset=Glass->Transform.GetLocation()-Door->Transform.GetLocation();
                HouseDoor->FinishSpawning(GetActorTransform());
                HouseDoor->AttachToComponent(GetMesh(),FAttachmentTransformRules::SnapToTargetNotIncludingScale);
                HouseDoor->SetActorRelativeLocation(Door->Transform.GetLocation()); HouseDoor->ForceNetUpdate();
            }
        }
    }
    if (HasAuthority()) for (const auto& Def : Stations)
    {
        auto* Station = GetWorld()->SpawnActor<ARVInteriorStation>();
        if (!Station) continue;
        Station->StationName = Def.Name; Station->RequiredPowerLoad=Def.RequiredPowerLoad;
        Station->AttachToComponent(GetMesh(), FAttachmentTransformRules::SnapToTargetNotIncludingScale);
        Station->SetActorRelativeLocation(Def.Position); Station->ForceNetUpdate();
    }
    if (!HasAuthority()) return;
    for (const auto& Def : ExteriorCompartments)
    {
        auto* Point=GetWorld()->SpawnActorDeferred<ARVExteriorStoragePoint>(ARVExteriorStoragePoint::StaticClass(),GetActorTransform(),this);
        if (!Point) continue;
        Point->DoorPartName=Def.DoorPartName;
        Point->Container->DisplayName=Def.DisplayName; Point->Container->MaxWeightKg=Def.MaxWeightKg;
        Point->Container->MaxVolumeLitres=Def.MaxVolumeLitres; Point->Container->AllowedTags=Def.AllowedTags;
        Point->ConfigureQueryExtent(Def.QueryExtent); Point->FinishSpawning(GetActorTransform());
        Point->AttachToComponent(GetMesh(),FAttachmentTransformRules::SnapToTargetNotIncludingScale);
        Point->SetActorRelativeLocation(Def.Position); Point->ForceNetUpdate();
    }
    if (bEnableStandingDoor) for (bool Enter : {true,false})
    {
        auto* Point=GetWorld()->SpawnActorDeferred<ARVInteriorAccessPoint>(ARVInteriorAccessPoint::StaticClass(),GetActorTransform(),this);
        Point->Vehicle=this; Point->bEnter=Enter; Point->FinishSpawning(GetActorTransform());
        Point->AttachToComponent(GetMesh(),FAttachmentTransformRules::SnapToTargetNotIncludingScale);
        Point->SetActorRelativeLocation(Enter?OutsideDoorLocation:InsideDoorLocation); Point->ForceNetUpdate();
    }
    if (bInteriorSeatAccess) for (auto* Seat : GetSeats())
    {
        auto* Point=GetWorld()->SpawnActorDeferred<ARVVehicleInteriorSeatPoint>(ARVVehicleInteriorSeatPoint::StaticClass(),GetActorTransform(),this);
        Point->Seat=Seat; Point->FinishSpawning(GetActorTransform());
        Point->AttachToComponent(GetMesh(),FAttachmentTransformRules::SnapToTargetNotIncludingScale);
        Point->SetActorRelativeLocation(FVector(150,Seat->bDriverSeat?-40:40,155));
        Point->ForceNetUpdate();
    }
}
UStaticMeshComponent* ARVInteriorMotorhome::FindVisualPart(FName Name) const
{
    for (const auto& Part : GeneratedParts) if (Part && Part->GetFName()==Name) return Cast<UStaticMeshComponent>(Part.Get());
    return nullptr;
}
bool ARVInteriorMotorhome::TryStandingDoor(ARVSurvivorCharacter* Character, bool Enter)
{
    if (HouseDoor && !HouseDoor->bOpen) return false;
    if (!HasAuthority() || !Character || !Character->GetController() || Character->SeatedVehicle
        || GetVelocity().Size()>MaxEntryExitSpeed) return false;
    if (const auto* PS=Character->GetPlayerState<ARVPlayerState>(); PS && PS->Needs->State.RestMode!=ERVRestMode::Awake) return false;
    const FVector Door=GetActorTransform().TransformPosition(Enter?OutsideDoorLocation:InsideDoorLocation);
    if (FVector::Distance(Character->GetActorLocation(),Door)>300.f) return false;
    FVector Target;
    if (Enter)
    {
        bool Clear=false;
        const float Radius=Character->GetCapsuleComponent()->GetScaledCapsuleRadius();
        const float Half=Character->GetCapsuleComponent()->GetScaledCapsuleHalfHeight();
        FCollisionQueryParams Params(SCENE_QUERY_STAT(RVCabinEntry),false,Character);
        // Include the RV/furniture and other players in clearance; do not push into occupied space.
        for (const FVector Offset : {FVector::ZeroVector,FVector(-10,0,0),FVector(10,0,0)})
        {
            Target=GetActorTransform().TransformPosition(StandingEntryLocation+Offset);
            if (!GetWorld()->OverlapBlockingTestByChannel(Target,FQuat::Identity,ECC_Pawn,FCollisionShape::MakeCapsule(Radius,Half),Params))
            { Clear=true; break; }
        }
        if (!Clear) return false;
    }
    else if (!FindSafeExitAtOffset(FVector(OutsideDoorLocation.X,240,0),Character,Target)) return false;
    Character->GetCharacterMovement()->StopMovementImmediately();
    Character->SetActorLocation(Target,false,nullptr,ETeleportType::TeleportPhysics);
    Character->GetCharacterMovement()->SetMovementMode(MOVE_Walking); Character->ForceNetUpdate(); return true;
}
void ARVInteriorMotorhome::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{ Super::GetLifetimeReplicatedProps(OutLifetimeProps); DOREPLIFETIME(ARVInteriorMotorhome,HouseDoor); }
bool ARVInteriorMotorhome::FindSafeInteriorPosition(ARVSurvivorCharacter* Character, FVector PreferredLocal, FVector& Position, UPrimitiveComponent*& Floor) const
{
    if (!Character) return false;
    const auto* Capsule=Character->GetCapsuleComponent();
    const auto* Frame=Character->FindComponentByClass<URVPassengerReferenceFrameComponent>();
    const float Radius=FMath::Min(Capsule->GetScaledCapsuleRadius(),Frame?Frame->InteriorCapsuleRadius:30.f);
    const float Half=Capsule->GetScaledCapsuleHalfHeight();
    FCollisionQueryParams Params(SCENE_QUERY_STAT(RVInteriorPlacement),false,Character);
    for (const FVector Offset : {FVector::ZeroVector,FVector(-40,0,0),FVector(40,0,0),FVector(-80,0,0),FVector(80,0,0)})
    {
        const FVector Aim=GetMesh()->GetComponentTransform().TransformPosition(PreferredLocal+Offset);
        FHitResult Hit;
        if (!GetWorld()->LineTraceSingleByChannel(Hit,Aim+FVector(0,0,30),Aim-FVector(0,0,180),ECC_Pawn,Params)
            || !Hit.GetComponent() || Hit.GetActor()!=this || !Hit.GetComponent()->ComponentHasTag(TEXT("RVPassengerPlatform"))
            || Hit.ImpactNormal.Z<.7f) continue;
        const FVector Candidate=Hit.ImpactPoint+FVector(0,0,Half+2);
        if (GetWorld()->OverlapBlockingTestByChannel(Candidate,FQuat::Identity,ECC_Pawn,FCollisionShape::MakeCapsule(Radius,Half),Params)) continue;
        Position=Candidate; Floor=Hit.GetComponent(); return true;
    }
    return false;
}
bool ARVInteriorMotorhome::TryMoveToLivingArea(ARVPlayerController* PC)
{
    if (!HasAuthority() || !PC || PC->SeatedVehicle!=this) return false;
    for (auto* Seat : GetSeats()) if (Seat->Occupant && Seat->OccupantController.Get()==PC)
    {
        // A moving driver must retain control; a passenger can safely join the rigid interior frame.
        if (Seat->bDriverSeat && GetVelocity().Size()>MaxEntryExitSpeed)
        { PC->SeatFeedback=TEXT("Stop before leaving the driver seat."); return false; }
        auto* Character=Seat->Occupant.Get(); FVector Position; UPrimitiveComponent* Floor=nullptr;
        if (!FindSafeInteriorPosition(Character,StandingEntryLocation,Position,Floor))
        { PC->SeatFeedback=TEXT("Living aisle is obstructed; seat retained."); return false; }
        ReleaseSeat(Seat,false,Position);
        auto* Movement=Character->GetCharacterMovement();
        Movement->FindFloor(Position,Movement->CurrentFloor,false);
        auto BaseData=MovementBaseUtility::GetMovementBaseDataFromPhysicsOwner(Floor);
        Character->SetBase(&BaseData);
        if (auto* Frame=Character->FindComponentByClass<URVPassengerReferenceFrameComponent>())
            Frame->TickComponent(0,LEVELTICK_All,nullptr);
        // SetBase after native root policy is enabled so the first based update uses the common root.
        Character->SetBase(&BaseData); Movement->Velocity=FVector::ZeroVector;
        PC->SeatFeedback=TEXT("Living area | Hold E at cab seat to sit");
        Character->ForceNetUpdate(); PC->ForceNetUpdate(); return true;
    }
    return false;
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


