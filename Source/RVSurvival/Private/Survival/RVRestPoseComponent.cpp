#include "Survival/RVRestPoseComponent.h"
#include "Survival/RVRestPoint.h"
#include "Interaction/RVInteractionComponent.h"
#include "Player/RVSurvivorCharacter.h"
#include "Player/RVPassengerReferenceFrameComponent.h"
#include "Vehicles/RVInteriorMotorhome.h"
#include "Components/CapsuleComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Camera/CameraComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Engine/StaticMesh.h"
#include "Net/UnrealNetwork.h"
URVRestPoseComponent::URVRestPoseComponent() { SetIsReplicatedByDefault(true); }
void URVRestPoseComponent::BeginPlay()
{
    Super::BeginPlay();
    auto* C=Cast<ARVSurvivorCharacter>(GetOwner()); if (!C) return;
    auto MakePart=[this,C](const TCHAR* Name,const TCHAR* Asset,FVector Location,FVector Scale,FRotator Rotation)
    {
        auto* Part=NewObject<UStaticMeshComponent>(C,Name);
        Part->SetupAttachment(C->GetRootComponent()); Part->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,Asset));
        Part->SetRelativeLocation(Location); Part->SetRelativeScale3D(Scale); Part->SetRelativeRotation(Rotation);
        Part->SetCollisionEnabled(ECollisionEnabled::NoCollision); Part->SetHiddenInGame(true); Part->RegisterComponent(); return Part;
    };
    PrototypeBody=MakePart(TEXT("PrototypeLyingBody"),TEXT("/Engine/BasicShapes/Cylinder.Cylinder"),FVector::ZeroVector,FVector(.32,.32,1.4),FRotator(90,0,0));
    PrototypeHead=MakePart(TEXT("PrototypeLyingHead"),TEXT("/Engine/BasicShapes/Sphere.Sphere"),FVector(83,0,0),FVector(.28),FRotator::ZeroRotator);
    OnRep_RestPoint();
}
void URVRestPoseComponent::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{ Super::GetLifetimeReplicatedProps(OutLifetimeProps); DOREPLIFETIME(URVRestPoseComponent,RestPoint); }
bool URVRestPoseComponent::BeginPoseAuthority(ARVRestPoint* Point)
{
    auto* C=Cast<ARVSurvivorCharacter>(GetOwner());
    if (!C || !C->HasAuthority() || !Point || RestPoint) return false;
    FVector Wake; UPrimitiveComponent* Floor=nullptr;
    if (!Point->FindWakePosition(C,Wake,Floor) || !Point->ValidateLyingPosition(C)) return false;
    // The held interaction completes before the rest state takes ownership; no reentrant interaction cancellation.
    auto* M=C->GetCharacterMovement(); M->StopMovementImmediately(); M->DisableMovement();
    M->CurrentFloor.Clear(); C->SetBase(static_cast<FMovementBaseInterfaceData*>(nullptr));
    if (auto* Frame=C->FindComponentByClass<URVPassengerReferenceFrameComponent>()) Frame->TickComponent(0,LEVELTICK_All,nullptr);
    C->GetCapsuleComponent()->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    C->AttachToActor(Point,FAttachmentTransformRules::SnapToTargetNotIncludingScale);
    // Marker mesh scale is presentation only; bed offsets are physical centimetres.
    C->SetActorLocation(Point->GetActorLocation()+Point->GetActorQuat().RotateVector(Point->LyingOffset),false,nullptr,ETeleportType::TeleportPhysics);
    C->SetActorRotation(Point->GetActorQuat()*Point->LyingRotation.Quaternion());
    RestPoint=Point; OnRep_RestPoint(); C->ForceNetUpdate(); return true;
}
bool URVRestPoseComponent::EndPoseAuthority(bool ForceCleanup)
{
    auto* C=Cast<ARVSurvivorCharacter>(GetOwner()); if (!C || !C->HasAuthority() || !RestPoint) return true;
    FVector Position; UPrimitiveComponent* Floor=nullptr;
    if (!RestPoint->FindWakePosition(C,Position,Floor) && !ForceCleanup) return false;
    C->DetachFromActor(FDetachmentTransformRules::KeepWorldTransform);
    if (Floor) C->SetActorLocation(Position,false,nullptr,ETeleportType::TeleportPhysics);
    RestPoint=nullptr; OnRep_RestPoint();
    C->SetActorRotation(FRotator(0,C->GetActorRotation().Yaw,0));
    auto* M=C->GetCharacterMovement(); M->Velocity=FVector::ZeroVector; M->SetMovementMode(MOVE_Walking);
    if (Floor)
    {
        M->FindFloor(Position,M->CurrentFloor,false);
        auto Data=MovementBaseUtility::GetMovementBaseDataFromPhysicsOwner(Floor); C->SetBase(&Data);
        if (auto* Frame=C->FindComponentByClass<URVPassengerReferenceFrameComponent>()) Frame->TickComponent(0,LEVELTICK_All,nullptr);
        C->SetBase(&Data);
    }
    C->ForceNetUpdate(); return true;
}
void URVRestPoseComponent::OnRep_RestPoint()
{
    auto* C=Cast<ARVSurvivorCharacter>(GetOwner()); if (!C) return;
    auto* Camera=C->FindComponentByClass<UCameraComponent>();
    if (RestPoint && !bPresentationActive)
    {
        PreviousEyeHeight=C->BaseEyeHeight;
        if (Camera) PreviousCameraLocation=Camera->GetRelativeLocation();
        bPresentationActive=true;
        // Swap only presentation. Do not rotate the native network-smoothed mesh or duplicate its standing prototype.
        TArray<USceneComponent*> Children; C->GetMesh()->GetChildrenComponents(true,Children); Children.Add(C->GetMesh());
        PreviousVisualVisibility.Reset();
        for (auto* Child:Children) if (auto* Part=Cast<UPrimitiveComponent>(Child))
        { PreviousVisualVisibility.Emplace(TWeakObjectPtr<UPrimitiveComponent>(Part),bool(Part->bHiddenInGame)); Part->SetHiddenInGame(true); }
        C->BaseEyeHeight=35; if (Camera) Camera->SetRelativeLocation(FVector(0,0,35));
    }
    else if (!RestPoint && bPresentationActive)
    {
        for (auto& State:PreviousVisualVisibility) if (auto* Part=State.Key.Get()) Part->SetHiddenInGame(State.Value);
        PreviousVisualVisibility.Reset(); C->BaseEyeHeight=PreviousEyeHeight;
        if (Camera) Camera->SetRelativeLocation(PreviousCameraLocation); bPresentationActive=false;
    }
    C->GetCapsuleComponent()->SetCollisionEnabled(RestPoint?ECollisionEnabled::NoCollision:ECollisionEnabled::QueryAndPhysics);
    C->bUseControllerRotationYaw=!RestPoint && !C->SeatedVehicle;
    if (RestPoint) C->GetCharacterMovement()->DisableMovement();
    else if (!C->SeatedVehicle) C->GetCharacterMovement()->SetMovementMode(MOVE_Walking);
    if (PrototypeBody) PrototypeBody->SetHiddenInGame(!RestPoint);
    if (PrototypeHead) PrototypeHead->SetHiddenInGame(!RestPoint);
}
